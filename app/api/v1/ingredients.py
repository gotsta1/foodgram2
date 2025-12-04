from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from app.db import get_connection
from app.schemas import Ingredient, IngredientStatsResponse
from app.services.ingredients import get_ingredient_stats, list_ingredients

router = APIRouter(prefix="/ingredients")


@router.get("", response_model=List[Ingredient])
async def get_ingredients(
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    sort: str | None = None,
    connection=Depends(get_connection),
):
    return await list_ingredients(connection, q=q, limit=limit, offset=offset, sort=sort)


@router.get("/{ingredient_id}/statistics", response_model=IngredientStatsResponse)
async def get_ingredient_statistics(
    ingredient_id: int,
    connection=Depends(get_connection),
):
    return await get_ingredient_stats(connection, ingredient_id)
