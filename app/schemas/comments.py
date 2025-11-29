from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator


class CommentCreate(BaseModel):
    text: Optional[str] = None
    image: Optional[str] = None

    @model_validator(mode="after")
    def ensure_any_content(self):  # type: ignore[override]
        if not self.text and not self.image:
            raise ValueError("either text or image must be provided")
        return self


class Comment(CommentCreate):
    id: int
    recipe_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
