from dataclasses import dataclass


@dataclass
class BlogPostChunk:
    id: int | None
    blog_post_id: int
    title: str
    chunk_index: int
    score: float | None = None