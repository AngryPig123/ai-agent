from typing import Any

from app.adapter.inbound.base_tool import BaseTool, ToolContext, ToolResult


class SearchBlogTool(BaseTool):
    name = "search_blog"
    description = "블로그 게시글 조회"

    def validate(self, input_data: dict[str, Any]) -> str | None:
        query = input_data.get("query")

        if query is None:
            return "query는 필수입니다."
        if not isinstance(query, str):
            return "query는 문자열이어야 합니다."
        if not query.strip():
            return "query는 비어 있을 수 없습니다."
        return None

    def run(self, input_data: dict[str, Any], context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={"answer": "테스트"}
        )
