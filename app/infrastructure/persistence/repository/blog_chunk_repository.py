from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.model.blog_chunk import BlogPostChunk
from app.application.port.out.blog_chunk_query_port import BlogChunkQueryPort
from app.infrastructure.persistence.entity.blog_chunk_entity import BlogChunkEntity

class BlogChunkRepository(BlogChunkQueryPort):

    def __init__(self, db: Session):
        self.db = db

    def search_all(self) -> list[BlogPostChunk]:
        stmt = select(BlogChunkEntity)
        rows = self.db.scalars(stmt).all()
        return [
            BlogPostChunk(
                id=row.id,
                blog_post_id=row.blog_post_id,
                title=row.title,
                chunk_index=row.chunk_index
            )
            for row in rows
        ]


    def search_similar(self, query_vector: list[float], limit: int = 5) -> list[BlogPostChunk]:
        stmt = (
            select(BlogChunkEntity)
            .order_by(BlogChunkEntity.embedding.cosine_distance(query_vector))
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
