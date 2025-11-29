from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories import recipes as recipes_repo
from app.repositories import shopping_list as shopping_list_repo
from app.repositories.utils import row_affected


async def list_items(connection, user_id: int, q: str | None, limit: int, offset: int) -> list[dict]:
    return await shopping_list_repo.list_items(connection, user_id, q=q, limit=limit, offset=offset)


async def add_item(connection, *, user_id: int, recipe_id: int) -> dict:
    recipe = await recipes_repo.get_by_id(connection, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    existing = await shopping_list_repo.get_item(connection, user_id, recipe_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Рецепт уже добавлен в список покупок")
    return await shopping_list_repo.add_item(connection, user_id, recipe_id)


async def delete_item(connection, *, user_id: int, recipe_id: int) -> None:
    result = await shopping_list_repo.delete_item(connection, user_id, recipe_id)
    if not row_affected(result):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")


async def add_item_by_recipe(connection, *, user_id: int, recipe_id: int) -> dict:
    return await add_item(connection, user_id=user_id, recipe_id=recipe_id)


async def delete_item_by_recipe(connection, *, user_id: int, recipe_id: int) -> None:
    await delete_item(connection, user_id=user_id, recipe_id=recipe_id)
