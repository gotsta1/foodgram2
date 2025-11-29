from __future__ import annotations

from typing import Any, Dict, List

import asyncpg


async def list_items(conn: asyncpg.Connection, user_id: int, q: str | None, limit: int, offset: int) -> List[Dict[str, Any]]:
    params: list[Any] = [user_id]
    where = "sl.user_id = $1"
    join = "JOIN recipes r ON r.id = sl.recipe_id"
    if q:
        params.append(f"%{q.lower()}%")
        where += f" AND LOWER(r.name) LIKE ${len(params)}"

    params.extend([limit, offset])
    query = f"""
        SELECT sl.id, sl.user_id, sl.recipe_id
        FROM shopping_list sl
        {join}
        WHERE {where}
        ORDER BY sl.id
        LIMIT ${len(params)-1} OFFSET ${len(params)}
    """
    records = await conn.fetch(query, *params)
    return [dict(r) for r in records]


async def add_item(conn: asyncpg.Connection, user_id: int, recipe_id: int) -> Dict[str, Any]:
    record = await conn.fetchrow(
        """
        INSERT INTO shopping_list (user_id, recipe_id)
        VALUES ($1, $2)
        RETURNING id, user_id, recipe_id
        """,
        user_id,
        recipe_id,
    )
    return dict(record)


async def get_item(conn: asyncpg.Connection, user_id: int, recipe_id: int) -> Optional[Dict[str, Any]]:
    record = await conn.fetchrow(
        "SELECT id, user_id, recipe_id FROM shopping_list WHERE user_id = $1 AND recipe_id = $2",
        user_id,
        recipe_id,
    )
    return dict(record) if record else None


async def delete_item(conn: asyncpg.Connection, user_id: int, recipe_id: int) -> str:
    return await conn.execute(
        "DELETE FROM shopping_list WHERE recipe_id = $1 AND user_id = $2",
        recipe_id,
        user_id,
    )
