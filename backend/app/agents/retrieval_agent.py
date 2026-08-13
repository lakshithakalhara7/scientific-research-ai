from app.services.nlp_service import preprocess_text
from app.services.retrieval_service import search_documents


class RetrievalAgent:

    def run(self, query: str):

        processed_query = preprocess_text(query)

        results = search_documents(query)

        return {
            "agent": "Retrieval Agent",
            "original_query": query,
            "processed_query": processed_query,
            "results": results
        }