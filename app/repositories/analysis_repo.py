# app/repositories/analysis_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.analysis import Analysis

async def create_analysis(db: AsyncSession, resume_id, result: dict):
    analysis = Analysis(resume_id=resume_id, result=result)
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis