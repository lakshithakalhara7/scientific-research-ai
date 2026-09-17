from pydantic import BaseModel
from typing import List


class AnalysisRequest(BaseModel):
    question: str
    chunks: List[str]


class AnalysisResponse(BaseModel):
    analysis: str