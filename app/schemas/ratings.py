from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RatingCreate(BaseModel):
    rate: int


class Rating(BaseModel):
    id: int
    recipe_id: int
    user_id: int
    rate: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RatingsResponse(BaseModel):
    avg_rate: float
    ratings: list[Rating]
