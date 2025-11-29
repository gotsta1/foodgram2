from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class FavoriteCreate(BaseModel):
    recipe_id: int


class Favorite(BaseModel):
    id: int
    recipe_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
