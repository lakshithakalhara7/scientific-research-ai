import json
from fastapi import FastAPI
from fastapi import HTTPException
from google.genai import errors

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


@app.post("/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest):
    try:
        result = analysis_agent.analyze(request.question, request.chunks)
    except errors.ClientError as e:
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded on the AI model. Please wait a bit and try again."
            )
        raise HTTPException(status_code=502, detail="AI model request failed.")
    except errors.ServerError:
        raise HTTPException(
            status_code=503,
            detail="The AI model is temporarily overloaded. Please try again shortly."
        )
    except (json.JSONDecodeError, KeyError):
        raise HTTPException(status_code=502, detail="Model returned an unexpected format.")
    return result