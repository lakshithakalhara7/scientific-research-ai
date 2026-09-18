from app.services.llm_service import LLMService

llm = LLMService()

response = llm.generate_response(
    "Explain machine learning in simple words."
)

print(response)