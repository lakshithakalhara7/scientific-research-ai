"""Multipart upload boundary; document processing belongs to its service."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.models.schemas import DocumentUploadResponse
from app.services.ingestion_service import IngestionError, IngestionService
from app.services.storage_service import MAX_PDF_SIZE_BYTES


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


def get_ingestion_service() -> IngestionService:
    """Construct lazily so validation and unrelated routes need no credentials."""
    return IngestionService()


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=DocumentUploadResponse,
)
def upload_document(
    service: Annotated[IngestionService, Depends(get_ingestion_service)],
    file: Annotated[UploadFile | None, File()] = None,
    category: Annotated[str | None, Form()] = None,
    title: Annotated[str | None, Form()] = None,
    doi: Annotated[str | None, Form()] = None,
    source_url: Annotated[str | None, Form()] = None,
) -> dict:
    """Ingest one PDF synchronously in FastAPI's worker thread pool."""
    if file is None:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    try:
        if file.size is not None and file.size > MAX_PDF_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="PDF exceeds the 25 MB upload limit.")
        # Multipart parsing may spool to disk; never read an unbounded file into RAM.
        content = file.file.read(MAX_PDF_SIZE_BYTES + 1)
        if len(content) > MAX_PDF_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="PDF exceeds the 25 MB upload limit.")
        return service.ingest_pdf(
            filename=file.filename,
            content_type=file.content_type,
            content=content,
            category=category,
            title=title,
            doi=doi,
            source_url=source_url,
        )
    except IngestionError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from None
    except HTTPException:
        raise
    except Exception:
        # SDK exceptions can embed credentials or request details. Never log them.
        logger.error("Unexpected document upload failure.")
        raise HTTPException(status_code=500, detail="Document ingestion failed.") from None
    finally:
        file.file.close()
