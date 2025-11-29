from __future__ import annotations

from app.repositories import ingredients as ingredients_repo


async def list_ingredients(connection, q: str | None, limit: int, offset: int, sort: str | None = None) -> list[dict]:
    return await ingredients_repo.list_ingredients(connection, q=q, limit=limit, offset=offset, sort=sort)
