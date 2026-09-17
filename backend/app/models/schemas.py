from pydantic import BaseModel
from typing import List


class AnalysisRequest(BaseModel):
    question: str
    chunks: List[str]


class AnalysisResponse(BaseModel):
    summary: str
    key_findings: List[str]
    methods: List[str]
    conclusion: str