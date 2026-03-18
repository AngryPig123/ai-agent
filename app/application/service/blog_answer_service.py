import uuid
from app.adapter.inbound.base_tool import ToolContext, BaseTool
from app.adapter.inbound.search_blog_tool import SearchBlogTool
from app.application.port.inbound.sync_blog_answer_usecase import UserAnswerUseCase
from app.application.port.outbound.llm_port import LLMPort
from app.application.service.prompt.blog_answer_prompt_builder import SearchBlogPromptBuilder


class BlogAnswerService(UserAnswerUseCase):

    def __init__(
            self,
            base_tools: list[BaseTool],  # 리스트로 받게 해야됨
            llm: LLMPort,
    ):
        self.base_tools = base_tools
        self.llm = llm

    def execute(self, text: str) -> str:
        trace_id = str(uuid.uuid4())

        context = ToolContext(
            agent_id="blog-answer-agent",
            session_id="blog-answer-session",
            user_id="anonymous",
            trace_id=trace_id
        )

        blog_posts = []

        for tool in self.base_tools:

            if tool.name == "search_blog":
                tool_result = tool.execute(
                    input_data={"query": text},
                    context=context,
                )
                if not tool_result.success:
                    return f"블로그 게시글 조회 중 오류가 발생했습니다: {tool_result.error}"

                references = tool_result.data.get("posts", [])
                prompt = tool.prompt_builder.build(
                    question=text,
                    references=references,
                )
                blog_posts = tool_result.data

            if tool.name == "summarize_context":
                tool_result = tool.execute(
                    input_data={"query": blog_posts},
                    context=context,
                )
                if not tool_result.success:
                    return f"블로그 게시글 조회 중 오류가 발생했습니다: {tool_result.error}"

        return self.llm.generate(prompt)
