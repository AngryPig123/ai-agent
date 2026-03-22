from abc import ABC, abstractmethod
from typing import Any


class UserAnswerUseCase(ABC):

    @abstractmethod
    def execute(self, state:dict[str,Any] ) -> str:
        pass
