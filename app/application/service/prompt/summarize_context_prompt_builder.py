from app.application.service.prompt.prompt_builder import PromptBuilder
from app.domain.model.blog_post import BlogPost


class SummarizeContextPromptBuilder(PromptBuilder):

    def build(self, question, references: list[BlogPost]) -> str:
        return f"""
               너는 첨부된 데이터를 보고 내용을 요약하는 AI야
               
               제공된 데이터에 포함된 리스트 요소에 각각의 content를 분석 및 요약을해야된다.
               요소안의 content는 html 형태의 문자열로 되어있으며 고려해서 요약해야된다.
               각 요소의 요약을 끝냈으면 전체 내용을 취합해서 전체 요약을 해야된다.
               제공된 내용에 없는 정보는 추측하지 말고 모른다고 답해라.

               [데이터 목록]
               {references}

               [답변 규칙]
               - 포함된 데이터
               - 먼저 질문에 대한 답변을 작성한다.
               - 답변은 한국어로 작성한다.
               - 마지막에 참고한 블로그 글 목록을 아래 형식으로 추가한다.

               [참고 링크 전체 요약]
               답변:
               """
