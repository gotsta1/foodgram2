from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories import users as users_repo
from app.repositories import favorites as favorites_repo
from app.repositories import comments as comments_repo
from app.repositories import subscriptions as subscriptions_repo
from app.schemas import UserUpdate
from app.services.files import process_image_input


def _sanitize(user: dict) -> dict:
    user.pop("password_hash", None)
    user.pop("username", None)
    return user


async def get_user_or_404(connection, user_id: int) -> dict:
    user = await users_repo.get_by_id(connection, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _sanitize(user)


async def list_users(connection, q: str | None, limit: int, offset: int) -> list[dict]:
    users = await users_repo.list_users(connection, q=q, limit=limit, offset=offset)
    return [_sanitize(u) for u in users]


async def get_current_user_profile(current_user: dict) -> dict:
    return _sanitize(dict(current_user))


async def update_current_user(connection, user_id: int, payload: UserUpdate) -> dict:
    if payload.email:
        existing = await users_repo.get_by_email(connection, payload.email)
        if existing and existing["id"] != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")

    if (
        payload.email is None
        and payload.first_name is None
        and payload.last_name is None
        and payload.avatar is None
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    email = payload.email if payload.email not in (None, "") else None
    first_name = payload.first_name if payload.first_name not in (None, "") else None
    last_name = payload.last_name if payload.last_name not in (None, "") else None
    avatar_input = payload.avatar
    delete_avatar = avatar_input == ""
    avatar_value = None
    if not delete_avatar and avatar_input not in (None, ""):
        avatar_value = process_image_input(avatar_input, subdir="avatars")
    if delete_avatar:
        avatar_value = "__DELETE__"
    updated = await users_repo.update_user(
        connection,
        user_id=user_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
        avatar=avatar_value,
    )
    return _sanitize(updated)


async def get_user_stats(connection, user_id: int) -> dict:
    user = await users_repo.get_by_id(connection, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    likes = await favorites_repo.count_for_author(connection, user_id)
    subscribers = await subscriptions_repo.count_followers(connection, user_id)
    comments = await comments_repo.count_for_author_recipes(connection, user_id)
    return {
        "likes": likes,
        "subscribers": subscribers,
        "comments": comments,
    }
