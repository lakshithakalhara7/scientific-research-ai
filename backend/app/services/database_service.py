"""Persistent metadata helpers, independent of the current local BM25 pipeline."""

from collections.abc import Sequence
from datetime import datetime
import logging
import re
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from postgrest.exceptions import APIError
from supabase import Client

from ..core.supabase_client import get_supabase_client


DocumentStatus = Literal["uploaded", "processing", "indexed", "failed"]
logger = logging.getLogger(__name__)


class DocumentCreate(BaseModel):
    """Metadata only: PDF bytes belong in the private Storage bucket."""

    model_config = ConfigDict(extra="forbid", frozen=True, revalidate_instances="always")

    original_filename: str = Field(min_length=1)
    storage_path: str = Field(min_length=1)
    title: str | None = None
    category: str | None = None
    doi: str | None = None
    source_url: str | None = None
    mime_type: Literal["application/pdf"] = "application/pdf"
    file_size_bytes: int | None = Field(default=None, ge=0)
    page_count: int | None = Field(default=None, ge=0)


class DocumentRecord(DocumentCreate):
    id: UUID
    status: DocumentStatus
    created_at: datetime


class DocumentChunkCreate(BaseModel):
    """One-based page and chunk positions match the existing local chunker."""

    model_config = ConfigDict(extra="forbid", frozen=True, revalidate_instances="always")

    page_number: int = Field(ge=1)
    chunk_number: int = Field(ge=1)
    chunk_text: str = Field(min_length=1)
    processed_text: str | None = None
    token_count: int | None = Field(default=None, ge=0)

    @field_validator("chunk_text", "processed_text", mode="before")
    @classmethod
    def remove_nul_characters(cls, value: object) -> object:
        # PDF extraction can emit U+0000. It is valid in JSON strings but cannot
        # be converted to PostgreSQL text. Preserve all other scientific Unicode.
        return value.replace("\x00", "") if isinstance(value, str) else value


class DocumentChunkRecord(DocumentChunkCreate):
    id: UUID
    document_id: UUID
    created_at: datetime


class DatabaseService:
    """Use only from trusted backend code; construction is explicit and opt-in."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client if client is not None else get_supabase_client()

    def create_document(
        self, document: DocumentCreate, *, document_id: UUID | None = None
    ) -> DocumentRecord:
        """Create metadata with the database's initial 'uploaded' status."""
        payload = DocumentCreate.model_validate(document).model_dump(mode="json")
        if document_id is not None:
            # Allocate the PostgreSQL primary key before constructing its object
            # path. The row returned by PostgreSQL remains the source of identity.
            payload["id"] = str(UUID(str(document_id)))
        response = self._client.table("documents").insert(payload).execute()
        if not response.data:
            raise RuntimeError("Supabase did not return the created document.")
        return DocumentRecord.model_validate(response.data[0])

    def get_document(self, document_id: UUID | str) -> DocumentRecord | None:
        response = (
            self._client.table("documents")
            .select("*")
            .eq("id", str(UUID(str(document_id))))
            .limit(1)
            .execute()
        )
        return DocumentRecord.model_validate(response.data[0]) if response.data else None

    def get_indexed_documents(self) -> list[DocumentRecord]:
        """Read completed documents only, including beyond the Data API row cap."""
        documents: list[DocumentRecord] = []
        offset = 0
        while True:
            response = (
                self._client.table("documents")
                .select("*")
                .eq("status", "indexed")
                .order("id")
                .range(offset, offset + 999)
                .execute()
            )
            if not response.data:
                return documents
            documents.extend(DocumentRecord.model_validate(row) for row in response.data)
            offset += len(response.data)

    def update_document_status(
        self, document_id: UUID | str, status: DocumentStatus
    ) -> DocumentRecord | None:
        """Update only status; return None if the document does not exist."""
        if status not in ("uploaded", "processing", "indexed", "failed"):
            raise ValueError("Invalid document status.")
        response = (
            self._client.table("documents")
            .update({"status": status})
            .eq("id", str(UUID(str(document_id))))
            .execute()
        )
        return DocumentRecord.model_validate(response.data[0]) if response.data else None

    def create_document_chunks(
        self,
        document_id: UUID | str,
        chunks: Sequence[DocumentChunkCreate],
    ) -> None:
        """Validate all chunks, then insert atomically without a truncated response."""
        identifier = str(UUID(str(document_id)))
        payloads = []
        positions: set[tuple[int, int]] = set()
        for item in chunks:
            chunk = DocumentChunkCreate.model_validate(item)
            position = (chunk.page_number, chunk.chunk_number)
            if position in positions:
                raise ValueError("Duplicate page_number/chunk_number in chunk batch.")
            positions.add(position)
            payloads.append({"document_id": identifier, **chunk.model_dump(mode="json")})
        if payloads:
            try:
                (
                    self._client.table("document_chunks")
                    .insert(payloads, returning="minimal")
                    .execute()
                )
            except APIError as error:
                # Code-only diagnostics with a fixed explanation: SDK messages,
                # details, hints and request headers can contain private data.
                code = error.code
                if not isinstance(code, str) or not re.fullmatch(r"(?:[A-Z0-9]{5}|PGRST[0-9]{3})", code):
                    code = "unknown"
                reason = (
                    "unsupported Unicode escape sequence"
                    if code == "22P05" else "database rejected chunk insert"
                )
                logger.warning(
                    "Chunk insert rejected: type=APIError code=%s reason=%s document_id=%s rows=%d",
                    code, reason, identifier, len(payloads),
                )
                raise

    def get_document_chunks(self, document_id: UUID | str) -> list[DocumentChunkRecord]:
        """Fetch all chunks in reading order, including beyond the server row cap.

        Read a stable document after its chunk insertion completes; separate HTTP
        pages do not share a database snapshot during concurrent writes.
        """
        identifier = str(UUID(str(document_id)))
        chunks: list[DocumentChunkRecord] = []
        offset = 0
        page_size = 1000
        while True:
            response = (
                self._client.table("document_chunks")
                .select("*")
                .eq("document_id", identifier)
                .order("page_number")
                .order("chunk_number")
                .range(offset, offset + page_size - 1)
                .execute()
            )
            rows = response.data
            if not rows:
                return chunks
            chunks.extend(DocumentChunkRecord.model_validate(row) for row in rows)
            # The project may impose a lower cap than our requested page size.
            offset += len(rows)
