from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class IngredientBase(BaseModel):
    name: str
    measurement_unit: str


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(IngredientBase):
    pass


class Ingredient(BaseModel):
    id: int
    name: str
    measurement_unit: str

    model_config = ConfigDict(from_attributes=True)
