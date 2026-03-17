from abc import ABC, abstractmethod


class EmbedPort(ABC):

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        pass
