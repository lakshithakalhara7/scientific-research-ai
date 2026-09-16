from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ResearchQuery(BaseModel):
    query: str


class UploadedDocument(BaseModel):
    """Public ingestion result; storage configuration stays on the server."""

    id: UUID
    title: str | None = None
    original_filename: str
    category: str | None = None
    status: Literal["indexed"]
    page_count: int = Field(ge=1)
    chunk_count: int = Field(ge=1)


class DocumentUploadResponse(BaseModel):
    status: Literal["success"]
    document: UploadedDocument
