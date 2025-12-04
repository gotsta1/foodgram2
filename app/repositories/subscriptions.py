from __future__ import annotations

from typing import Any, Dict, List

import asyncpg


async def list_subscriptions(conn: asyncpg.Connection, user_id: int, q: str | None, limit: int, offset: int) -> List[Dict[str, Any]]:
    params: list[Any] = [user_id]
    where = "s.user_id = $1"
    if q:
        params.append(f"%{q.lower()}%")
        where += f" AND (LOWER(u.first_name) LIKE ${len(params)} OR LOWER(u.last_name) LIKE ${len(params)})"
    params.extend([limit, offset])
    query = f"""
        SELECT s.id, s.user_id, s.following_id, s.added_at,
               u.email, u.first_name, u.last_name, u.avatar
        FROM subscriptions s
        JOIN users u ON u.id = s.following_id
        WHERE {where}
        ORDER BY s.added_at DESC
        LIMIT ${len(params)-1} OFFSET ${len(params)}
    """
    records = await conn.fetch(query, *params)
    return [dict(r) for r in records]


async def list_followers(conn: asyncpg.Connection, user_id: int, q: str | None, limit: int, offset: int) -> List[Dict[str, Any]]:
    params: list[Any] = [user_id]
    where = "s.following_id = $1"
    if q:
        params.append(f"%{q.lower()}%")
        where += f" AND (LOWER(u.first_name) LIKE ${len(params)} OR LOWER(u.last_name) LIKE ${len(params)})"
    params.extend([limit, offset])
    query = f"""
        SELECT s.id, s.user_id, s.following_id, s.added_at,
               u.email, u.first_name, u.last_name, u.avatar
        FROM subscriptions s
        JOIN users u ON u.id = s.user_id
        WHERE {where}
        ORDER BY s.added_at DESC
        LIMIT ${len(params)-1} OFFSET ${len(params)}
    """
    records = await conn.fetch(query, *params)
    return [dict(r) for r in records]


async def upsert_item(conn: asyncpg.Connection, user_id: int, following_id: int) -> Dict[str, Any]:
    record = await conn.fetchrow(
        """
        INSERT INTO subscriptions (user_id, following_id)
        VALUES ($1, $2)
        ON CONFLICT (user_id, following_id)
        DO UPDATE SET added_at = NOW()
        RETURNING id, user_id, following_id, added_at
        """,
        user_id,
        following_id,
    )
    return dict(record)


async def delete_item(conn: asyncpg.Connection, user_id: int, following_id: int) -> str:
    return await conn.execute(
        "DELETE FROM subscriptions WHERE user_id = $1 AND following_id = $2",
        user_id,
        following_id,
    )


async def get_subscription(conn: asyncpg.Connection, user_id: int, following_id: int) -> Optional[Dict[str, Any]]:
    record = await conn.fetchrow(
        "SELECT id, user_id, following_id, added_at FROM subscriptions WHERE user_id = $1 AND following_id = $2",
        user_id,
        following_id,
    )
    return dict(record) if record else None


async def count_followers(conn: asyncpg.Connection, user_id: int) -> int:
    val = await conn.fetchval("SELECT COUNT(*) FROM subscriptions WHERE following_id = $1", user_id)
    return int(val or 0)
