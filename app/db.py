import os
from typing import AsyncIterator, Optional

import asyncpg
from fastapi import HTTPException, status
from asyncpg.pool import Pool

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://foodgram:foodgram@db:5432/foodgram")

pool: Optional[Pool] = None


async def connect_to_db() -> None:
    """Create a global connection pool."""
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(DATABASE_URL, command_timeout=60)


async def close_db_connection() -> None:
    """Close the global connection pool."""
    global pool
    if pool:
        await pool.close()
        pool = None


async def get_connection() -> AsyncIterator[asyncpg.Connection]:
    """Provide a single connection with an open transaction."""
    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database pool is not initialized",
        )

    async with pool.acquire() as connection:
        async with connection.transaction():
            yield connection


async def init_db() -> None:
    """Create tables if they are missing (lightweight bootstrap, not a migration system)."""
    schema_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(150) UNIQUE NOT NULL,
        email VARCHAR(254) UNIQUE NOT NULL,
        first_name VARCHAR(150) NOT NULL,
        last_name VARCHAR(150) NOT NULL,
        avatar VARCHAR(255),
        password_hash VARCHAR(255) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS tags (
        id SERIAL PRIMARY KEY,
        name VARCHAR(256) UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS ingredients (
        id SERIAL PRIMARY KEY,
        name VARCHAR(128) UNIQUE NOT NULL,
        measurement_unit VARCHAR(64) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS recipes (
        id SERIAL PRIMARY KEY,
        author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name VARCHAR(256) NOT NULL,
        image VARCHAR(255) NOT NULL,
        text TEXT NOT NULL,
        cooking_time SMALLINT NOT NULL CHECK (cooking_time >= 1 AND cooking_time <= 32000),
        views INTEGER NOT NULL DEFAULT 0,
        pub_date TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW())
    );

    CREATE TABLE IF NOT EXISTS recipe_ingredients (
        id SERIAL PRIMARY KEY,
        recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
        ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
        amount SMALLINT NOT NULL CHECK (amount >= 1 AND amount <= 32000),
        UNIQUE (recipe_id, ingredient_id)
    );

    CREATE TABLE IF NOT EXISTS recipe_tag (
        id SERIAL PRIMARY KEY,
        recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
        tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW()),
        UNIQUE (recipe_id, tag_id)
    );

    CREATE TABLE IF NOT EXISTS comments (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
        text TEXT,
        image VARCHAR(255),
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW()),
        CONSTRAINT comments_check CHECK (
            (text IS NOT NULL AND text <> '') OR (image IS NOT NULL AND image <> '')
        )
    );

    CREATE TABLE IF NOT EXISTS ratings (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW()),
        rate INTEGER NOT NULL CHECK (rate >= 1 AND rate <= 5),
        UNIQUE (user_id, recipe_id)
    );

    CREATE TABLE IF NOT EXISTS favorites (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
        UNIQUE (user_id, recipe_id)
    );

    CREATE TABLE IF NOT EXISTS shopping_list (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
        UNIQUE (user_id, recipe_id)
    );

    CREATE TABLE IF NOT EXISTS subscriptions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        following_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        added_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW()),
        UNIQUE (user_id, following_id),
        CONSTRAINT subscriptions_check CHECK (user_id <> following_id)
    );
    ALTER TABLE recipes ADD COLUMN IF NOT EXISTS views INTEGER NOT NULL DEFAULT 0;
    """

    async with pool.acquire() as connection:  # type: ignore[arg-type]
        await connection.execute(schema_sql)
