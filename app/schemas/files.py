from __future__ import annotations

from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    url: str
