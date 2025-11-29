from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.db import get_connection
from app.schemas import LoginRequest, TokenResponse, UserCreate
from app.services.auth import login_user, register_user

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, connection=Depends(get_connection)):
    return await register_user(connection, payload)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, connection=Depends(get_connection)):
    return await login_user(connection, payload.email, payload.password)
