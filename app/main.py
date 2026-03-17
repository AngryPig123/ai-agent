from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.service.blog_answer_service import BlogAnswerService
from app.infrastructure.adapter.embed.ollama_embed_adapter import OllamaEmbedAdapter
from app.infrastructure.adapter.llm.ollama_llm_adapter import OllamaLLMAdapter
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

        usecase = BlogAnswerService(
            blog_post_chunk_query_port=blog_post_chunk_query_port,
            blog_post_query_port=blog_post_query_port,
            llm=llm,
            embed=embed,
        )

        answer = usecase.execute("헥사고날 아키텍처가 뭐야?")
        print(answer)


if __name__ == "__main__":
    main()
