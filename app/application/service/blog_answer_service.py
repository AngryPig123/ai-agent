from typing import Any

from app.application.orchestrator.tool_flow_orchestrator import ToolFlowOrchestrator
from app.application.port.inbound.sync_blog_answer_usecase import UserAnswerUseCase


class BlogAnswerService(UserAnswerUseCase):

    def __init__(
            self,
            tool_flow_orchestrator: ToolFlowOrchestrator
    ):
        self.tool_flow_orchestrator = tool_flow_orchestrator

    def execute(self, state: dict[str, Any]) -> str:
        agent_id = "blog-answer-agent"
        session_id = "blog-answer-session"
        user_id = "anonymous"

        state = self.tool_flow_orchestrator.run(
            initial_state=state,
            agent_id=agent_id,
            user_id=user_id,
            session_id=session_id
        )

        return state["answer"]
