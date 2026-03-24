from abc import ABC, abstractmethod
from typing import Any

from app.application.tool.agent_state import AgentState


class UserAnswerUseCase(ABC):

    @abstractmethod
    def execute(self, state: AgentState) -> str:
        pass
