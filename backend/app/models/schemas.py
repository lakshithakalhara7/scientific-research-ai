from typing import List, Literal
from uuid import UUID

from pydantic import BaseModel, Field


# =========================
# Member 1 - Retrieval
# =========================

class ResearchQuery(BaseModel):
    query: str
    document_id: UUID | None = None


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


# =========================
# Member 2 - Analysis Agent
# =========================

class AnalysisRequest(BaseModel):
    question: str
    chunks: List[str]


class AnalysisResponse(BaseModel):
    summary: str
    key_findings: List[str]
    methods: List[str]
    conclusion: str