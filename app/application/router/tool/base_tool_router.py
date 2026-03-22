from abc import ABC, abstractmethod
from typing import Any


class BaseToolRouter(ABC):
    @abstractmethod
    def next_tool(self, state: dict[str, Any], executed_tools: set[str]) -> str | None:
        pass
