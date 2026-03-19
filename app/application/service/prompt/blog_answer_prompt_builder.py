from app.application.service.prompt.prompt_builder import PromptBuilder


class BlogAnswerPromptBuilder(PromptBuilder):
    def build(self, question: str, references: list[dict]) -> str:
        return f"""
                너는 블로그 글을 기반으로 질문에 답변하는 AI 도우미다.
                
                아래 제공된 블로그 글 정보를 참고해서 질문에 답변해라.
                제공된 내용에 없는 정보는 추측하지 말고 모른다고 답해라.
                
                [참고 블로그 데이터 목록]
                {references}
                
                [사용자 질문]
                {question}
                
                [답변 규칙]
                - 참고 데이터(result)에 (tags_json)와 유사한 블로그글도 첨부한다.
                - 먼저 질문에 대한 답변을 작성한다.
                - 답변은 한국어로 작성한다.
                - 마지막에 참고한 블로그 글 목록을 아래 형식으로 추가한다.
                
                [참고한 글]
                - 제목 (source_path)
                - 관련 태그 (tags_json)
                
                답변:
                """
