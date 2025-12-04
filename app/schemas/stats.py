from __future__ import annotations

from pydantic import BaseModel


class RecipeStatsResponse(BaseModel):
    likes: int
    views: int
    comments: int
    avg_rate: float


class UserStatsResponse(BaseModel):
    likes: int
    subscribers: int
    comments: int


class IngredientStatsResponse(BaseModel):
    uses: int
