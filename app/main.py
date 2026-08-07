# app/main.py
from fastapi import FastAPI
from sqlalchemy import text
from app.db.session import engine

app = FastAPI(title="AI Resume Analyzer API", version="1.0.0")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/health/db")
async def db_health_check():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        return {"db_status": "connected", "result": result.scalar()}