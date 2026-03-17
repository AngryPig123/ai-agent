from abc import ABC
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolContext:
    agent_id: str
    session_id: str
    user_id: str
    trace_id: str


@dataclass
class ToolResult:
    success: bool
    data: Any = None
    error: str | None = None


class BaseTool(ABC):
    name: str = ""
    description = ""

    def execute(self, input_data: dict[str, Any], context: ToolContext) -> ToolResult:
        error = self.validate(input_data)
        if error:
            return ToolResult(success=False, error=error)
        try:
            return self.run(input_data=input_data, context=context)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def validate(self, input_data: dict[str, Any]) -> str | None:
        pass

    def run(self, input_data: dict[str, Any], context: ToolContext) -> ToolResult:
        pass
