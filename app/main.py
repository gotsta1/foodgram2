from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import router as api_router
from app.db import close_db_connection, connect_to_db, init_db

app = FastAPI(title="Foodgram API (FastAPI + PostgreSQL, raw SQL)")


@app.on_event("startup")
async def on_startup() -> None:
    await connect_to_db()
    await init_db()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await close_db_connection()


app.include_router(api_router)
app.mount("/media", StaticFiles(directory="media"), name="media")
