from app.application.port.out.blog_post_chunk_query_port import BlogPostChunkQueryPort
from app.application.port.out.blog_post_query_port import BlogPostQueryPort
from app.application.port.out.embed_port import EmbedPort
from app.application.port.out.llm_port import LLMPort
from app.application.port.out.sync_blog_answer_usecase import UserAnswerUseCase


class BlogAnswerService(UserAnswerUseCase):

    def __init__(
            self,
            blog_post_chunk_query_port: BlogPostChunkQueryPort,
            blog_post_query_port: BlogPostQueryPort,
            llm: LLMPort,
            embed: EmbedPort
    ):
        self.blog_post_chunk_query_port = blog_post_chunk_query_port
        self.blog_post_query_port = blog_post_query_port
        self.llm = llm
        self.embed = embed

    def execute(self, text):
        query_vector = self.embed.embed(text=text)
        blog_chunk_list = self.blog_post_chunk_query_port.search_similar(query_vector=query_vector, limit=3)

        blog_ids = []
        for blog_chunk in blog_chunk_list:
            blog_ids.append(blog_chunk.blog_post_id)

        blog_posts = self.blog_post_query_port.find_by_blog_post_ids(blog_ids)

        result = []
        for post in blog_posts:
            a = {
                "title": post.title,
                "description": post.description,
                "source_path": post.source_path,
                "tags_json": post.tags_json
            }
            result.append(a)

        prompt = f"""
                너는 블로그 글을 기반으로 질문에 답변하는 AI 도우미다.
        
                아래 제공된 블로그 글 정보를 참고해서 질문에 답변해라.
                제공된 내용에 없는 정보는 추측하지 말고 모른다고 답해라.
        
                [참고 블로그 데이터 목록]
                {result}
        
                [사용자 질문]
                {text}
        
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

        return self.llm.generate(prompt)
