import requests

from app.application.port.outbound.embed_port import EmbedPort


class OllamaEmbedAdapter(EmbedPort):

    def __init__(self, model: str):
        self.model = model
        self.url = "http://localhost:11434/api/embed"

    def embed(self, text: str) -> list[float]:
        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "input": text
            },
            timeout=30,
        )

        if not response.ok:
            raise RuntimeError(
                f"Ollama embed request failed: {response.status_code} {response.text}"
            )

        data = response.json()

        embeddings = data.get("embeddings")
        if not embeddings or not isinstance(embeddings, list):
            raise ValueError(f"Invalid embedding response: {data}")

        return embeddings[0]
