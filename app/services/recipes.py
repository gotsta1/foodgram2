from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories import ingredients as ingredients_repo
from app.repositories import recipe_ingredients as ri_repo
from app.repositories import recipe_tags as rt_repo
from app.repositories import recipes as recipes_repo
from app.repositories import tags as tags_repo
from app.repositories import favorites as favorites_repo
from app.repositories import comments as comments_repo
from app.repositories import ratings as ratings_repo
from app.repositories.utils import row_affected
from app.services.files import process_image_input


async def list_recipes(connection, q: str | None, limit: int, offset: int, sort: str | None = None) -> list[dict]:
    recipes = await recipes_repo.list_recipes(connection, q=q, limit=limit, offset=offset, sort=sort)
    enriched = []
    for recipe in recipes:
        enriched.append(await _attach_details(connection, recipe))
    return enriched


async def list_user_recipes(connection, user_id: int, q: str | None, limit: int, offset: int) -> list[dict]:
    recipes = await recipes_repo.list_user_recipes(connection, user_id, q=q, limit=limit, offset=offset)
    enriched = []
    for recipe in recipes:
        enriched.append(await _attach_details(connection, recipe))
    return enriched


async def get_recipe_or_404(connection, recipe_id: int) -> dict:
    recipe = await recipes_repo.get_by_id(connection, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    await recipes_repo.increment_views(connection, recipe_id)
    recipe["views"] = (recipe.get("views") or 0) + 1
    return await _attach_details(connection, recipe)


async def get_recipe_stats(connection, recipe_id: int) -> dict:
    recipe = await recipes_repo.get_by_id(connection, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    likes = await favorites_repo.count_for_recipe(connection, recipe_id)
    comments = await comments_repo.count_for_recipe(connection, recipe_id)
    avg_rate = await ratings_repo.get_avg_rate(connection, recipe_id)
    return {
        "likes": likes,
        "views": recipe.get("views", 0),
        "comments": comments,
        "avg_rate": round(avg_rate, 2),
    }


async def create_recipe(
    connection,
    *,
    author_id: int,
    name: str,
    image: str,
    text: str,
    cooking_time: int,
    tags: list[str],
    ingredients: list[dict],
) -> dict:
    image_url = process_image_input(image, subdir="recipes")
    recipe = await recipes_repo.create_recipe(
        connection,
        author_id=author_id,
        name=name,
        image=image_url or "",
        text=text,
        cooking_time=cooking_time,
    )
    await _sync_recipe_tags(connection, recipe["id"], tags)
    await _sync_recipe_ingredients(connection, recipe["id"], author_id, ingredients)
    return await _attach_details(connection, recipe)


async def update_recipe(
    connection,
    *,
    recipe_id: int,
    author_id: int,
    name: str | None,
    image: str | None,
    text: str | None,
    cooking_time: int | None,
    tags: list[str] | None,
    ingredients: list[dict] | None,
) -> dict:
    recipe = await recipes_repo.get_by_id(connection, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    if recipe["author_id"] != author_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the author can update this recipe")

    new_name = name if name is not None else recipe["name"]
    new_text = text if text is not None else recipe["text"]
    new_cooking_time = cooking_time if cooking_time is not None else recipe["cooking_time"]
    new_image = process_image_input(image, subdir="recipes") if image is not None else recipe["image"]

    if new_cooking_time is None or new_cooking_time <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid cooking_time")

    updated = await recipes_repo.update_recipe(
        connection,
        recipe_id=recipe_id,
        name=new_name,
        image=new_image or "",
        text=new_text,
        cooking_time=new_cooking_time,
    )
    if tags is not None:
        await _sync_recipe_tags(connection, recipe_id, tags)
    if ingredients is not None:
        await _sync_recipe_ingredients(connection, recipe_id, author_id, ingredients)
    return await _attach_details(connection, updated)


async def delete_recipe(connection, *, recipe_id: int, author_id: int) -> None:
    recipe = await recipes_repo.get_by_id(connection, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    if recipe["author_id"] != author_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the author can delete this recipe")
    result = await recipes_repo.delete_recipe(connection, recipe_id)
    if not row_affected(result):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")


async def _sync_recipe_tags(connection, recipe_id: int, tags: list[str]) -> None:
    normalized = []
    for tag in tags or []:
        normalized_name = tag.strip().lower()
        if normalized_name:
            normalized.append(normalized_name)

    unique_tags = list(set(normalized))

    await rt_repo.delete_all_for_recipe(connection, recipe_id)

    for tag_name in unique_tags:
        existing = await tags_repo.get_by_name(connection, tag_name)
        if existing:
            tag_id = existing["id"]
        else:
            created = await tags_repo.create_tag(connection, tag_name)
            tag_id = created["id"]
        await rt_repo.upsert_item(connection, recipe_id, tag_id)


async def _sync_recipe_ingredients(connection, recipe_id: int, author_id: int, ingredients: list[dict]) -> None:
    await ri_repo.delete_all_for_recipe(connection, recipe_id)

    for item in ingredients or []:
        if hasattr(item, "ingredient_id"):
            ingredient_id = getattr(item, "ingredient_id")
            amount = getattr(item, "amount")
        elif isinstance(item, dict):
            ingredient_id = item.get("ingredient_id")
            amount = item.get("amount")
        else:
            raise HTTPException(status_code=400, detail="Invalid ingredient payload")

        if ingredient_id is None or amount is None:
            raise HTTPException(status_code=400, detail="ingredient_id and amount are required for ingredients")
        if not (1 <= int(amount) <= 32000):
            raise HTTPException(status_code=400, detail="amount must be between 1 and 32000")

        ingredient = await ingredients_repo.get_by_id(connection, ingredient_id)
        if not ingredient:
            raise HTTPException(status_code=404, detail=f"Ingredient {ingredient_id} not found")

        await ri_repo.upsert_item(connection, recipe_id, ingredient_id, int(amount))


async def _attach_details(connection, recipe: dict) -> dict:
    recipe_id = recipe["id"]

    tag_links = await rt_repo.list_items(connection, recipe_id)
    tag_names: list[str] = []
    for link in tag_links:
        tag = await tags_repo.get_by_id(connection, link["tag_id"])
        if tag:
            tag_names.append(tag["name"])
    recipe["tags"] = tag_names

    ing_links = await ri_repo.list_items(connection, recipe_id)
    recipe["ingredients"] = [
        {"ingredient_id": item["ingredient_id"], "amount": item["amount"]}
        for item in ing_links
    ]
    return recipe
