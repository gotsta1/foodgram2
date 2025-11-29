from __future__ import annotations

from pydantic import BaseModel

from .users import User


class SubscriptionsResponse(BaseModel):
    count: int
    subscriptions: list[User]


class FollowersResponse(BaseModel):
    count: int
    followers: list[User]
