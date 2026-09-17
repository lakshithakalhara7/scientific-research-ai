"""One BM25 snapshot from Supabase chunks, or the local corpus as fallback.

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
from .database_service import DatabaseService, DocumentChunkRecord, DocumentRecord
from .document_service import load_all_research_papers
from .indexing_service import build_inverted_index
from .nlp_service import preprocess_text


logger = logging.getLogger(__name__)
_lock = RLock()
_resources: tuple[dict, dict] | None = None


class RetrievalSourceError(RuntimeError):
    """Persistent chunks could not be read; excludes raw SDK request details."""


class DocumentRetrievalError(RuntimeError):
    """Safe document-scope failure that the API can map to an HTTP response."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message


def _adapt_document_chunks(
    document: DocumentRecord, records: list[DocumentChunkRecord]
) -> list[dict]:
    chunks: list[dict] = []
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
        chunks.extend(_adapt_document_chunks(document, records))
    return chunks


def _unique_chunks(chunks: list[dict]) -> list[dict]:
    """Keep the first occurrence of an identity without comparing evidence text."""
    seen: set[tuple] = set()
    unique: list[dict] = []
    for chunk in chunks:
        if "document_id" in chunk:
            identity = ("supabase", chunk["document_id"], chunk["chunk_id"])
        else:
            identity = (
                "local", chunk["filename"], chunk["page_number"], chunk["chunk_number"]
            )
        if identity not in seen:
            seen.add(identity)
            unique.append(chunk)
    return unique


def _usable_persistent_chunks(chunks: list[dict]) -> list[dict]:
    """Require evidence text and searchable tokens; reuse stored NLP when present."""
    usable: list[dict] = []
    for chunk in _unique_chunks(chunks):
        if not chunk["text"].strip():
            continue
        tokens = chunk.get("processed_tokens")
        if tokens is None:
            tokens = preprocess_text(chunk["text"])
        if tokens:
            usable.append({**chunk, "processed_tokens": tokens})
    return usable


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

    # NLP/build errors must surface, rather than masquerading as cloud outages.
    persistent = _usable_persistent_chunks(persistent)
    if pending_document_id is not None:
        pending_id = str(UUID(str(pending_document_id)))
        if not any(chunk["document_id"] == pending_id for chunk in persistent):
            raise RetrievalSourceError("No searchable chunks are available for the new document.")
    if persistent:
        return build_inverted_index(persistent)

    # A snapshot uses exactly one source. Never read local PDFs when cloud chunks
    # are usable, including during preparation of a newly ingested document.
    local = create_document_chunks(load_all_research_papers(), chunk_size=250, overlap=50)
    return build_inverted_index(_unique_chunks(local))


def get_retrieval_resources() -> tuple[dict, dict]:
    """Build once on first query, then reuse the same completed snapshot."""
    global _resources
    with _lock:
        if _resources is None:
            _resources = _build_resources(allow_local_fallback=True)
        return _resources


def get_document_retrieval_resources(document_id: UUID | str) -> tuple[dict, dict]:
    """Select a persistent document before scoring, without using local fallback.

    Check current metadata even for a cached document. Reuse its cached postings
    when present; otherwise read only this document into a request-local index.
    Neither path modifies the shared corpus snapshot or its publication lifecycle.
    """
    try:
        identifier = str(UUID(str(document_id)))
    except (ValueError, TypeError, AttributeError):
        raise DocumentRetrievalError(422, "document_id must be a valid UUID.") from None

    # Coordinate with ingestion's status callback and atomic index publication.
    with _lock:
        try:
            database = DatabaseService()
            document = database.get_document(identifier)
        except Exception:
            raise DocumentRetrievalError(503, "The persistent retrieval source is unavailable.") from None
        if document is None:
            raise DocumentRetrievalError(404, "The selected document does not exist.")
        if str(document.id) != identifier:
            raise DocumentRetrievalError(503, "The persistent retrieval source is unavailable.")
        if document.status != "indexed":
            raise DocumentRetrievalError(409, "The selected document is not indexed yet.")

        if _resources is not None:
            inverted_index, chunk_store = _resources
            selected = {
                chunk_id: chunk for chunk_id, chunk in chunk_store.items()
                if chunk.get("document_id") == identifier
            }
            if selected:
                # Both postings and corpus statistics must use the chosen scope.
                scoped_index = {}
                for term, postings in inverted_index.items():
                    scoped_postings = {
                        chunk_id: frequency for chunk_id, frequency in postings.items()
                        if chunk_id in selected
                    }
                    if scoped_postings:
                        scoped_index[term] = scoped_postings
                return scoped_index, selected

        try:
            records = database.get_document_chunks(identifier)
        except Exception:
            raise DocumentRetrievalError(503, "The persistent retrieval source is unavailable.") from None
        if any(str(record.document_id) != identifier for record in records):
            raise DocumentRetrievalError(503, "The persistent retrieval source is unavailable.")
        chunks = _usable_persistent_chunks(_adapt_document_chunks(document, records))
        if not chunks:
            raise DocumentRetrievalError(409, "The indexed document has no searchable chunks.")
        return build_inverted_index(chunks)


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
