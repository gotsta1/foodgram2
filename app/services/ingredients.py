from __future__ import annotations

from app.repositories import ingredients as ingredients_repo
from app.repositories import recipe_ingredients as ri_repo


async def list_ingredients(connection, q: str | None, limit: int, offset: int, sort: str | None = None) -> list[dict]:
    return await ingredients_repo.list_ingredients(connection, q=q, limit=limit, offset=offset, sort=sort)


async def get_ingredient_stats(connection, ingredient_id: int) -> dict:
    ingredient = await ingredients_repo.get_by_id(connection, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
    uses = await ri_repo.count_recipes_for_ingredient(connection, ingredient_id)
    return {"uses": uses}
