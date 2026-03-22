import uuid
from typing import Any

from app.application.port.inbound.sync_blog_answer_usecase import UserAnswerUseCase
from app.application.registry.tool_registry import ToolRegistry
from app.application.router.tool.base_tool_router import BaseToolRouter
from app.application.tool.base_tool import ToolContext


class BlogAnswerService(UserAnswerUseCase):

    def __init__(
            self,
            tool_router: BaseToolRouter,
            tool_registry: ToolRegistry
    ):
        self.tool_router = tool_router
        self.tool_registry = tool_registry

    def execute(self, state: dict[str, Any]) -> str:

        context = ToolContext(
            agent_id="blog-answer-agent",
            session_id="blog-answer-session",
            user_id="anonymous",
            trace_id=str(uuid.uuid4())
        )

        executed_tools: set[str] = set()

        while True:
            tool_name = self.tool_router.next_tool(state=state, executed_tools=executed_tools)
            if tool_name is None:
                break

            tool = self.tool_registry.get(tool_name)

            result, state = tool.execute(state=state, context=context)
            if not result.success:
                raise RuntimeError(result.error)

            executed_tools.add(tool.name)

            if tool.is_terminal:
                break

        return state["answer"]
