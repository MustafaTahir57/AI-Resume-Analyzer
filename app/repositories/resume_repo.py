# app/repositories/resume_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.resume import Resume

async def create_resume(db: AsyncSession, user_id, file_path: str, original_filename: str, extracted_text: str):
    resume = Resume(
        user_id=user_id,
        file_path=file_path,
        original_filename=original_filename,
        extracted_text=extracted_text,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume