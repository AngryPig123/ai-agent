from abc import ABC, abstractmethod
from typing import Any

from app.application.tool.agent_state import AgentState


class BaseToolRouter(ABC):
    @abstractmethod
    def next_tool(self, state: AgentState, executed_tools: set[str]) -> str | None:
        pass
