from fastapi import FastAPI

from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse
)

from app.agents.analysis_agent import AnalysisAgent

app = FastAPI(
    title="Scientific Research AI"
)

analysis_agent = AnalysisAgent()


@app.get("/")
def home():
    return {
        "message": "Scientific Research AI Running"
    }


@app.post("/analyze",
          response_model=AnalysisResponse)
def analyze(request: AnalysisRequest):

    result = analysis_agent.analyze(
        request.question,
        request.chunks
    )

    return AnalysisResponse(
        analysis=result
    )