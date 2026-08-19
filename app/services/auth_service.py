# app/services/auth_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.user_repo import get_user_by_email, create_user
from app.core.security import hash_password, verify_password
from app.schemas.user import UserCreate

async def register_user(db: AsyncSession, user_data: UserCreate):
    existing = await get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed = hash_password(user_data.password)
    return await create_user(db, user_data.email, hashed, user_data.full_name)

async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user