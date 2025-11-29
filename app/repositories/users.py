from __future__ import annotations

from typing import Any, Dict, Optional

import asyncpg


async def get_by_id(conn: asyncpg.Connection, user_id: int) -> Optional[Dict[str, Any]]:
    record = await conn.fetchrow(
        "SELECT id, username, email, first_name, last_name, avatar, password_hash FROM users WHERE id = $1",
        user_id,
    )
    return dict(record) if record else None


async def get_by_email(conn: asyncpg.Connection, email: str) -> Optional[Dict[str, Any]]:
    record = await conn.fetchrow(
        "SELECT id, username, email, first_name, last_name, avatar, password_hash FROM users WHERE email = $1",
        email,
    )
    return dict(record) if record else None


async def create_user(
    conn: asyncpg.Connection,
    *,
    username: str,
    email: str,
    first_name: str,
    last_name: str,
    avatar: Optional[str],
    password_hash: str,
) -> Dict[str, Any]:
    record = await conn.fetchrow(
        """
        INSERT INTO users (username, email, first_name, last_name, avatar, password_hash)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, username, email, first_name, last_name, avatar, password_hash
        """,
        username,
        email,
        first_name,
        last_name,
        avatar,
        password_hash,
    )
    return dict(record)


async def list_users(conn: asyncpg.Connection, q: str | None, limit: int, offset: int) -> list[Dict[str, Any]]:
    base_query = """
        SELECT id, email, first_name, last_name, avatar
        FROM users
    """
    where_clause = ""
    params: list[Any] = []
    if q:
        where_clause = "WHERE LOWER(first_name) LIKE $1 OR LOWER(last_name) LIKE $1"
        params.append(f"%{q.lower()}%")

    params.extend([limit, offset])
    query = f"""
        {base_query}
        {where_clause}
        ORDER BY id
        LIMIT ${len(params)-1} OFFSET ${len(params)}
    """
    records = await conn.fetch(query, *params)
    return [dict(r) for r in records]


async def update_user(
    conn: asyncpg.Connection,
    *,
    user_id: int,
    email: Optional[str],
    first_name: Optional[str],
    last_name: Optional[str],
    avatar: Optional[str],
) -> Dict[str, Any]:
    record = await conn.fetchrow(
        """
        UPDATE users
        SET email = COALESCE($1, email),
            first_name = COALESCE($2, first_name),
            last_name = COALESCE($3, last_name),
            avatar = CASE WHEN $4 = '__DELETE__' THEN NULL ELSE COALESCE($4, avatar) END
        WHERE id = $5
        RETURNING id, email, first_name, last_name, avatar
        """,
        email,
        first_name,
        last_name,
        avatar,
        user_id,
    )
    return dict(record)
