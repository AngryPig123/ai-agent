from dataclasses import dataclass, field, replace
from typing import Any

from app.domain.model.blog_post import BlogPost


@dataclass(frozen=True)
class AgentState:
    user_question: str
    blog_posts: list[BlogPost] = None
    summary: str | None = None
    answer: str | None = None

    extras: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        return self.extras.get(key, default)

    def has(self, key: str) -> bool:
        if hasattr(self, key):
            return getattr(self, key) is not None
        return key in self.extras and self.extras[key] is not None

    def update(self, **kwargs) -> "AgentState":
        known_fields = {"user_question", "blog_posts", "summary", "answer", "extras"}

        direct_updates = {k: v for k, v in kwargs.items() if k in known_fields}
        extra_updates = {k: v for k, v in kwargs.items() if k not in known_fields}

        new_state = replace(self, **direct_updates)

        if extra_updates:
            merged_extras = dict(new_state.extras)
            merged_extras.update(extra_updates)
            new_state = replace(new_state, extras=merged_extras)

        return new_state

    def with_references(self, blog_posts: list[BlogPost]) -> "AgentState":
        return AgentState(
            user_question=self.user_question,
            blog_posts=blog_posts,
            summary=self.summary,
            answer=self.answer
        )

    def with_summary(self, summary: str) -> "AgentState":
        return AgentState(
            user_question=self.user_question,
            blog_posts=self.blog_posts,
            summary=summary,
            answer=self.answer
        )

    def with_answer(self, answer: str) -> "AgentState":
        return AgentState(
            user_question=self.user_question,
            blog_posts=self.blog_posts,
            summary=self.summary,
            answer=answer
        )
