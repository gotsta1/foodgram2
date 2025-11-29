from __future__ import annotations

from pydantic import BaseModel

from .shopping_list import ShoppingListItem


class ShoppingListResponse(BaseModel):
    count: int
    shopping_list: list[ShoppingListItem]
