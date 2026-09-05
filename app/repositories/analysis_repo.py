# app/repositories/analysis_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.analysis import Analysis
from sqlalchemy import select
from datetime import datetime, timedelta

async def create_analysis(db: AsyncSession, resume_id, result: dict):
    analysis = Analysis(resume_id=resume_id, result=result)
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis

async def create_pending_analysis(db: AsyncSession, resume_id):
    analysis = Analysis(resume_id=resume_id, status="pending", result=None)
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis

async def update_analysis_result(db: AsyncSession, analysis_id, status: str, result: dict | None):
    analysis = await db.get(Analysis, analysis_id)
    analysis.status = status
    analysis.result = result
    await db.commit()

async def get_analysis_by_id(db: AsyncSession, analysis_id):
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()

    if analysis and analysis.status == "pending":
        age = datetime.utcnow() - analysis.created_at
        if age > timedelta(minutes=3):
            analysis.status = "failed"
            await db.commit()
            await db.refresh(analysis)

    return analysis

# app/repositories/analysis_repo.py — add this
async def get_analyses_by_resume(db: AsyncSession, resume_id):
    result = await db.execute(select(Analysis).where(Analysis.resume_id == resume_id))
    return result.scalars().all()