# app/main.py
from fastapi import FastAPI
from sqlalchemy import text
from app.db.session import engine
from app.api.v1.routes_auth import router as auth_router
from app.api.v1.routes_resumes import router as resumes_router
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.logging import setup_logging
from fastapi.middleware.cors import CORSMiddleware

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Resume Analyzer API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev ke liye sab allow — production mein specific domain daalenge
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.exception("Unhandled error")
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong. Please try again later."},
    )

app.include_router(auth_router)
app.include_router(resumes_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/health/db")
async def db_health_check():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        return {"db_status": "connected", "result": result.scalar()}

