from abc import ABC, abstractmethod


class UserAnswerUseCase(ABC):

    @abstractmethod
    def execute(self, source_url) -> str:
        pass
