from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from app.db import get_connection
from app.dependencies.auth import get_current_user
from app.schemas import Recipe, Subscription, User, UserRecipesResponse, UserStatsResponse, UserUpdate
from app.services.recipes import list_user_recipes
from app.services.users import get_current_user_profile, get_user_or_404, get_user_stats, list_users, update_current_user
from app.services.subscriptions import upsert_item as subscribe_user
from app.services.users import get_current_user_profile, get_user_or_404, get_user_stats, list_users, update_current_user

router = APIRouter(prefix="/users")


@router.get("", response_model=List[User])
async def get_users(
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    connection=Depends(get_connection),
):
    return await list_users(connection, q=q, limit=limit, offset=offset)


@router.get("/me", response_model=User)
async def get_me(current_user=Depends(get_current_user)):
    return await get_current_user_profile(current_user)


@router.patch("/me", response_model=User)
async def update_me(
    payload: UserUpdate,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    return await update_current_user(connection, current_user["id"], payload)


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int, connection=Depends(get_connection)):
    return await get_user_or_404(connection, user_id)


@router.get("/{user_id}/recipes", response_model=UserRecipesResponse)
async def get_user_recipes(
    user_id: int,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    connection=Depends(get_connection),
):
    user = await get_user_or_404(connection, user_id)
    recipes = await list_user_recipes(connection, user_id, q=q, limit=limit, offset=offset)
    return UserRecipesResponse(user=user, recipes=recipes)


@router.post("/{user_id}/subscribe", response_model=Subscription, status_code=201)
async def subscribe_user_endpoint(
    user_id: int,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    return await subscribe_user(connection, user_id=current_user["id"], following_id=user_id)


@router.get("/{user_id}/statistics", response_model=UserStatsResponse)
async def get_user_statistics(
    user_id: int,
    connection=Depends(get_connection),
):
    return await get_user_stats(connection, user_id)
