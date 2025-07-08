
import os
import google.generativeai as genai

class LLMService:
    """Service for interacting with a Large Language Model."""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=self.api_key) # type: ignore
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17') # type: ignore

    def generate_response(self, prompt: str) -> str:
        """Generates a response from the LLM based on the prompt."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Handle potential API errors gracefully
            return f"Error generating response: {e}"
