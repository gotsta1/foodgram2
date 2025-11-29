from __future__ import annotations

from fastapi import HTTPException

from app.repositories import ratings as ratings_repo
from app.repositories import recipes as recipes_repo


async def list_ratings(connection, recipe_id: int | None, limit: int, offset: int) -> list[dict]:
    return await ratings_repo.list_ratings(connection, recipe_id, limit=limit, offset=offset)


async def get_avg_rate(connection, recipe_id: int) -> float:
    return await ratings_repo.get_avg_rate(connection, recipe_id)


async def create_rating(connection, *, user_id: int, recipe_id: int, rate: int) -> dict:
    recipe = await recipes_repo.get_by_id(connection, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if not (1 <= rate <= 5):
        raise HTTPException(status_code=400, detail="Rate must be between 1 and 5")

    existing = await ratings_repo.get_user_rating(connection, user_id, recipe_id)
    if existing:
        raise HTTPException(status_code=400, detail="Rating already exists and cannot be changed")

    return await ratings_repo.add_rating(connection, user_id, recipe_id, rate)
