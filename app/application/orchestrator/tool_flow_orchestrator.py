from typing import Any

from app.application.registry.tool_registry import ToolRegistry
from app.application.router.tool.base_tool_router import BaseToolRouter
from app.application.tool.base_tool import ToolContext


class ToolFlowOrchestrator:

    def __init__(
            self,
            tool_router: BaseToolRouter,
            tool_registry: ToolRegistry
    ):
        self.tool_router = tool_router
        self.tool_registry = tool_registry

    def run(
            self,
            initial_state: dict[str, Any],
            agent_id: str,
            user_id: str,
            session_id: str,
    ) -> dict[str, Any]:

        state = dict(initial_state)
        import uuid
        context = ToolContext(
            agent_id=agent_id,
            user_id=user_id,
            session_id=session_id,
            trace_id=str(uuid.uuid4()),
        )

        executed_tools: set[str] = set()

        while True:
            tool_name = self.tool_router.next_tool(
                state=state,
                executed_tools=executed_tools,
            )
            if tool_name is None:
                break

            tool = self.tool_registry.get(tool_name)

            result, state = tool.execute(state=state, context=context)
            if not result.success:
                raise RuntimeError(result.error)

            executed_tools.add(tool.name)

            if tool.is_terminal:
                break

        return state
