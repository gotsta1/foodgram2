from __future__ import annotations

from pydantic import BaseModel

from .recipes import Recipe
from .users import User


class UserRecipesResponse(BaseModel):
    user: User
    recipes: list[Recipe]
