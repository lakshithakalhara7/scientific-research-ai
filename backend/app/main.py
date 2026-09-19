from fastapi import FastAPI

app = FastAPI(
    title="Scientific Research Agentic AI",
    description="Agentic AI system for scientific research",
    version="1.0.0"
)


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