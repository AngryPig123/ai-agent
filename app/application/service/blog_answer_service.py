import uuid
from typing import Any

from app.application.port.inbound.sync_blog_answer_usecase import UserAnswerUseCase
from app.application.tool.answer_draft_tool import AnswerDraftTool
from app.application.tool.base_tool import ToolContext
from app.application.tool.search_blog_tool import SearchBlogTool
from app.application.tool.summarize_context_tool import SummarizeContextTool


class BlogAnswerService(UserAnswerUseCase):

    def __init__(
            self,
            search_blog_tool: SearchBlogTool,
            answer_draft_tool: AnswerDraftTool,
            summarize_context_tool: SummarizeContextTool,
    ):
        self.search_blog_tool = search_blog_tool
        self.answer_draft_tool = answer_draft_tool
        self.summarize_context_tool = summarize_context_tool

    def execute(self, state:dict[str,Any]) -> str:

        context = ToolContext(
            agent_id="blog-answer-agent",
            session_id="blog-answer-session",
            user_id="anonymous",
            trace_id=str(uuid.uuid4())
        )

        self.search_blog_tool.execute(
            state=state,
            context=context,
        )

        self.summarize_context_tool.execute(
            state=state,
            context=context
        )

        self.answer_draft_tool.execute(
            state=state,
            context=context
        )

        return state["answer"]
