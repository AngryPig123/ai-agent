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
    #   registry에서 식별할 고유 이름
    name: str = ""

    #   사람이 읽는 설명
    description = ""

    #   tool이 실행되기 위한 상태 키 목록
    requires: tuple[str, ...] = ()

    #   tool이 성공하면 state에 채워줄 키
    provides: tuple[str, ...] = ()

    #   tool 결과가 최종 산출물인지 여부
    is_terminal: bool = False

    def execute(self, state: dict[str, Any], context: ToolContext) -> tuple[ToolResult, dict[str, Any]]:
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

    def validate(self, input_data: dict[str, Any]) -> str | None:
        pass

    def run(self, input_data: dict[str, Any], context: ToolContext) -> ToolResult:
        pass

    #   현재 Tool이 실행 가능한 생태인지 판단
    def can_handle(self, state: dict[str, Any]) -> bool:
        return all(
            key in state and state[key] is not None
            for key in self.requires
        )

    #   공용 state에서 이 Tool이 실행에 필요한 입력만 추출
    def build_input(self, state: dict[str, Any]) -> dict[str, Any]:
        return {
            key: state[key]
            for key in self.requires
            if key in state
        }

    #   Tool 실행 결과를 공용 state에 반영
    def update_state(
            self,
            state: dict[str, Any],
            result: ToolResult
    ):
        new_state = dict(state)
        for key in self.provides:
            if key in result.data:
                new_state[key] = result.data[key]
        return new_state
