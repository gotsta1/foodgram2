from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from app.db import get_connection
from app.schemas import Tag
from app.services.tags import list_tags

router = APIRouter(prefix="/tags")


@router.get("", response_model=List[Tag])
async def get_tags(
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    connection=Depends(get_connection),
):
    return await list_tags(connection, q=q, limit=limit, offset=offset)
