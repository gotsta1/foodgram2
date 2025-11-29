from __future__ import annotations

from typing import Any, Dict, List, Optional

import asyncpg


async def list_ratings(
    conn: asyncpg.Connection,
    recipe_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    params: list[Any] = []
    where = ""
    if recipe_id is not None:
        where = "WHERE recipe_id = $1"
        params.append(recipe_id)
    params.extend([limit, offset])
    query = f"""
        SELECT id, user_id, recipe_id, rate, created_at
        FROM ratings
        {where}
        ORDER BY created_at DESC
        LIMIT ${len(params)-1} OFFSET ${len(params)}
    """
    records = await conn.fetch(query, *params)
    return [dict(r) for r in records]


async def get_avg_rate(conn: asyncpg.Connection, recipe_id: int) -> float:
    record = await conn.fetchrow("SELECT AVG(rate) AS avg_rate FROM ratings WHERE recipe_id = $1", recipe_id)
    if record and record["avg_rate"] is not None:
        return float(record["avg_rate"])
    return 0.0


async def get_user_rating(conn: asyncpg.Connection, user_id: int, recipe_id: int) -> Optional[Dict[str, Any]]:
    record = await conn.fetchrow(
        "SELECT id, user_id, recipe_id, rate, created_at FROM ratings WHERE user_id = $1 AND recipe_id = $2",
        user_id,
        recipe_id,
    )
    return dict(record) if record else None


async def add_rating(conn: asyncpg.Connection, user_id: int, recipe_id: int, rate: int) -> Dict[str, Any]:
    record = await conn.fetchrow(
        """
        INSERT INTO ratings (user_id, recipe_id, rate)
        VALUES ($1, $2, $3)
        RETURNING id, user_id, recipe_id, rate, created_at
        """,
        user_id,
        recipe_id,
        rate,
    )
    return dict(record)
