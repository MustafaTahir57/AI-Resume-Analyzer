# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    openrouter_api_key: str   # ← add this line
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    frontend_url: str

    class Config:
        env_file = ".env"

settings = Settings()

# config.py reads .env, validates every variable, converts types, and exports one ready-to-use settings object that the rest of the app imports from. Good understanding.