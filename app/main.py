from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.adapter.inbound.search_blog_tool import SearchBlogTool
from app.adapter.inbound.summarize_context_tool import SummarizeContextTool
from app.application.service.blog_answer_service import BlogAnswerService
from app.adapter.outbound.embed.ollama_embed_adapter import OllamaEmbedAdapter
from app.adapter.outbound.llm.ollama_llm_adapter import OllamaLLMAdapter
from app.application.service.prompt.blog_answer_prompt_builder import SearchBlogPromptBuilder
from app.application.service.prompt.summarize_context_prompt_builder import SummarizeContextPromptBuilder
from app.infrastructure.persistence.repository.blog_post_chunk_repository import BlogPostChunkRepository
from app.infrastructure.persistence.repository.blog_post_repository import BlogPostRepository


def main() -> None:
    engine = create_engine("postgresql+psycopg://appuser:apppass@localhost:5433/appdb")
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as db:
        blog_post_chunk_query_port = BlogPostChunkRepository(db=db)
        blog_post_query_port = BlogPostRepository(db=db)
        llm = OllamaLLMAdapter("qwen2.5:7b")
        embed = OllamaEmbedAdapter("nomic-embed-text-v2-moe:latest")

        tools = []

        search_blog_prompt_builder = SearchBlogPromptBuilder()
        search_blog_tool = SearchBlogTool(
            prompt_builder=search_blog_prompt_builder,
            blog_post_chunk_query_port=blog_post_chunk_query_port,
            blog_post_query_port=blog_post_query_port,
            embed=embed,
        )

        summarize_context_prompt_builder = SummarizeContextPromptBuilder()
        summarize_context_tool = SummarizeContextTool(
            prompt_builder=summarize_context_prompt_builder,
            llm=llm
        )

        tools.append(search_blog_tool)
        tools.append(summarize_context_tool)

        blog_answer_service = BlogAnswerService(
            tools,
            llm=llm,
        )

        answer = blog_answer_service.execute("""
        """)
        print(answer)


if __name__ == "__main__":
    main()
