from __future__ import annotations

from typing import Any, Dict, Optional

import asyncpg


async def list_ingredients(conn: asyncpg.Connection, q: str | None, limit: int, offset: int, sort: str | None = None) -> list[Dict[str, Any]]:
    order = "usage_count DESC, name" if sort == "popular" else "name"
    base_query = f"""
        SELECT i.id, i.name, i.measurement_unit,
               COALESCE(ri_count.count, 0) AS usage_count
        FROM ingredients i
        LEFT JOIN (
            SELECT ingredient_id, COUNT(*) AS count
            FROM recipe_ingredients
            GROUP BY ingredient_id
        ) ri_count ON ri_count.ingredient_id = i.id
    """
    where_clause = ""
    params: list[Any] = []
    if q:
        where_clause = "WHERE LOWER(i.name) LIKE $1"
        params.append(f"%{q.lower()}%")

    params.extend([limit, offset])
    query = f"""
        {base_query}
        {where_clause}
        ORDER BY {order}
        LIMIT ${len(params)-1} OFFSET ${len(params)}
    """
    records = await conn.fetch(query, *params)
    return [dict(r) for r in records]


async def get_by_id(conn: asyncpg.Connection, ingredient_id: int) -> Optional[Dict[str, Any]]:
    record = await conn.fetchrow("SELECT id, name, measurement_unit FROM ingredients WHERE id = $1", ingredient_id)
    return dict(record) if record else None


async def get_by_name(conn: asyncpg.Connection, name: str) -> Optional[Dict[str, Any]]:
    record = await conn.fetchrow("SELECT id, name, measurement_unit FROM ingredients WHERE name = $1", name)
    return dict(record) if record else None
