from app.services.llm_service import LLMService


class AnalysisAgent:

    def __init__(self):
        self.llm = LLMService()

    def analyze(self, question, chunks):

        context = "\n\n".join(chunks)

        prompt = f"""
You are a Scientific Research Analysis Agent.

Research Question:
{question}

Research Context:
{context}

Instructions:

1. Summarize the research findings.
2. Extract key findings.
3. Identify methods/models used.
4. Only use the provided research context.
5. If information is missing from the context, clearly say so.
6. Avoid unsupported claims or assumptions.
7. Base the analysis strictly on the provided context.
8. Provide a clear, concise, and academic response.

Your response should be structured and easy to understand.
"""

        return self.llm.generate_response(prompt)