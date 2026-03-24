from app.application.tool.agent_state import AgentState
from app.application.tool.base_tool import BaseTool
from app.application.tool.base_tool_router import BaseToolRouter
from app.application.tool.tool_registry import ToolRegistry


class RuleBasedToolRouter(BaseToolRouter):

    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry

    def next_tool(self, state: AgentState, executed_tools: set[str]) -> str | None:
        candidates = [
            tool
            for tool in self.tool_registry.list_tools()
            if tool.name not in executed_tools and tool.can_handle(state)
        ]

        if not candidates:
            return None

        for tool in candidates:
            if self._provides_missing_state(tool, state):
                return tool.name

        terminal_candidates = [tool for tool in candidates if tool.is_terminal]
        if terminal_candidates:
            return terminal_candidates[0].name

        return candidates[0].name

    @staticmethod
    def _provides_missing_state(tool: BaseTool, state: AgentState) -> bool:
        return any(not state.has(key) for key in tool.provides)
