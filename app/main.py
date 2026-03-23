from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.adapter.outbound.embed.ollama_embed_adapter import OllamaEmbedAdapter
from app.adapter.outbound.llm.ollama_llm_adapter import OllamaLLMAdapter
from app.application.orchestrator.tool_flow_orchestrator import ToolFlowOrchestrator
from app.application.registry.tool_registry import ToolRegistry
from app.application.router.tool.rule_based_tool_router import RuleBasedToolRouter
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

        state = {
            "user_question": "무엇을 학습하려는 블로그야?"
        }

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

        tool_registry = ToolRegistry()
        tool_registry.register(search_blog_tool)
        tool_registry.register(summarize_context_tool)
        tool_registry.register(answer_draft_tool)

        rule_based_tool_router = RuleBasedToolRouter(tool_registry=tool_registry)

        tool_flow_orchestrator = ToolFlowOrchestrator(
            tool_registry=tool_registry,
            tool_router=rule_based_tool_router
        )

        blog_answer_service = BlogAnswerService(
            tool_flow_orchestrator=tool_flow_orchestrator
        )

        answer = blog_answer_service.execute(state)
        print(answer)


if __name__ == "__main__":
    main()
