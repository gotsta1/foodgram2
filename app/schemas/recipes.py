from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RecipeIngredientInput(BaseModel):
    ingredient_id: int
    amount: int


class RecipeBase(BaseModel):
    name: str
    image: str
    text: str
    cooking_time: int
    tags: list[str] = Field(default_factory=list)
    ingredients: list[RecipeIngredientInput] = Field(default_factory=list)


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(BaseModel):
    name: str | None = None
    image: str | None = None
    text: str | None = None
    cooking_time: int | None = None
    tags: list[str] | None = None
    ingredients: list[RecipeIngredientInput] | None = None


class Recipe(BaseModel):
    views: int
    id: int
    author_id: int
    pub_date: datetime
    name: str
    image: str
    text: str
    cooking_time: int
    tags: list[str] = Field(default_factory=list)
    ingredients: list[RecipeIngredientInput] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RecipeIngredientBase(BaseModel):
    recipe_id: int
    ingredient_id: int
    amount: int


class RecipeIngredient(BaseModel):
    id: int
    recipe_id: int
    ingredient_id: int
    amount: int

    model_config = ConfigDict(from_attributes=True)


class RecipeTagBase(BaseModel):
    recipe_id: int
    tag_id: int


class RecipeTag(BaseModel):
    id: int
    recipe_id: int
    tag_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
