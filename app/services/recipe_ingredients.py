from __future__ import annotations

from fastapi import HTTPException

from app.repositories import ingredients as ingredients_repo
from app.repositories import recipe_ingredients as ri_repo
from app.repositories import recipes as recipes_repo
from app.repositories.utils import row_affected


async def list_items(connection, recipe_id: int | None = None) -> list[dict]:
    return await ri_repo.list_items(connection, recipe_id)


async def upsert_item(connection, *, user_id: int, recipe_id: int, ingredient_id: int, amount: int) -> dict:
    recipe = await recipes_repo.get_by_id(connection, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    if recipe["author_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only author can change ingredients")

    ingredient = await ingredients_repo.get_by_id(connection, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")

    return await ri_repo.upsert_item(connection, recipe_id, ingredient_id, amount)


async def delete_item(connection, *, user_id: int, item_id: int) -> None:
    item = await ri_repo.get_with_author(connection, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe ingredient not found")
    if item["author_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only author can change ingredients")

    result = await ri_repo.delete_item(connection, item_id)
    if not row_affected(result):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe ingredient not found")
