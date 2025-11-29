from __future__ import annotations

from typing import Any, Dict, List, Optional

import asyncpg


async def list_comments(
    conn: asyncpg.Connection,
    recipe_id: Optional[int] = None,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    params: list[Any] = []
    conditions = []
    if recipe_id is not None:
        conditions.append("recipe_id = $1")
        params.append(recipe_id)
    if q:
        params.append(f"%{q.lower()}%")
        conditions.append(f"LOWER(text) LIKE ${len(params)}")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    params.extend([limit, offset])
    query = f"""
        SELECT id, user_id, recipe_id, text, image, created_at
        FROM comments
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ${len(params)-1} OFFSET ${len(params)}
    """
    records = await conn.fetch(query, *params)
    return [dict(r) for r in records]


async def create_comment(
    conn: asyncpg.Connection,
    *,
    user_id: int,
    recipe_id: int,
    text: Optional[str],
    image: Optional[str],
) -> Dict[str, Any]:
    record = await conn.fetchrow(
        """
        INSERT INTO comments (user_id, recipe_id, text, image)
        VALUES ($1, $2, $3, $4)
        RETURNING id, user_id, recipe_id, text, image, created_at
        """,
        user_id,
        recipe_id,
        text,
        image,
    )
    return dict(record)


async def get_by_id(conn: asyncpg.Connection, comment_id: int) -> Optional[Dict[str, Any]]:
    record = await conn.fetchrow(
        "SELECT id, user_id, recipe_id, text, image FROM comments WHERE id = $1",
        comment_id,
    )
    return dict(record) if record else None


async def delete_comment(conn: asyncpg.Connection, comment_id: int) -> str:
    return await conn.execute("DELETE FROM comments WHERE id = $1", comment_id)


async def update_comment(
    conn: asyncpg.Connection,
    *,
    comment_id: int,
    text: Optional[str],
    image: Optional[str],
) -> Dict[str, Any]:
    record = await conn.fetchrow(
        """
        UPDATE comments
        SET text = $1, image = $2
        WHERE id = $3
        RETURNING id, user_id, recipe_id, text, image, created_at
        """,
        text,
        image,
        comment_id,
    )
    return dict(record)
