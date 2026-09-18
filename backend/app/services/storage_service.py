"""Opt-in PDF operations for the manually created private Storage bucket."""

import re

from supabase import Client

from app.core.supabase_client import get_supabase_client


RESEARCH_PAPERS_BUCKET = "research-papers"
MAX_PDF_SIZE_BYTES = 25_000_000
_PDF_OBJECT_KEY = re.compile(
    r"(?:[A-Za-z0-9][A-Za-z0-9._-]*/)*[A-Za-z0-9][A-Za-z0-9._-]*\.pdf",
    re.IGNORECASE,
)


def _validate_storage_path(storage_path: str) -> None:
    if not isinstance(storage_path, str) or not _PDF_OBJECT_KEY.fullmatch(storage_path):
        raise ValueError(
            "Use a relative .pdf object key with letters, digits, dots, underscores "
            "or hyphens; each path segment must start with a letter or digit."
        )


class StorageService:
    """PDF bytes only; never generates public URLs or creates buckets."""

    def __init__(self, client: Client | None = None) -> None:
        self._client = client if client is not None else get_supabase_client()

    def upload_pdf(self, storage_path: str, content: bytes) -> str:
        """Upload a new object (for example '<document UUID>/paper.pdf').

        The header check is a basic type guard. Full PDF parsing belongs to the
        existing extraction service when a future ingestion flow is connected.
        """
        _validate_storage_path(storage_path)
        if not isinstance(content, bytes):
            raise TypeError("PDF content must be bytes.")
        if len(content) > MAX_PDF_SIZE_BYTES:
            raise ValueError("PDF exceeds the 25 MB upload limit.")
        if not content.startswith(b"%PDF-"):
            raise ValueError("Content must start with a PDF header.")
        self._client.storage.from_(RESEARCH_PAPERS_BUCKET).upload(
            path=storage_path,
            file=content,
            file_options={"content-type": "application/pdf", "upsert": "false"},
        )
        return storage_path

    def download_pdf(self, storage_path: str) -> bytes:
        _validate_storage_path(storage_path)
        return self._client.storage.from_(RESEARCH_PAPERS_BUCKET).download(storage_path)

    def delete_pdf(self, storage_path: str) -> None:
        """Delete only the explicitly named object; does not delete metadata."""
        _validate_storage_path(storage_path)
        self._client.storage.from_(RESEARCH_PAPERS_BUCKET).remove([storage_path])
