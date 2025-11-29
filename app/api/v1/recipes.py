from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, status

from app.db import get_connection
from app.dependencies.auth import get_current_user
from app.schemas import (
    Comment,
    CommentCreate,
    Favorite,
    Rating,
    RatingCreate,
    RatingsResponse,
    Recipe,
    RecipeCreate,
    RecipeUpdate,
)
from app.services.comments import create_comment, delete_comment, list_comments, update_comment
from app.services.favorites import add_favorite, delete_favorite
from app.services.ratings import create_rating, get_avg_rate, list_ratings
from app.services.shopping_list import add_item as add_to_shopping_list
from app.services.shopping_list import delete_item as delete_from_shopping_list
from app.services.recipes import create_recipe, delete_recipe, get_recipe_or_404, list_recipes, update_recipe
from app.services.files import process_image_input

router = APIRouter(prefix="/recipes")


@router.get("", response_model=List[Recipe])
async def get_recipes(
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    sort: str | None = None,
    connection=Depends(get_connection),
):
    return await list_recipes(connection, q=q, limit=limit, offset=offset, sort=sort)


@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: int, connection=Depends(get_connection)):
    return await get_recipe_or_404(connection, recipe_id)


@router.post("", response_model=Recipe, status_code=status.HTTP_201_CREATED)
async def create_recipe_endpoint(
    payload: RecipeCreate,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    return await create_recipe(
        connection,
        author_id=current_user["id"],
        name=payload.name,
        image=payload.image,
        text=payload.text,
        cooking_time=payload.cooking_time,
        tags=payload.tags,
        ingredients=payload.ingredients,
    )


@router.patch("/{recipe_id}", response_model=Recipe)
async def update_recipe_endpoint(
    recipe_id: int,
    payload: RecipeUpdate,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    if all(
        value is None
        for value in [
            payload.name,
            payload.image,
            payload.text,
            payload.cooking_time,
            payload.tags,
            payload.ingredients,
        ]
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    return await update_recipe(
        connection,
        recipe_id=recipe_id,
        author_id=current_user["id"],
        name=payload.name,
        image=payload.image,
        text=payload.text,
        cooking_time=payload.cooking_time,
        tags=payload.tags,
        ingredients=payload.ingredients,
    )


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe_endpoint(
    recipe_id: int,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    await delete_recipe(connection, recipe_id=recipe_id, author_id=current_user["id"])
    return None


@router.get("/{recipe_id}/comments", response_model=List[Comment])
async def get_recipe_comments(
    recipe_id: int,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    connection=Depends(get_connection),
):
    return await list_comments(connection, recipe_id, q=q, limit=limit, offset=offset)


@router.post("/{recipe_id}/comments", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def add_comment(
    recipe_id: int,
    payload: CommentCreate,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    return await create_comment(
        connection,
        user_id=current_user["id"],
        recipe_id=recipe_id,
        text=payload.text,
        image=payload.image,
    )


@router.patch("/{recipe_id}/comments/{comment_id}", response_model=Comment)
async def update_comment_endpoint(
    recipe_id: int,
    comment_id: int,
    payload: CommentCreate,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    return await update_comment(
        connection,
        user_id=current_user["id"],
        comment_id=comment_id,
        recipe_id=recipe_id,
        text=payload.text,
        image=payload.image,
    )


@router.delete("/{recipe_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_endpoint(
    recipe_id: int,
    comment_id: int,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    await delete_comment(connection, user_id=current_user["id"], comment_id=comment_id)
    return None


@router.post("/{recipe_id}/favorite", response_model=Favorite, status_code=status.HTTP_201_CREATED)
async def add_recipe_favorite(
    recipe_id: int,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    return await add_favorite(connection, user_id=current_user["id"], recipe_id=recipe_id)


@router.delete("/{recipe_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe_favorite(
    recipe_id: int,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    await delete_favorite(connection, user_id=current_user["id"], recipe_id=recipe_id)
    return None


@router.post("/{recipe_id}/shopping-list", status_code=status.HTTP_201_CREATED)
async def add_recipe_to_shopping_list(
    recipe_id: int,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    return await add_to_shopping_list(connection, user_id=current_user["id"], recipe_id=recipe_id)


@router.delete("/{recipe_id}/shopping-list", status_code=status.HTTP_204_NO_CONTENT)
async def remove_recipe_from_shopping_list(
    recipe_id: int,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    await delete_from_shopping_list(connection, user_id=current_user["id"], recipe_id=recipe_id)
    return None


@router.get("/{recipe_id}/ratings", response_model=RatingsResponse)
async def get_recipe_ratings(
    recipe_id: int,
    limit: int = 50,
    offset: int = 0,
    connection=Depends(get_connection),
):
    ratings = await list_ratings(connection, recipe_id, limit=limit, offset=offset)
    avg_rate = await get_avg_rate(connection, recipe_id)
    return RatingsResponse(avg_rate=round(avg_rate, 2), ratings=ratings)


@router.post("/{recipe_id}/ratings", response_model=Rating, status_code=status.HTTP_201_CREATED)
async def add_rating(
    recipe_id: int,
    payload: RatingCreate,
    connection=Depends(get_connection),
    current_user=Depends(get_current_user),
):
    return await create_rating(
        connection,
        user_id=current_user["id"],
        recipe_id=recipe_id,
        rate=payload.rate,
    )
