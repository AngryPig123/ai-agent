from abc import ABC
from typing import Any


class PromptBuilder(ABC):

    def build(self, question: str, references: list[Any]) -> str:
        pass
