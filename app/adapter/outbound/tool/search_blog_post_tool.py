from typing import Any

from app.application.port.out.tool import BaseTool, ToolContext, ToolResult


class SearchBlogPostTool(BaseTool):

    def validate(self, input_data: dict[str, Any]) -> str | None:
        if "message" not in input_data:
            return "message는 필수입니다."
        return None

    def run(self, input_data: dict[str, Any], context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "echo": input_data["message"],
                "trace_id": context.trace_id
            }
        )
