from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories import recipe_tags as rt_repo
from app.repositories import recipes as recipes_repo
from app.repositories import tags as tags_repo
from app.repositories.utils import row_affected


async def list_items(connection, recipe_id: int | None = None) -> list[dict]:
    return await rt_repo.list_items(connection, recipe_id)


async def upsert_item(connection, *, user_id: int, recipe_id: int, tag_id: int) -> dict:
    recipe = await recipes_repo.get_by_id(connection, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    if recipe["author_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only author can change tags")

    tag = await tags_repo.get_by_id(connection, tag_id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    return await rt_repo.upsert_item(connection, recipe_id, tag_id)


async def delete_item(connection, *, user_id: int, item_id: int) -> None:
    item = await rt_repo.get_with_author(connection, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe tag not found")
    if item["author_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only author can change tags")

    result = await rt_repo.delete_item(connection, item_id)
    if not row_affected(result):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe tag not found")
