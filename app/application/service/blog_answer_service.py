import uuid

from app.application.port.inbound.sync_blog_answer_usecase import UserAnswerUseCase
from app.application.port.outbound.llm_port import LLMPort
from app.application.tool.answer_draft_tool import AnswerDraftTool
from app.application.tool.base_tool import ToolContext
from app.application.tool.search_blog_tool import SearchBlogTool
from app.application.tool.summarize_context_tool import SummarizeContextTool


class BlogAnswerService(UserAnswerUseCase):

    def __init__(
            self,
            llm: LLMPort,
            search_blog_tool: SearchBlogTool,
            answer_draft_tool: AnswerDraftTool,
            summarize_context_tool: SummarizeContextTool,
    ):
        self.llm = llm
        self.search_blog_tool = search_blog_tool
        self.answer_draft_tool = answer_draft_tool
        self.summarize_context_tool = summarize_context_tool

    def execute(self, text: str) -> str:
        context = ToolContext(
            agent_id="blog-answer-agent",
            session_id="blog-answer-session",
            user_id="anonymous",
            trace_id=str(uuid.uuid4())
        )

        search_blog_tool_result = self.search_blog_tool.execute(
            input_data={"query": text},
            context=context,
        )
        blog_posts = search_blog_tool_result.data.get("posts", [])

        summarize_context_tool_result = self.summarize_context_tool.execute(
            input_data={"query": blog_posts},
            context=context
        )
        summary = summarize_context_tool_result.data.get("summary")
        input_data = {
            "question": text,
            "references": blog_posts,
            "summary": summary
        }

        answer_draft_tool_result = self.answer_draft_tool.execute(
            input_data=input_data,
            context=context
        )

        return answer_draft_tool_result.data.get("answer")
