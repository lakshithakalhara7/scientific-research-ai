"""One BM25 resource snapshot shared by local compatibility data and persisted chunks.

Refreshes are serialized within one backend process. Queries reuse the completed
snapshot. Run one worker for this prototype; other processes require a restart or
explicit refresh to see writes made elsewhere.
"""

from collections.abc import Callable
import logging
from threading import RLock
from uuid import UUID

from ..core.config import SupabaseConfigurationError
from .chunking_service import create_document_chunks
from .database_service import DatabaseService
from .document_service import load_all_research_papers
from .indexing_service import build_inverted_index


logger = logging.getLogger(__name__)
_lock = RLock()
_resources: tuple[dict, dict] | None = None


class RetrievalSourceError(RuntimeError):
    """Persistent chunks could not be read; excludes raw SDK request details."""


def _persistent_chunks(
    database: DatabaseService, pending_document_id: UUID | str | None = None
) -> list[dict]:
    documents = database.get_indexed_documents()
    pending_id = str(UUID(str(pending_document_id))) if pending_document_id else None
    if pending_id:
        pending = database.get_document(pending_id)
        if pending is None or pending.status != "processing":
            raise RetrievalSourceError("The document is not ready for index preparation.")
        documents = [document for document in documents if str(document.id) != pending_id]
        documents.append(pending)

    chunks: list[dict] = []
    for document in documents:
        # Defense in depth for fakes/adapters or concurrent ingestion changes.
        if document.status != "indexed" and str(document.id) != pending_id:
            continue
        records = database.get_document_chunks(document.id)
        if str(document.id) == pending_id and not records:
            raise RetrievalSourceError("No persisted chunks are available for the new document.")
        for record in records:
            chunk = {
                "chunk_id": str(record.id),
                "document_id": str(document.id),
                "filename": document.original_filename,
                "category": document.category or "uncategorized",
                "page_number": record.page_number,
                "chunk_number": record.chunk_number,
                "text": record.chunk_text,
            }
            if record.processed_text is not None:
                chunk["processed_tokens"] = record.processed_text.split()
            chunks.append(chunk)
    return chunks


def _build_resources(
    *, database: DatabaseService | None = None,
    pending_document_id: UUID | str | None = None,
    allow_local_fallback: bool = False,
) -> tuple[dict, dict]:
    try:
        persistent = _persistent_chunks(
            database if database is not None else DatabaseService(), pending_document_id
        )
    except Exception as error:
        if not allow_local_fallback:
            raise RetrievalSourceError("Supabase chunks are unavailable for index refresh.") from None
        if not isinstance(error, SupabaseConfigurationError):
            logger.warning("Supabase chunks unavailable; using the local corpus until refresh.")
        persistent = []

    # Temporary compatibility: one combined index, no automatic corpus upload.
    local = create_document_chunks(load_all_research_papers(), chunk_size=250, overlap=50)
    return build_inverted_index(local + persistent)


def get_retrieval_resources() -> tuple[dict, dict]:
    """Build once on first query, then reuse the same completed snapshot."""
    global _resources
    with _lock:
        if _resources is None:
            _resources = _build_resources(allow_local_fallback=True)
        return _resources


def refresh_retrieval_index(
    *, database: DatabaseService | None = None,
    pending_document_id: UUID | str | None = None,
    on_ready: Callable[[], None] | None = None,
) -> tuple[dict, dict]:
    """Build from persisted rows and publish only after the completion callback.

The ingestion callback marks the pending document indexed. If loading, indexing,
or that update fails, the old snapshot remains available and the candidate never
becomes visible. Pending documents require this callback to prevent premature use.
"""
    global _resources
    if pending_document_id is not None and on_ready is None:
        raise ValueError("A pending document requires an indexed-status callback.")
    with _lock:
        candidate = _build_resources(database=database, pending_document_id=pending_document_id)
        if on_ready is not None:
            on_ready()
        _resources = candidate
        return candidate


def clear_retrieval_cache() -> None:
    """Discard the snapshot; the next query reloads data (also useful in tests)."""
    global _resources
    with _lock:
        _resources = None
