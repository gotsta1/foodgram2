from __future__ import annotations

from typing import Any, Dict, List

import asyncpg


async def list_favorites(conn: asyncpg.Connection, user_id: int, q: str | None, limit: int, offset: int) -> List[Dict[str, Any]]:
    params: list[Any] = [user_id]
    where = "f.user_id = $1"
    join = "JOIN recipes r ON r.id = f.recipe_id"
    if q:
        params.append(f"%{q.lower()}%")
        where += f" AND LOWER(r.name) LIKE ${len(params)}"

    params.extend([limit, offset])
    query = f"""
        SELECT f.id, f.user_id, f.recipe_id
        FROM favorites f
        {join}
        WHERE {where}
        ORDER BY f.id
        LIMIT ${len(params)-1} OFFSET ${len(params)}
    """
    records = await conn.fetch(query, *params)
    return [dict(r) for r in records]


async def add_favorite(conn: asyncpg.Connection, user_id: int, recipe_id: int) -> Dict[str, Any]:
    record = await conn.fetchrow(
        """
        INSERT INTO favorites (user_id, recipe_id)
        VALUES ($1, $2)
        RETURNING id, user_id, recipe_id
        """,
        user_id,
        recipe_id,
    )
    return dict(record)


async def get_user_favorite(conn: asyncpg.Connection, user_id: int, recipe_id: int) -> Optional[Dict[str, Any]]:
    record = await conn.fetchrow(
        "SELECT id, user_id, recipe_id FROM favorites WHERE user_id = $1 AND recipe_id = $2",
        user_id,
        recipe_id,
    )
    return dict(record) if record else None


async def delete_favorite(conn: asyncpg.Connection, user_id: int, recipe_id: int) -> str:
    return await conn.execute(
        "DELETE FROM favorites WHERE recipe_id = $1 AND user_id = $2",
        recipe_id,
        user_id,
    )
