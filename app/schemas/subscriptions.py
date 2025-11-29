from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubscriptionCreate(BaseModel):
    following_id: int


class Subscription(BaseModel):
    id: int
    user_id: int
    following_id: int
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)
