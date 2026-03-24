from dataclasses import dataclass

from datetime import datetime


@dataclass
class BlogPost:
    id: int
    title: str
    description: str
    source_path: str
    content: str
    tags_json: str
    updated: datetime
    created_at: datetime
    updated_at: datetime
