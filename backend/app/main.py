from fastapi import FastAPI

from app.api.documents import router as documents_router
from app.models.schemas import ResearchQuery
from app.services.nlp_service import preprocess_text
from app.agents.retrieval_agent import RetrievalAgent


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

    return retrieval_agent.run(
        request.query
    )
