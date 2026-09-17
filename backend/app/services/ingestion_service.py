"""Coordinate validated PDF persistence and publication to the existing BM25 index."""

from collections.abc import Callable
import logging
import re
import unicodedata
from typing import Any
from uuid import UUID, uuid4

from pydantic import HttpUrl, ValidationError

from app.services.chunking_service import create_document_chunks
from app.services.database_service import (
    DatabaseService,
    DocumentChunkCreate,
    DocumentCreate,
    DocumentRecord,
)
from app.services.document_service import (
    PDFValidationError,
    extract_text_from_pdf_bytes,
    inspect_pdf_bytes,
)
from app.services.nlp_service import preprocess_text
from app.services.storage_service import MAX_PDF_SIZE_BYTES, StorageService


logger = logging.getLogger(__name__)


class IngestionError(Exception):
    """An HTTP-compatible error whose message contains no SDK or input details."""

    def __init__(
        self, status_code: int, message: str, document_id: UUID | str | None = None
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.document_id = str(document_id) if document_id is not None else None


def _validate_filename(filename: str | None) -> tuple[str, str]:
    if not isinstance(filename, str) or not filename.strip():
        raise IngestionError(400, "A PDF filename is required.")
    if (
        len(filename) > 255
        or any(character in filename for character in ("/", "\\", ":", ".."))
        or any(unicodedata.category(character).startswith("C") for character in filename)
    ):
        raise IngestionError(400, "Use a plain PDF filename without paths or control characters.")
    filename = filename.strip()
    if not filename.lower().endswith(".pdf") or not filename[:-4].strip(". _-"):
        raise IngestionError(400, "The file must have a .pdf extension and a filename.")
    stem = unicodedata.normalize("NFKD", filename[:-4]).encode("ascii", "ignore").decode()
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._-") or "document"
    return filename, stem[:240] + ".pdf"


def _optional_metadata(value: str | None, field: str, max_length: int) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise IngestionError(400, f"Invalid {field} metadata.")
    value = value.strip()
    if not value:
        return None
    if len(value) > max_length or any(
        unicodedata.category(character).startswith("C") for character in value
    ):
        raise IngestionError(400, f"Invalid {field} metadata.")
    return value


def _cloud_error(error: Exception, document_id: UUID | None = None) -> IngestionError:
    # Inspect only fixed error codes. Never use SDK messages in responses or logs.
    code = str(getattr(error, "code", ""))
    status = str(getattr(error, "status", getattr(error, "status_code", "")))
    if code == "23505" or status == "409":
        return IngestionError(409, "The document operation conflicted with an existing record.", document_id)
    return IngestionError(503, "Document persistence is unavailable. Please try again later.", document_id)


class IngestionService:
    """Keep cloud access out of agents and reject invalid inputs before client setup.

    Failed rows/chunks stay marked failed and are excluded from retrieval. Only
    this attempt's successfully uploaded object is eligible for cleanup.
    """

    def __init__(
        self,
        database: DatabaseService | None = None,
        storage: StorageService | None = None,
        index_refresher: Callable[..., Any] | None = None,
    ) -> None:
        self._database = database
        self._storage = storage
        self._index_refresher = index_refresher

    def ingest_pdf(
        self,
        *,
        filename: str | None,
        content_type: str | None,
        content: bytes,
        category: str | None = None,
        title: str | None = None,
        doi: str | None = None,
        source_url: str | None = None,
    ) -> dict[str, Any]:
        original_filename, safe_filename = _validate_filename(filename)
        if not isinstance(content_type, str) or content_type.split(";", 1)[0].strip().lower() != "application/pdf":
            raise IngestionError(400, "The upload MIME type must be application/pdf.")
        if not isinstance(content, bytes) or not content:
            raise IngestionError(400, "A non-empty PDF file is required.")
        if len(content) > MAX_PDF_SIZE_BYTES:
            raise IngestionError(413, "The PDF exceeds the 25 MB upload limit.")
        if not content.startswith(b"%PDF-"):
            raise IngestionError(400, "The file must begin with a valid PDF header.")
        category = _optional_metadata(category, "category", 100)
        title = _optional_metadata(title, "title", 500)
        doi = _optional_metadata(doi, "doi", 255)
        source_url = _optional_metadata(source_url, "source_url", 2048)
        if source_url is not None:
            try:
                parsed_url = HttpUrl(source_url)
                if parsed_url.username or parsed_url.password:
                    raise ValueError
            except (ValidationError, ValueError):
                raise IngestionError(400, "source_url must be an HTTP or HTTPS URL without credentials.") from None
            source_url = str(parsed_url)
        try:
            page_count = inspect_pdf_bytes(content)
        except PDFValidationError as error:
            raise IngestionError(400, str(error)) from None

        # A PostgreSQL UUID primary key is allocated per attempt, never by filename.
        document_id = uuid4()
        storage_path = f"documents/{document_id}/{safe_filename}"
        metadata = DocumentCreate(
            original_filename=original_filename,
            storage_path=storage_path,
            category=category,
            title=title,
            doi=doi,
            source_url=source_url,
            file_size_bytes=len(content),
            page_count=page_count,
        )
        record: DocumentRecord | None = None
        indexed_record: DocumentRecord | None = None
        uploaded = False
        database = self._database
        storage = self._storage
        stage = "initialization"
        try:
            database = database if database is not None else DatabaseService()
            storage = storage if storage is not None else StorageService()
            stage = "create_document"
            created_record = database.create_document(metadata, document_id=document_id)
            if created_record.id != document_id or created_record.storage_path != storage_path:
                raise IngestionError(500, "Document persistence returned inconsistent metadata.", document_id)
            record = created_record
            stage = "upload"
            storage.upload_pdf(record.storage_path, content)
            uploaded = True
            stage = "processing_status"
            processing_record = database.update_document_status(record.id, "processing")
            if processing_record is None or processing_record.id != record.id or processing_record.status != "processing":
                raise IngestionError(503, "The document could not enter processing.", record.id)
            stage = "extraction"
            pages = extract_text_from_pdf_bytes(content)
            stage = "chunking"
            chunks = create_document_chunks([{
                "filename": original_filename,
                "category": category,
                "pages": pages,
            }])
            if not chunks:
                raise IngestionError(400, "The PDF contains no extractable text; OCR is not supported.", record.id)
            stage = "preprocessing"
            persisted_chunks = []
            searchable = False
            for chunk in chunks:
                # Normalize PostgreSQL-incompatible PDF NUL artifacts before NLP
                # so persisted evidence, processed tokens and token_count agree.
                chunk_text = chunk["text"].replace("\x00", "")
                tokens = preprocess_text(chunk_text)
                searchable = searchable or bool(tokens)
                persisted_chunks.append(DocumentChunkCreate(
                    page_number=chunk["page_number"],
                    chunk_number=chunk["chunk_number"],
                    chunk_text=chunk_text,
                    processed_text=" ".join(tokens),
                    token_count=len(tokens),
                ))
            if not searchable:
                raise IngestionError(400, "The PDF contains no searchable text after preprocessing.", record.id)
            stage = "insert_chunks"
            database.create_document_chunks(record.id, persisted_chunks)

            def mark_indexed() -> None:
                nonlocal indexed_record
                try:
                    indexed_record = database.update_document_status(record.id, "indexed")
                    if indexed_record is None or indexed_record.id != record.id or indexed_record.status != "indexed":
                        raise IngestionError(503, "The document could not be marked indexed.", record.id)
                except Exception as error:
                    # A timeout can follow a committed database update. Compensate
                    # before the refresh lock is released so another upload cannot
                    # index this failed attempt while outer cleanup is running.
                    try:
                        database.update_document_status(record.id, "failed")
                    except Exception:
                        logger.warning("PDF ingestion failure status unavailable: document_id=%s", document_id)
                    if isinstance(error, IngestionError):
                        raise error from None
                    raise _cloud_error(error, record.id) from None

            stage = "index_refresh"
            refresher = self._index_refresher
            if refresher is None:
                from app.services.retrieval_index_service import refresh_retrieval_index
                refresher = refresh_retrieval_index
            # The refresh builds first, runs this status callback, then atomically
            # publishes. A failed build/status update preserves the old snapshot.
            refresher(database=database, pending_document_id=record.id, on_ready=mark_indexed)
            if indexed_record is None:
                raise IngestionError(500, "The retrieval index did not publish the document.", record.id)
            return {"status": "success", "document": {
                "id": str(indexed_record.id),
                "title": indexed_record.title,
                "original_filename": indexed_record.original_filename,
                "category": indexed_record.category,
                "status": indexed_record.status,
                "page_count": indexed_record.page_count,
                "chunk_count": len(persisted_chunks),
            }}
        except Exception as error:
            # Fixed stage labels and our generated UUID are the only log fields.
            logger.warning("PDF ingestion failed: stage=%s document_id=%s", stage, document_id)
            if record is not None and database is not None:
                try:
                    database.update_document_status(record.id, "failed")
                except Exception:
                    logger.warning("PDF ingestion failure status unavailable: document_id=%s", document_id)
            if uploaded and record is not None and storage is not None:
                try:
                    storage.delete_pdf(record.storage_path)
                except Exception:
                    logger.warning("PDF ingestion object cleanup unavailable: document_id=%s", document_id)
            if isinstance(error, IngestionError):
                raise error from None
            if isinstance(error, PDFValidationError):
                raise IngestionError(400, "The file is not a readable PDF.", document_id) from None
            if stage in {"initialization", "create_document", "upload", "processing_status", "insert_chunks"}:
                raise _cloud_error(error, document_id) from None
            if stage == "index_refresh":
                from app.services.retrieval_index_service import RetrievalSourceError
                if isinstance(error, RetrievalSourceError):
                    raise IngestionError(503, "The retrieval data source is unavailable. Please try again later.", document_id) from None
            raise IngestionError(500, "PDF processing failed. Please try again later.", document_id) from None
