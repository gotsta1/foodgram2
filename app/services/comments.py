from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories import comments as comments_repo
from app.repositories import recipes as recipes_repo
from app.repositories.utils import row_affected
from app.services.files import process_image_input


async def list_comments(connection, recipe_id: int | None, q: str | None, limit: int, offset: int) -> list[dict]:
    return await comments_repo.list_comments(connection, recipe_id, q=q, limit=limit, offset=offset)


async def create_comment(connection, *, user_id: int, recipe_id: int, text: str | None, image: str | None) -> dict:
    recipe = await recipes_repo.get_by_id(connection, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    image_url = process_image_input(image, subdir="comments") if image else None
    return await comments_repo.create_comment(
        connection,
        user_id=user_id,
        recipe_id=recipe_id,
        text=text,
        image=image_url,
    )


async def delete_comment(connection, *, user_id: int, comment_id: int) -> None:
    comment = await comments_repo.get_by_id(connection, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own comments")
    result = await comments_repo.delete_comment(connection, comment_id)
    if not row_affected(result):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")


async def update_comment(
    connection,
    *,
    user_id: int,
    comment_id: int,
    recipe_id: int,
    text: str | None,
    image: str | None,
) -> dict:
    comment = await comments_repo.get_by_id(connection, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment["recipe_id"] != recipe_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment does not belong to this recipe")
    if comment["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own comments")

    new_text = text if text is not None else comment.get("text")
    new_image = process_image_input(image, subdir="comments") if image is not None else comment.get("image")

    if not new_text and not new_image:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either text or image must be provided")

    updated = await comments_repo.update_comment(
        connection,
        comment_id=comment_id,
        text=new_text,
        image=new_image,
    )
    return updated
