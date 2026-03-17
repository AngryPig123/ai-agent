import requests

from app.application.port.out.llm_port import LLMPort


class OllamaLLMAdapter(LLMPort):

    def __init__(self, model: str):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt: str) -> str:
        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["response"]
