from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.port.out.blog_post_chunk_query_port import BlogPostChunkQueryPort
from app.domain.model.blog_post_chunk import BlogPostChunk
from app.infrastructure.persistence.entity.blog_post_chunk_entity import BlogPostChunkEntity


class BlogPostChunkRepository(BlogPostChunkQueryPort):

    def __init__(self, db: Session):
        self.db = db

    def search_similar(self, query_vector: list[float], limit: int = 5) -> list[BlogPostChunk]:
        stmt = (
            select(BlogPostChunkEntity)
            .order_by(BlogPostChunkEntity.embedding.cosine_distance(query_vector))
            .limit(limit)
        )

        rows = self.db.scalars(stmt).all()

        return [
            BlogPostChunk(
                id=row.id,
                blog_post_id=row.blog_post_id,
                title=row.title,
                chunk_index=row.chunk_index,
            )
            for row in rows
        ]
