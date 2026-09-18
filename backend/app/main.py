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
    VerificationRequest,
    ResearchWorkflowRequest
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

@app.post("/research")
def research_workflow(
    request: ResearchWorkflowRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Complete secured scientific research workflow:

    Security
        -> Retrieval Agent
        -> Analysis Agent
        -> Verification Agent
    """

    try:
        # ---------------------------------
        # 1. SECURITY
        # ---------------------------------

        security_result = security_service.prepare_safe_query(
            request.question
        )

        if not security_result["safe"]:
            raise HTTPException(
                status_code=400,
                detail=security_result["reason"]
            )

        safe_question = security_result["query"]


        # ---------------------------------
        # 2. MEMBER 01 - RETRIEVAL
        # ---------------------------------

        retrieval_output = retrieval_agent.run(
            safe_question,
            document_id=request.document_id,
            top_k=request.top_k
        )

        retrieval_results = retrieval_output.get(
            "results",
            []
        )

        if not retrieval_results:
            raise HTTPException(
                status_code=404,
                detail=(
                    "No relevant research evidence "
                    "was found for this question."
                )
            )


        # ---------------------------------
        # 3. PREPARE CHUNKS FOR MEMBER 02
        # ---------------------------------

        chunks = [
            result["text"]
            for result in retrieval_results
            if result.get("text")
        ]


        # ---------------------------------
        # 4. MEMBER 02 - ANALYSIS
        # ---------------------------------

        analysis_output = analysis_agent.analyze(
            safe_question,
            chunks
        )


        # ---------------------------------
        # 5. MEMBER 03 - VERIFICATION
        # ---------------------------------

        verification_output = (
            verification_agent.verify_analysis(
                analysis_output,
                retrieval_output
            )
        )


        # ---------------------------------
        # 6. USER-FACING SOURCE METADATA
        # ---------------------------------

        sources = []

        for result in retrieval_results:

            sources.append({
                "filename": result.get("filename"),
                "page_number": result.get("page_number"),
                "chunk_number": result.get("chunk_number"),
                "retrieval_score": result.get("score")
            })


        # ---------------------------------
        # 7. FINAL RESPONSE
        # ---------------------------------

        return {
            "success": True,

            "question": safe_question,

            "privacy_warning": security_result.get(
                "privacy_warning",
                False
            ),

            "analysis": analysis_output,

            "verification": verification_output,

            "sources": sources
        }


    except HTTPException:
        raise


    except DocumentRetrievalError as error:

        raise HTTPException(
            status_code=error.status_code,
            detail=error.message
        ) from None


    except errors.ClientError as error:

        error_text = str(error)

        if (
            "RESOURCE_EXHAUSTED" in error_text
            or "429" in error_text
        ):
            raise HTTPException(
                status_code=429,
                detail=(
                    "The AI service has reached its "
                    "current usage limit. Please try again later."
                )
            ) from None

        raise HTTPException(
            status_code=502,
            detail="The AI model request failed."
        ) from None


    except errors.ServerError:

        raise HTTPException(
            status_code=503,
            detail=(
                "The AI service is temporarily unavailable. "
                "Please try again later."
            )
        ) from None


    except Exception as error:

        safe_error = (
            security_service.create_safe_error_response(
                error
            )
        )

        raise HTTPException(
            status_code=500,
            detail=safe_error["message"]
        ) from None