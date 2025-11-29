from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Tuple
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", "media"))
ALLOWED_CONTENT_TYPES: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


async def save_image(file: UploadFile, subdir: str) -> str:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Allowed: jpeg, png, webp",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Max size is 5MB",
        )

    ext = ALLOWED_CONTENT_TYPES[file.content_type]
    return _write_bytes(content, ext, subdir)


def save_base64_image(data: str, subdir: str) -> str:
    """
    Accept base64 string with optional data URL prefix and save to media.
    """
    try:
        mime, raw_b64 = _split_data_url(data)
        ext = ALLOWED_CONTENT_TYPES.get(mime, ".png") if mime else ".png"
        content = base64.b64decode(raw_b64)
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid base64 image")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Max size is 5MB",
        )

    return _write_bytes(content, ext, subdir)


def _split_data_url(data: str) -> Tuple[str | None, str]:
    if data.startswith("data:"):
        header, _, b64data = data.partition(",")
        mime = header.split(";")[0].replace("data:", "", 1)
        return mime, b64data
    return None, data


def _write_bytes(content: bytes, ext: str, subdir: str) -> str:
    target_dir = MEDIA_ROOT / subdir
    _ensure_dir(target_dir)
    filename = f"{uuid4().hex}{ext}"
    target_path = target_dir / filename
    target_path.write_bytes(content)
    return f"/media/{subdir}/{filename}"


def process_image_input(image_value: str | None, subdir: str) -> str | None:
    """
    Accepts either an existing URL/path or base64 string. Returns stored media URL.
    """
    if not image_value:
        return None
    image_value = image_value.strip()
    if image_value.startswith("/media/") or image_value.startswith("http"):
        return image_value
    return save_base64_image(image_value, subdir=subdir)
