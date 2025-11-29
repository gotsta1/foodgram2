from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, status

from app.db import get_connection
from app.dependencies.auth import get_current_user
from app.schemas import FollowersResponse, Subscription, SubscriptionCreate, SubscriptionsResponse, User
from app.services.subscriptions import delete_item, list_followers, list_items, upsert_item

router = APIRouter(prefix="/subscriptions")


@router.get("", response_model=SubscriptionsResponse)
async def get_subscriptions(
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    subs = await list_items(connection, current_user["id"], q=q, limit=limit, offset=offset)
    users = [
        User(
            id=item["following_id"],
            email=item.get("email", ""),
            first_name=item.get("first_name", ""),
            last_name=item.get("last_name", ""),
            avatar=item.get("avatar"),
        )
        for item in subs
    ]
    return SubscriptionsResponse(count=len(users), subscriptions=users)


@router.post("", response_model=Subscription, status_code=status.HTTP_201_CREATED)
async def subscribe(
    payload: SubscriptionCreate,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    return await upsert_item(connection, user_id=current_user["id"], following_id=payload.following_id)


@router.delete("/{following_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe(
    following_id: int,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    await delete_item(connection, user_id=current_user["id"], following_id=following_id)
    return None

