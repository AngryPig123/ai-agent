from typing import Any

from app.application.port.outbound.llm_port import LLMPort
from app.application.tool.base_tool import BaseTool, ToolContext, ToolResult


def prompt_builder(question: str, references: list[dict], summary: str) -> str:
    formatted_refs = "\n".join([
        f"""
        [글 {i + 1}]
        제목: {ref.get("title")}
        내용: {ref.get("content")[:500]}
        태그: {ref.get("tags_json")}
        경로: {ref.get("source_path")}
        """
        for i, ref in enumerate(references)
    ])

    return f"""
            너는 블로그 글을 기반으로 질문에 답변하는 AI 도우미다.

            아래 참고 자료와 요약 정보를 기반으로 사용자 질문에 답변하라.
            제공된 내용에 없는 정보는 절대 추측하지 말고 "모르겠습니다"라고 답하라.

            [참고 자료]
            {formatted_refs}

            [요약 정보]
            {summary}

            [사용자 질문]
            {question}

            [답변 규칙]
            - 질문에 대해 먼저 명확하게 설명한다.
            - 이해하기 쉽게 풀어서 설명한다.
            - 요약 정보를 참고하여 핵심 내용을 반영하되, 그대로 복사하지 않는다.
            - 답변은 한국어로 작성한다.

            [출력 형식]

            답변:
            (여기에 사용자 질문에 대한 답변)

            참고한 글:
            - 제목 (경로)
            - 관련 태그
            """


class AnswerDraftTool(BaseTool):

    def __init__(self, llm: LLMPort):
        self.llm = llm

    def validate(self, input_data: dict[str, Any]) -> str | None:
        posts = input_data.get("query")
        if posts is None:
            return "요약 본문은 필수입니다."
        return None

    def run(self, input_data: dict[str, Any], context: ToolContext) -> ToolResult:
        query = input_data.get("query")
        prompt = prompt_builder(query["question"], query["references"], query["summary"])
        answer = self.llm.generate(prompt)
        return ToolResult(success=True, data={"answer": answer})
