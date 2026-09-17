# analysis_agent.py
import json
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
5. If information is missing from the context, clearly say so in the conclusion.
6. Avoid unsupported claims or assumptions.

Respond ONLY with valid JSON, no markdown formatting, no code fences, matching exactly this shape:
{{
  "summary": "string",
  "key_findings": ["string", "string"],
  "methods": ["string", "string"],
  "conclusion": "string"
}}
"""
        raw = self.llm.generate_response(prompt)
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)