from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.application.tool.agent_state import AgentState


@dataclass(frozen=True)
class ToolContext:
    agent_id: str
    session_id: str
    user_id: str
    trace_id: str


@dataclass(frozen=True)
class ToolResult:
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None


class BaseTool(ABC):
    #   registry에서 식별할 고유 이름
    name: str = ""

    #   사람이 읽는 설명
    description: str = ""

    #   tool이 실행되기 위한 상태 키 목록
    requires: tuple[str, ...] = ()

    #   tool이 성공하면 state에 채워줄 키
    provides: tuple[str, ...] = ()

    #   tool 결과가 최종 산출물인지 여부
    is_terminal: bool = False

    def execute(self, state: AgentState, context: ToolContext) -> tuple[ToolResult, AgentState]:
        if not self.can_handle(state):
            return ToolResult(success=False, error="cannot handle"), state

        input_data = self.build_input(state)
        error = self.validate(input_data)

        if error:
            return ToolResult(success=False, error=error), state

        result = self.run(input_data, context)
        if not result.success:
            return result, state

        new_state = self.update_state(state, result)
        return result, new_state

    def can_handle(self, state: AgentState) -> bool:
        return all(state.has(key) for key in self.requires)

    def build_input(self, state: AgentState) -> dict[str, Any]:
        result ={
            key: state.get(key)
            for key in self.requires
        }
        return result

    def update_state(self, state: AgentState, result: ToolResult) -> AgentState:
        if not result.data:
            return state

        if not isinstance(result.data, dict):
            return state

        updates = {
            key: result.data[key]
            for key in self.provides
            if key in result.data
        }
        return state.update(**updates)

    @abstractmethod
    def validate(self, input_data: dict[str, Any]) -> str | None:
        return None

    @abstractmethod
    def run(self, input_data: dict[str, Any], context: ToolContext) -> ToolResult:
        raise NotImplementedError
