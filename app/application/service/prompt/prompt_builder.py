from abc import ABC

class PromptBuilder(ABC):

    def build(self, question: str, references: list[dict]) -> str:
        pass
