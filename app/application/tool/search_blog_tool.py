from typing import Any

from app.application.port.outbound.blog_post_chunk_query_port import BlogPostChunkQueryPort
from app.application.port.outbound.blog_post_query_port import BlogPostQueryPort
from app.application.port.outbound.embed_port import EmbedPort
from app.application.tool.base_tool import BaseTool, ToolContext, ToolResult


class SearchBlogTool(BaseTool):
    name = "search_blog"
    description = "블로그 게시글 조회"

    def __init__(
            self,
            blog_post_chunk_query_port: BlogPostChunkQueryPort,
            blog_post_query_port: BlogPostQueryPort,
            embed: EmbedPort,
    ):
        self.blog_post_chunk_query_port = blog_post_chunk_query_port
        self.blog_post_query_port = blog_post_query_port
        self.embed = embed

    def validate(self, input_data: dict[str, Any]) -> str | None:
        query = input_data.get("query")

        if query is None:
            return "query는 필수입니다."
        if not isinstance(query, str):
            return "query는 문자열이어야 합니다."
        if not query.strip():
            return "query는 비어 있을 수 없습니다."
        return None

    def run(self, input_data: dict[str, Any], context: ToolContext) -> ToolResult:
        query = input_data["query"].strip()
        query_vector = self.embed.embed(text=query)

        chunks = self.blog_post_chunk_query_port.search_similar(
            query_vector=query_vector,
            limit=3,
        )

        blog_ids = []
        for chunk in chunks:
            if chunk.blog_post_id not in blog_ids:
                blog_ids.append(chunk.blog_post_id)

        posts = self.blog_post_query_port.find_by_blog_post_ids(blog_ids)

        result = [
            {
                "title": post.title,
                "description": post.description,
                "source_path": post.source_path,
                "tags_json": post.tags_json,
                "content": post.content
            }
            for post in posts
        ]

        return ToolResult(success=True, data={"posts": result})
