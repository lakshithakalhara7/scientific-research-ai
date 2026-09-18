import json
import logging

from fastapi import FastAPI, HTTPException, Depends
from app.core.auth import get_current_user
from google.genai import errors

from app.api.documents import router as documents_router

from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ResearchQuery,
    VerificationRequest
)

from app.services.nlp_service import preprocess_text
from app.services.retrieval_index_service import DocumentRetrievalError

from app.agents.retrieval_agent import RetrievalAgent
from app.agents.analysis_agent import AnalysisAgent
from app.agents.verification_agent import VerificationAgent
from app.services.security_service import SecurityService


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Scientific Research Agentic AI",
    description="Agentic AI system for scientific research",
    version="1.0.0"
)

app.include_router(documents_router)

retrieval_agent = RetrievalAgent()
analysis_agent = AnalysisAgent()
verification_agent = VerificationAgent()
security_service = SecurityService()


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
def retrieve_research(
    request: ResearchQuery,
    current_user: dict = Depends(get_current_user)
):
    try:
        security_result = security_service.prepare_safe_query(
            request.query
        )

        if not security_result["safe"]:
            raise HTTPException(
                status_code=400,
                detail=security_result["reason"]
            )

        safe_query = security_result["query"]

        return retrieval_agent.run(
            safe_query,
            document_id=request.document_id
        )

    except HTTPException:
        raise

    except DocumentRetrievalError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.message
        ) from None

    except Exception as error:
        safe_error = (
            security_service.create_safe_error_response(error)
        )

        raise HTTPException(
            status_code=500,
            detail=safe_error["message"]
        ) from None

@app.post("/analyze", response_model=AnalysisResponse)
def analyze(
    request: AnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        security_result = security_service.prepare_safe_query(
            request.question
        )

        if not security_result["safe"]:
            raise HTTPException(
                status_code=400,
                detail=security_result["reason"]
            )

        safe_question = security_result["query"]

        result = analysis_agent.analyze(
            safe_question,
            request.chunks
        )

        return result

    except HTTPException:
        raise

    except errors.ClientError as error:
        if (
            "RESOURCE_EXHAUSTED" in str(error)
            or "429" in str(error)
        ):
            raise HTTPException(
                status_code=429,
                detail=(
                    "Rate limit exceeded on the AI model. "
                    "Please wait and try again."
                )
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

@app.post("/verify")
def verify_analysis(
    request: VerificationRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        analysis_output = request.analysis.model_dump()

        result = verification_agent.verify_analysis(
            analysis_output,
            request.retrieval_output
        )

        return result

    except Exception as error:
        safe_error = (
            security_service.create_safe_error_response(error)
        )

        raise HTTPException(
            status_code=500,
            detail=safe_error["message"]
        ) from None
    
@app.get("/protected-test")
def protected_test(
    current_user: dict = Depends(get_current_user)
):
    return {
        "message": "Authentication successful.",
        "user": current_user
    }    