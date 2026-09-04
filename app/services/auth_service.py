# app/services/auth_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.user_repo import get_user_by_email, create_user
from app.core.security import hash_password, verify_password
from app.schemas.user import UserCreate
from app.core.security import create_reset_token, decode_reset_token
from app.repositories.user_repo import update_user_password
from app.services.email_service import send_reset_email
import logging
logger = logging.getLogger(__name__)

async def register_user(db: AsyncSession, user_data: UserCreate):
    existing = await get_user_by_email(db, user_data.email)
    if existing:
        logger.warning(f"Registration attempt with existing email: {user_data.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed = hash_password(user_data.password)
    user = await create_user(db, user_data.email, hashed, user_data.full_name)
    logger.info(f"New user registered: {user.email}")
    return user

async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        logger.warning(f"No user with this email Id exists")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
   
    return user

async def forgot_password(db: AsyncSession, email: str):
    user = await get_user_by_email(db, email)
    if not user:
        # Security: don't reveal whether the email exists
        logger.info(f"Password reset requested for non-existent email: {email}")
        return
    token = create_reset_token(str(user.id))
    # TODO: send this via email in production. For now, log it so we can test.
    logger.info(f"Password reset token for {email}: {token}")

async def reset_password(db: AsyncSession, token: str, new_password: str):
    user_id = decode_reset_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    hashed = hash_password(new_password)
    await update_user_password(db, user_id, hashed)

async def forgot_password(db: AsyncSession, email: str):
    user = await get_user_by_email(db, email)
    if not user:
        logger.info(f"Password reset requested for non-existent email: {email}")
        return
    token = create_reset_token(str(user.id))
    send_reset_email(user.email, token)
    logger.info(f"Password reset email sent to: {email}")