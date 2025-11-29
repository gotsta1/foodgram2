from __future__ import annotations

from fastapi import HTTPException, status

from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password
from app.repositories import users as users_repo
from app.schemas import TokenResponse, UserCreate
from app.services.files import process_image_input


def _sanitize_user(user: dict) -> dict:
    user.pop("password_hash", None)
    user.pop("username", None)
    return user


async def register_user(connection, payload: UserCreate) -> TokenResponse:
    existing = await users_repo.get_by_email(connection, payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")

    try:
        password_hash = get_password_hash(payload.password)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc))
    avatar_url = process_image_input(payload.avatar, subdir="avatars") if payload.avatar else None
    record = await users_repo.create_user(
        connection,
        username=payload.email,
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        avatar=avatar_url,
        password_hash=password_hash,
    )
    user = _sanitize_user(record)
    access = create_access_token(user["id"])
    refresh = create_refresh_token(user["id"])
    return TokenResponse(access_token=access, refresh_token=refresh)


async def login_user(connection, email: str, password: str) -> TokenResponse:
    user_record = await users_repo.get_by_email(connection, email)
    if not user_record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    try:
        password_ok = verify_password(password, user_record["password_hash"])
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not password_ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user = _sanitize_user(user_record)
    access = create_access_token(user["id"])
    refresh = create_refresh_token(user["id"])
    return TokenResponse(access_token=access, refresh_token=refresh)
