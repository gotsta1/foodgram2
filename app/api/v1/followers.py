from __future__ import annotations

from fastapi import APIRouter, Depends

from app.db import get_connection
from app.dependencies.auth import get_current_user
from app.schemas import FollowersResponse, User
from app.services.subscriptions import list_followers

router = APIRouter(prefix="/followers")


@router.get("", response_model=FollowersResponse)
async def get_followers(
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    followers = await list_followers(connection, current_user["id"], q=q, limit=limit, offset=offset)
    users = [
        User(
            id=item["user_id"],
            email=item.get("email", ""),
            first_name=item.get("first_name", ""),
            last_name=item.get("last_name", ""),
            avatar=item.get("avatar"),
        )
        for item in followers
    ]
    return FollowersResponse(count=len(users), followers=users)
