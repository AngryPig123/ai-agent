from abc import ABC, abstractmethod

from app.domain.model.blog_post_chunk import BlogPostChunk


class BlogPostChunkQueryPort(ABC):

    @abstractmethod
    def search_similar(self, query_vector: list[float], limit: int = 5) -> list[BlogPostChunk]:
        raise NotImplementedError
