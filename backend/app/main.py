import logging

from fastapi import FastAPI, HTTPException

from app.api.documents import router as documents_router
from app.models.schemas import ResearchQuery
from app.services.nlp_service import preprocess_text
from app.services.retrieval_index_service import DocumentRetrievalError
from app.agents.retrieval_agent import RetrievalAgent


logger = logging.getLogger(__name__)


app = FastAPI(
    title="Scientific Research Agentic AI",
    description="Agentic AI system for scientific research",
    version="1.0.0"
)

app.include_router(documents_router)


retrieval_agent = RetrievalAgent()


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
        return retrieval_agent.run(request.query, document_id=request.document_id)
    except DocumentRetrievalError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from None
    except Exception:
        logger.error("Unexpected research retrieval failure.")
        raise HTTPException(status_code=500, detail="Research retrieval failed.") from None
