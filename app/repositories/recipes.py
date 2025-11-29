from __future__ import annotations

from typing import Any, Dict, List, Optional

import asyncpg


async def list_recipes(conn: asyncpg.Connection, q: str | None, limit: int, offset: int, sort: str | None = None) -> List[Dict[str, Any]]:
    order = "views DESC, pub_date DESC" if sort == "popular" else "pub_date DESC"
    base_query = f"""
        SELECT views, id, author_id, name, image, text, cooking_time, pub_date
        FROM recipes
    """
    params: List[Any] = []
    where_clause = ""
    if q:
        where_clause = "WHERE LOWER(name) LIKE $1 OR LOWER(text) LIKE $1"
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


async def list_user_recipes(conn: asyncpg.Connection, user_id: int, q: str | None, limit: int, offset: int) -> List[Dict[str, Any]]:
    params = [user_id]
    where = "r.author_id = $1"
    if q:
        params.append(f"%{q.lower()}%")
        where += f" AND (LOWER(r.name) LIKE ${len(params)} OR LOWER(r.text) LIKE ${len(params)})"

    params.extend([limit, offset])
    query = f"""
        SELECT r.id, r.author_id, r.name, r.image, r.text, r.cooking_time, r.pub_date,
               u.email, u.first_name, u.last_name, u.avatar
        FROM recipes r
        JOIN users u ON u.id = r.author_id
        WHERE {where}
        ORDER BY r.pub_date DESC
        LIMIT ${len(params)-1} OFFSET ${len(params)}
    """
    records = await conn.fetch(query, *params)
    return [dict(r) for r in records]


async def get_by_id(conn: asyncpg.Connection, recipe_id: int) -> Optional[Dict[str, Any]]:
    record = await conn.fetchrow(
        "SELECT id, author_id, name, image, text, cooking_time, pub_date, views FROM recipes WHERE id = $1",
        recipe_id,
    )
    return dict(record) if record else None


async def create_recipe(
    conn: asyncpg.Connection,
    *,
    author_id: int,
    name: str,
    image: str,
    text: str,
    cooking_time: int,
) -> Dict[str, Any]:
    record = await conn.fetchrow(
        """
        INSERT INTO recipes (author_id, name, image, text, cooking_time)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, author_id, name, image, text, cooking_time, pub_date
        """,
        author_id,
        name,
        image,
        text,
        cooking_time,
    )
    return dict(record)


async def update_recipe(
    conn: asyncpg.Connection,
    *,
    recipe_id: int,
    name: str,
    image: str,
    text: str,
    cooking_time: int,
) -> Dict[str, Any]:
    record = await conn.fetchrow(
        """
        UPDATE recipes
        SET name = $1, image = $2, text = $3, cooking_time = $4
        WHERE id = $5
        RETURNING id, author_id, name, image, text, cooking_time, pub_date
        """,
        name,
        image,
        text,
        cooking_time,
        recipe_id,
    )
    return dict(record)


async def increment_views(conn: asyncpg.Connection, recipe_id: int) -> None:
    await conn.execute("UPDATE recipes SET views = views + 1 WHERE id = $1", recipe_id)


async def delete_recipe(conn: asyncpg.Connection, recipe_id: int) -> str:
    return await conn.execute("DELETE FROM recipes WHERE id = $1", recipe_id)
