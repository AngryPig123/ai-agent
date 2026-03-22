from typing import Any

from app.application.port.outbound.llm_port import LLMPort
from app.application.tool.base_tool import BaseTool, ToolContext, ToolResult


def prompt_builder(contents: list[Any]) -> str:
    joined_contents = "\n\n".join(
        f"[문서 {idx + 1}]\n{str(content)}"
        for idx, content in enumerate(contents)
    )

    return f"""
            당신은 여러 문서를 읽고 핵심 내용을 정확하게 정리하는 요약 전문가이다.
        
            아래에 여러 개의 문서 내용이 주어진다.
            이 문서들은 이후 사용자의 질문에 답변하기 위한 참고 문맥으로 사용될 예정이다.
        
            작업 목표:
            0. 요약 대상이되는 본문에 포함된 HTML 요소는 태그가 포함한 시맨틱 요소에 맞게 이해한다.
            1. 전체 문서에서 핵심 주제와 공통 맥락을 파악한다.
            2. 중복되는 설명은 제거하고 중요한 내용만 압축한다.
            3. 사실, 개념, 규칙, 흐름, 주의사항 중심으로 정리한다.
            4. 추측하거나 없는 내용을 만들어내지 않는다.
            5. 문서에 없는 내용은 절대 추가하지 않는다.
            6. 최종 결과는 한국어로 작성한다.
        
            출력 규칙:
            - 불필요한 서론 없이 바로 요약 내용만 작성한다.
            - 핵심 개념
            - 중요 세부 사항
            - 주의할 점 또는 제약 사항
            이 드러나도록 정리한다.
            - 너무 짧지 않게, 그러나 중복 없이 압축적으로 작성한다.
            - 마크다운 리스트 형식으로 정리한다.
        
            문서 내용:
            {joined_contents}
            """.strip()


class SummarizeContextTool(BaseTool):

    name = "summarize_context"
    description = "블로그 게시글 조회"
    requires = ("blog_posts",)
    provides = ("summary",)

    def __init__(self, llm: LLMPort):
        self.llm = llm

    def build_input(self, state: dict[str, Any]) -> dict[str, Any]:
        return {
            "blog_posts": state["blog_posts"]
        }

    def validate(self, input_data: dict[str, Any]) -> str | None:
        blog_posts = input_data.get("blog_posts")
        if blog_posts is None:
            return "blog_posts은 필수입니다."
        if not isinstance(blog_posts, list):
            return "blog_posts은 리스트여야 합니다."
        if len(blog_posts) == 0:
            return "blog_posts은 비어 있을 수 없습니다."
        return None

    def run(self, input_data: dict[str, Any], context: ToolContext) -> ToolResult:
        blog_posts = input_data.get("blog_posts")
        prompt = prompt_builder([post['content'] for post in blog_posts])
        summary = self.llm.generate(prompt)
        return ToolResult(success=True, data={"summary": summary})
