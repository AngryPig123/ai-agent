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

        search_blog_tool_result, search_blog_tool_state = self.search_blog_tool.execute(
            state=state,
            context=context,
        )

        if not search_blog_tool_result.success:
            raise RuntimeError(search_blog_tool_result.error)

        summarize_context_tool_result,summarize_context_tool_state = self.summarize_context_tool.execute(
            state=search_blog_tool_state,
            context=context
        )

        if not summarize_context_tool_result.success:
            raise RuntimeError(summarize_context_tool_result.error)

        answer_draft_tool_result, answer_draft_tool_state = self.answer_draft_tool.execute(
            state=summarize_context_tool_state,
            context=context
        )

        if not answer_draft_tool_result.success:
            raise RuntimeError(answer_draft_tool_result.error)

        return answer_draft_tool_state["answer"]
