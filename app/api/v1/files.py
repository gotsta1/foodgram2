from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from app.dependencies.auth import get_current_user
from app.schemas import FileUploadResponse
from app.services.files import save_image

router = APIRouter(prefix="/files")


@router.post("/avatars", response_model=FileUploadResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    url = await save_image(file, subdir="avatars")
    return FileUploadResponse(url=url)


@router.post("/recipes", response_model=FileUploadResponse)
async def upload_recipe_image(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    url = await save_image(file, subdir="recipes")
    return FileUploadResponse(url=url)
