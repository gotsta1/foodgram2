from __future__ import annotations

from typing import Any, Dict, List

import asyncpg


async def list_items(conn: asyncpg.Connection, recipe_id: int | None = None) -> List[Dict[str, Any]]:
    if recipe_id:
        records = await conn.fetch(
            """
            SELECT id, recipe_id, ingredient_id, amount
            FROM recipe_ingredients
            WHERE recipe_id = $1
            ORDER BY id
            """,
            recipe_id,
        )
    else:
        records = await conn.fetch("SELECT id, recipe_id, ingredient_id, amount FROM recipe_ingredients ORDER BY id")
    return [dict(r) for r in records]


async def upsert_item(conn: asyncpg.Connection, recipe_id: int, ingredient_id: int, amount: int) -> Dict[str, Any]:
    record = await conn.fetchrow(
        """
        INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount)
        VALUES ($1, $2, $3)
        ON CONFLICT (recipe_id, ingredient_id)
        DO UPDATE SET amount = EXCLUDED.amount
        RETURNING id, recipe_id, ingredient_id, amount
        """,
        recipe_id,
        ingredient_id,
        amount,
    )
    return dict(record)


async def get_with_author(conn: asyncpg.Connection, item_id: int) -> Dict[str, Any] | None:
    record = await conn.fetchrow(
        """
        SELECT ri.id, r.author_id
        FROM recipe_ingredients ri
        JOIN recipes r ON r.id = ri.recipe_id
        WHERE ri.id = $1
        """,
        item_id,
    )
    return dict(record) if record else None


async def delete_item(conn: asyncpg.Connection, item_id: int) -> str:
    return await conn.execute("DELETE FROM recipe_ingredients WHERE id = $1", item_id)


async def delete_all_for_recipe(conn: asyncpg.Connection, recipe_id: int) -> str:
    return await conn.execute("DELETE FROM recipe_ingredients WHERE recipe_id = $1", recipe_id)


async def count_recipes_for_ingredient(conn: asyncpg.Connection, ingredient_id: int) -> int:
    val = await conn.fetchval(
        "SELECT COUNT(DISTINCT recipe_id) FROM recipe_ingredients WHERE ingredient_id = $1",
        ingredient_id,
    )
    return int(val or 0)
