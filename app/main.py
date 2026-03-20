from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.adapter.outbound.embed.ollama_embed_adapter import OllamaEmbedAdapter
from app.adapter.outbound.llm.ollama_llm_adapter import OllamaLLMAdapter
from app.application.service.blog_answer_service import BlogAnswerService
from app.application.tool.answer_draft_tool import AnswerDraftTool
from app.application.tool.search_blog_tool import SearchBlogTool
from app.application.tool.summarize_context_tool import SummarizeContextTool
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

        summarize_context_tool = SummarizeContextTool(
            llm=llm
        )

        answer_draft_tool = AnswerDraftTool(
            llm=llm
        )

        blog_answer_service = BlogAnswerService(
            search_blog_tool=search_blog_tool,
            answer_draft_tool=answer_draft_tool,
            summarize_context_tool=summarize_context_tool,
        )

        answer = blog_answer_service.execute("헥사고날 아키텍처가 뭐야?")
        print(answer)


if __name__ == "__main__":
    main()
