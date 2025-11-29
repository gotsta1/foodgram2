from __future__ import annotations

from typing import Any, Dict, Optional

import asyncpg


async def list_tags(conn: asyncpg.Connection, q: str | None, limit: int, offset: int) -> list[Dict[str, Any]]:
    base = "SELECT id, name FROM tags"
    where = ""
    params: list[Any] = []
    if q:
        where = "WHERE LOWER(name) LIKE $1"
        params.append(f"%{q.lower()}%")

    params.extend([limit, offset])
    query = f"{base} {where} ORDER BY name LIMIT ${len(params)-1} OFFSET ${len(params)}"
    records = await conn.fetch(query, *params)
    return [dict(r) for r in records]


async def get_by_id(conn: asyncpg.Connection, tag_id: int) -> Optional[Dict[str, Any]]:
    record = await conn.fetchrow("SELECT id, name FROM tags WHERE id = $1", tag_id)
    return dict(record) if record else None


async def get_by_name(conn: asyncpg.Connection, name: str) -> Optional[Dict[str, Any]]:
    record = await conn.fetchrow("SELECT id, name FROM tags WHERE LOWER(name) = LOWER($1)", name)
    return dict(record) if record else None


async def create_tag(conn: asyncpg.Connection, name: str) -> Dict[str, Any]:
    normalized = name.lower()
    record = await conn.fetchrow("INSERT INTO tags (name) VALUES ($1) RETURNING id, name", normalized)
    return dict(record)


async def update_tag(conn: asyncpg.Connection, tag_id: int, name: str) -> Dict[str, Any]:
    normalized = name.lower()
    record = await conn.fetchrow(
        "UPDATE tags SET name = $1 WHERE id = $2 RETURNING id, name",
        normalized,
        tag_id,
    )
    return dict(record)


async def delete_tag(conn: asyncpg.Connection, tag_id: int) -> str:
    return await conn.execute("DELETE FROM tags WHERE id = $1", tag_id)
