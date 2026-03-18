from ipaddress import summarize_address_range
from typing import Any

from app.adapter.inbound.base_tool import BaseTool, ToolContext, ToolResult
from app.application.port.outbound.llm_port import LLMPort
from app.application.service.prompt.prompt_builder import PromptBuilder
from app.application.service.prompt.summarize_context_prompt_builder import SummarizeContextPromptBuilder
from app.domain.model.blog_post import BlogPost


class SummarizeContextTool(BaseTool):
    name = "summarize_context"
    description = "블로그 게시글 요약"

    def __init__(self, llm: LLMPort, prompt_builder: PromptBuilder):
        super().__init__(prompt_builder)
        self.llm = llm

    def validate(self, input_data: dict[str, list[BlogPost]]) -> str | None:
        blog_posts = input_data.get("query")
        if blog_posts is None:
            return "query는 필수입니다."
        if not isinstance(blog_posts, list):
            return "query는 문자열이어야 합니다."
        if not len(blog_posts) <= 0:
            return "query는 비어 있을 수 없습니다."
        return None

    def run(self, input_data: dict[str, list[BlogPost]], context: ToolContext) -> ToolResult:
        blog_posts = input_data.get("query")
        summarize_context_prompt_builder = SummarizeContextPromptBuilder()
        summarize = self.llm.generate(summarize_context_prompt_builder.build("", blog_posts))
        return ToolResult(success=True, data={"summarize": summarize})
