import uuid
from app.adapter.inbound.base_tool import ToolContext
from app.adapter.inbound.search_blog_tool import SearchBlogTool
from app.application.port.inbound.sync_blog_answer_usecase import UserAnswerUseCase
from app.application.port.outbound.llm_port import LLMPort
from app.application.service.prompt.blog_answer_prompt_builder import SearchBlogPromptBuilder


class BlogAnswerService(UserAnswerUseCase):

    def __init__(
            self,
            search_blog_tool: SearchBlogTool,
            llm: LLMPort,
            prompt_builder: SearchBlogPromptBuilder,
    ):
        self.search_blog_tool = search_blog_tool
        self.llm = llm
        self.prompt_builder = prompt_builder

    def execute(self, text: str) -> str:
        context = ToolContext(
            agent_id="blog-answer-agent",
            session_id="blog-answer-session",
            user_id="anonymous",
            trace_id=str(uuid.uuid4())
        )

        tool_result = self.search_blog_tool.execute(
            input_data={"query": text},
            context=context,
        )

        if not tool_result.success:
            return f"블로그 게시글 조회 중 오류가 발생했습니다: {tool_result.error}"

        references = tool_result.data.get("posts", [])

        prompt = self.prompt_builder.build(
            question=text,
            references=references,
        )

        return self.llm.generate(prompt)
