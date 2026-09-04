from passlib.context import CryptContext
# app/core/security.py  (add to existing file)
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload.get("sub")
    except Exception:
        return None

def create_reset_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=15)
    payload = {"sub": user_id, "purpose": "password_reset", "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

def decode_reset_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("purpose") != "password_reset":
            return None
        return payload.get("sub")
    except Exception:
        return None

pwd_Context = CryptContext(schemes=["bcrypt"], deprecated= "auto")

def hash_password(password: str) -> str:
    return pwd_Context.hash(password)

def verify_password(plain_password: str , hashed_password: str) -> bool:
    return pwd_Context.verify(plain_password, hashed_password)