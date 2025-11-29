from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories import subscriptions as subscriptions_repo
from app.repositories import users as users_repo
from app.repositories.utils import row_affected


async def list_items(connection, user_id: int, q: str | None, limit: int, offset: int) -> list[dict]:
    return await subscriptions_repo.list_subscriptions(connection, user_id, q=q, limit=limit, offset=offset)


async def list_followers(connection, user_id: int, q: str | None, limit: int, offset: int) -> list[dict]:
    return await subscriptions_repo.list_followers(connection, user_id, q=q, limit=limit, offset=offset)


async def upsert_item(connection, *, user_id: int, following_id: int) -> dict:
    if user_id == following_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot subscribe to yourself")

    target_user = await users_repo.get_by_id(connection, following_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found")

    existing = await subscriptions_repo.get_subscription(connection, user_id, following_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already subscribed")

    return await subscriptions_repo.upsert_item(connection, user_id, following_id)


async def delete_item(connection, *, user_id: int, following_id: int) -> None:
    existing = await subscriptions_repo.get_subscription(connection, user_id, following_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not subscribed to this user")

    result = await subscriptions_repo.delete_item(connection, user_id, following_id)
    if not row_affected(result):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
