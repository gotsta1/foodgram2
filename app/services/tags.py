from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories import tags as tags_repo
from app.repositories.utils import row_affected


async def list_tags(connection, q: str | None, limit: int, offset: int) -> list[dict]:
    return await tags_repo.list_tags(connection, q=q, limit=limit, offset=offset)


async def create_tag(connection, name: str) -> dict:
    existing = await tags_repo.get_by_name(connection, name)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag with this name already exists")
    return await tags_repo.create_tag(connection, name)


async def update_tag(connection, tag_id: int, name: str) -> dict:
    tag = await tags_repo.get_by_id(connection, tag_id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    if name != tag["name"]:
        duplicate = await tags_repo.get_by_name(connection, name)
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag with this name already exists",
            )
    return await tags_repo.update_tag(connection, tag_id, name)


async def delete_tag(connection, tag_id: int) -> None:
    result = await tags_repo.delete_tag(connection, tag_id)
    if not row_affected(result):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")


async def get_tag_or_404(connection, tag_id: int) -> dict:
    tag = await tags_repo.get_by_id(connection, tag_id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag
