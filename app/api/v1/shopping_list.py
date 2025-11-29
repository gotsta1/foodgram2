from __future__ import annotations

from fastapi import APIRouter, Depends

from app.db import get_connection
from app.dependencies.auth import get_current_user
from app.schemas import ShoppingListResponse
from app.services.shopping_list import list_items

router = APIRouter(prefix="/shopping-list")


@router.get("", response_model=ShoppingListResponse)
async def get_shopping_list(
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    items = await list_items(connection, current_user["id"], q=q, limit=limit, offset=offset)
    return ShoppingListResponse(count=len(items), shopping_list=items)
