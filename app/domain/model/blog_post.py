from dataclasses import dataclass

from sqlalchemy import DateTime


@dataclass
class BlogPost:
    id: int
    title: str
    description: str
    source_path: str
    content: str
    tags_json: str
    updated: DateTime
    created_at: DateTime
    updated_at: DateTime
