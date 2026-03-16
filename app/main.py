from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.persistence.repository.blog_chunk_repository import BlogChunkRepository

DATABASE_URL = "postgresql+psycopg://appuser:apppass@localhost:5432/appdb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

if __name__ == "__main__":
    with SessionLocal() as db:
        repo = BlogChunkRepository(db)
        chunks = repo.search_all()
        print(chunks)


