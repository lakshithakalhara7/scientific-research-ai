# llm_service.py
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

class LLMService:

    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

    def generate_response(self, prompt: str, max_retries: int = 3):
        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=prompt
                )
                return response.text
            except errors.ServerError as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait = 2 ** attempt  # 1s, 2s, 4s
                    time.sleep(wait)
                    continue
        raise last_error