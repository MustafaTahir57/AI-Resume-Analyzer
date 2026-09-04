# app/api/v1/routes_auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import register_user, authenticate_user
from app.core.security import create_access_token
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import ForgotPasswordRequest, ResetPasswordRequest
from app.services.auth_service import forgot_password, reset_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_user(db, user_data)

@router.post("/login")
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, credentials.email, credentials.password)
    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/forgot-password")
async def forgot_password_route(payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    await forgot_password(db, payload.email)
    return {"message": "If that email exists, a reset link has been sent."}

@router.post("/reset-password")
async def reset_password_route(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    await reset_password(db, payload.token, payload.new_password)
    return {"message": "Password has been reset successfully."}