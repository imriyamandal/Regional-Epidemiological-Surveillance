from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database.models import User
from app.database.session import get_db
from app.schemas.auth import (
    PasswordResetRequest,
    PasswordUpdate,
    ProfileUpdate,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        user = await AuthService.register(db, data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await AuthService.authenticate(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return AuthService.create_tokens(user)


@router.get("/me", response_model=UserResponse)
async def me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    data: ProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if data.full_name:
        current_user.full_name = data.full_name
    await db.flush()
    await db.refresh(current_user)
    return current_user


@router.post("/forgot-password")
async def forgot_password(data: PasswordResetRequest):
    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/change-password")
async def change_password(
    data: PasswordUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    from app.core.security import get_password_hash, verify_password

    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.hashed_password = get_password_hash(data.new_password)
    await db.flush()
    return {"message": "Password updated successfully"}
