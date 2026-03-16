from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import VECTOR

from app.infrastructure.db import Base

class BlogChunkEntity(Base):
    __tablename__ = "blog_post_chunk"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blog_post_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(VECTOR(768), nullable=False)