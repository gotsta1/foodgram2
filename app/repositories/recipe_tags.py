from __future__ import annotations

from typing import Any, Dict, List, Optional

import asyncpg


async def list_items(conn: asyncpg.Connection, recipe_id: Optional[int] = None) -> List[Dict[str, Any]]:
    if recipe_id:
        records = await conn.fetch(
            """
            SELECT id, recipe_id, tag_id, created_at
            FROM recipe_tag
            WHERE recipe_id = $1
            ORDER BY created_at DESC
            """,
            recipe_id,
        )
    else:
        records = await conn.fetch(
            "SELECT id, recipe_id, tag_id, created_at FROM recipe_tag ORDER BY created_at DESC"
        )
    return [dict(r) for r in records]


async def upsert_item(conn: asyncpg.Connection, recipe_id: int, tag_id: int) -> Dict[str, Any]:
    record = await conn.fetchrow(
        """
        INSERT INTO recipe_tag (recipe_id, tag_id)
        VALUES ($1, $2)
        ON CONFLICT (recipe_id, tag_id)
        DO UPDATE SET created_at = NOW()
        RETURNING id, recipe_id, tag_id, created_at
        """,
        recipe_id,
        tag_id,
    )
    return dict(record)


async def get_with_author(conn: asyncpg.Connection, item_id: int) -> Dict[str, Any] | None:
    record = await conn.fetchrow(
        """
        SELECT rt.id, r.author_id
        FROM recipe_tag rt
        JOIN recipes r ON r.id = rt.recipe_id
        WHERE rt.id = $1
        """,
        item_id,
    )
    return dict(record) if record else None


async def delete_item(conn: asyncpg.Connection, item_id: int) -> str:
    return await conn.execute("DELETE FROM recipe_tag WHERE id = $1", item_id)


async def delete_all_for_recipe(conn: asyncpg.Connection, recipe_id: int) -> str:
    return await conn.execute("DELETE FROM recipe_tag WHERE recipe_id = $1", recipe_id)
