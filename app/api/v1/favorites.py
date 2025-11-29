from __future__ import annotations

from fastapi import APIRouter, Depends

from app.db import get_connection
from app.dependencies.auth import get_current_user
from app.schemas import FavoritesListResponse
from app.services.favorites import list_favorites

router = APIRouter(prefix="/favorites")


@router.get("", response_model=FavoritesListResponse)
async def get_favorites(
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    favorites = await list_favorites(connection, current_user["id"], q=q, limit=limit, offset=offset)
    return FavoritesListResponse(count=len(favorites), favorites=favorites)
