from abc import abstractmethod

from abc import ABC, abstractmethod
from app.domain.model.blog_chunk import BlogPostChunk

class BlogChunkQueryPort(ABC):

    @abstractmethod
    def search_similar(self, query_vector: list[float], limit: int = 5) -> list[BlogPostChunk]:
        raise NotImplementedError

    @abstractmethod
    def search_all(self) -> list[BlogPostChunk]:
        raise NotImplementedError

