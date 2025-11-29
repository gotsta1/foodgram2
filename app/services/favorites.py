from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories import favorites as favorites_repo
from app.repositories import recipes as recipes_repo
from app.repositories.utils import row_affected


async def list_favorites(connection, user_id: int, q: str | None, limit: int, offset: int) -> list[dict]:
    return await favorites_repo.list_favorites(connection, user_id, q=q, limit=limit, offset=offset)


async def add_favorite(connection, *, user_id: int, recipe_id: int) -> dict:
    recipe = await recipes_repo.get_by_id(connection, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    existing = await favorites_repo.get_user_favorite(connection, user_id, recipe_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Рецепт уже добавлен в избранное")
    return await favorites_repo.add_favorite(connection, user_id, recipe_id)


async def delete_favorite(connection, *, user_id: int, recipe_id: int) -> None:
    result = await favorites_repo.delete_favorite(connection, user_id, recipe_id)
    if not row_affected(result):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found")
