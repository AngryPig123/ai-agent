from typing import Any

from app.application.tool.base_tool import BaseTool, ToolContext, ToolResult
from app.application.port.outbound.llm_port import LLMPort


class SummarizeContextTool(BaseTool):
    name = "summarize_context"
    description = "블로그 게시글 조회"

    def __init__(self, llm: LLMPort):
        self.llm = llm

    def execute(self, input_data: dict[str, Any], context: ToolContext) -> ToolResult:
        pass

    def validate(self, input_data: dict[str, Any]) -> str | None:
        posts = input_data.get("query")
        if len(posts) == 0:
            return "요약 본문은 비어 있을 수 없습니다."
        if not posts is None:
            return "요약 본문은 필수 입니다."

        return None

    def run(self, input_data: dict[str, Any], context: ToolContext) -> ToolResult:

        pass
