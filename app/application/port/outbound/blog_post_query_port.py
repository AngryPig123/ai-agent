from abc import ABC, abstractmethod

from app.domain.model.blog_post import BlogPost


class BlogPostQueryPort(ABC):

    @abstractmethod
    def find_by_blog_post_ids(self, blog_post_ids: list[int]) -> list[BlogPost]:
        raise NotImplementedError
