from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.port.outbound.blog_post_query_port import BlogPostQueryPort
from app.domain.model.blog_post import BlogPost
from app.infrastructure.persistence.entity.blog_post_entity import BlogPostEntity


class BlogPostRepository(BlogPostQueryPort):

    def __init__(self, db: Session):
        self.db = db

    def find_by_blog_post_ids(self, blog_post_ids: list[int]) -> list[BlogPost]:
        if not blog_post_ids:
            return []
        stmt = (
            select(BlogPostEntity)
            .where(BlogPostEntity.id.in_(blog_post_ids))
        )
        rows = self.db.scalars(stmt).all()
        return [
            BlogPost(
                id=row.id,
                title=row.title,
                description=row.description,
                source_path=row.source_path,
                content=row.content,
                tags_json=row.tags_json,
                updated=row.updated,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]
