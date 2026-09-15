from typing import Dict, Any

from app.services.nlp_service import preprocess_text
from app.services.retrieval_service import search_documents


class RetrievalAgent:
    """
    Retrieval Agent

    Responsibilities:
    1. Receive the user's research question
    2. Preprocess the query using NLP
    3. Search the indexed research corpus
    4. Rank relevant research paper chunks
    5. Return structured evidence for the next agent
    """

    def run(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:

        # ------------------------------------------
        # Validate query
        # ------------------------------------------

        if not query or not query.strip():
            return {
                "agent": "Retrieval Agent",
                "status": "error",
                "message": "Research query cannot be empty.",
                "results": []
            }

        clean_query = query.strip()

        # ------------------------------------------
        # NLP preprocessing
        # ------------------------------------------

        processed_query = preprocess_text(
            clean_query
        )

        if not processed_query:
            return {
                "agent": "Retrieval Agent",
                "status": "no_valid_terms",
                "original_query": clean_query,
                "processed_query": [],
                "results": []
            }

        # ------------------------------------------
        # Information Retrieval
        # ------------------------------------------

        results = search_documents(
            query=clean_query,
            top_k=top_k
        )

        # ------------------------------------------
        # Structured agent output
        # ------------------------------------------

        return {
            "agent": "Retrieval Agent",
            "status": "success",
            "original_query": clean_query,
            "processed_query": processed_query,
            "total_results": len(results),
            "results": results
        }