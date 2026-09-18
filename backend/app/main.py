import json
import logging

from fastapi import FastAPI, HTTPException
from google.genai import errors

from app.api.documents import router as documents_router

from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ResearchQuery
)

from app.services.nlp_service import preprocess_text
from app.services.retrieval_index_service import DocumentRetrievalError

from app.agents.retrieval_agent import RetrievalAgent
from app.agents.analysis_agent import AnalysisAgent


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Scientific Research Agentic AI",
    description="Agentic AI system for scientific research",
    version="1.0.0"
)

app.include_router(documents_router)

retrieval_agent = RetrievalAgent()
analysis_agent = AnalysisAgent()


@app.get("/")
def root():
    return {
        "message": "Scientific Research AI Backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/test-nlp")
def test_nlp(query: str):

    processed_query = preprocess_text(query)

    return {
        "original_query": query,
        "processed_query": processed_query
    }


@app.post("/agents/retrieve")
def retrieve_research(request: ResearchQuery):

    try:
        return retrieval_agent.run(
            request.query,
            document_id=request.document_id
        )

    except DocumentRetrievalError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.message
        ) from None

    except Exception:
        logger.error("Unexpected research retrieval failure.")
        raise HTTPException(
            status_code=500,
            detail="Research retrieval failed."
        ) from None


@app.post("/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest):

    try:
        result = analysis_agent.analyze(
            request.question,
            request.chunks
        )

    except errors.ClientError as e:

        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded on the AI model. Please wait and try again."
            )

        raise HTTPException(
            status_code=502,
            detail="AI model request failed."
        )

    except errors.ServerError:

        raise HTTPException(
            status_code=503,
            detail="AI model is temporarily overloaded."
        )

    except (json.JSONDecodeError, KeyError):

        raise HTTPException(
            status_code=502,
            detail="Model returned unexpected output."
        )

    return result