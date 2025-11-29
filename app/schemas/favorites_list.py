from __future__ import annotations

from pydantic import BaseModel

from .favorites import Favorite


class FavoritesListResponse(BaseModel):
    count: int
    favorites: list[Favorite]
