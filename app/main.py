from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.tool.search_blog_tool import SearchBlogTool
from app.application.service.blog_answer_service import BlogAnswerService
from app.adapter.outbound.embed.ollama_embed_adapter import OllamaEmbedAdapter
from app.adapter.outbound.llm.ollama_llm_adapter import OllamaLLMAdapter
from app.application.service.prompt.blog_answer_prompt_builder import BlogAnswerPromptBuilder
from app.infrastructure.persistence.repository.blog_post_chunk_repository import BlogPostChunkRepository
from app.infrastructure.persistence.repository.blog_post_repository import BlogPostRepository


def main() -> None:
    engine = create_engine("postgresql+psycopg://appuser:apppass@localhost:5432/appdb")
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as db:
        blog_post_chunk_query_port = BlogPostChunkRepository(db=db)
        blog_post_query_port = BlogPostRepository(db=db)
        llm = OllamaLLMAdapter("qwen2.5:7b")
        embed = OllamaEmbedAdapter("nomic-embed-text-v2-moe:latest")

        search_blog_tool = SearchBlogTool(
            blog_post_chunk_query_port=blog_post_chunk_query_port,
            blog_post_query_port=blog_post_query_port,
            embed=embed,
        )

        prompt_builder = BlogAnswerPromptBuilder()

        blog_answer_service = BlogAnswerService(
            search_blog_tool=search_blog_tool,
            llm=llm,
            prompt_builder=prompt_builder,
        )

        answer = blog_answer_service.execute("헥사고날 아키텍처가 뭐야?")
        print(answer)


if __name__ == "__main__":
    main()
