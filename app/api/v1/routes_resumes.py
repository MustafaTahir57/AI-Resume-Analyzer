# app/api/v1/routes_resumes.py
import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.file_service import extract_text
from app.repositories.resume_repo import create_resume
from fastapi import Path
from app.services.ai_service import analyze_resume
from app.repositories.resume_repo import get_resume_by_id
from app.repositories.analysis_repo import create_analysis

router = APIRouter(prefix="/resumes", tags=["resumes"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are allowed")

    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    extracted = extract_text(file_path, file.filename)

    resume = await create_resume(db, current_user.id, file_path, file.filename, extracted)
    return {"id": resume.id, "filename": resume.original_filename, "text_preview": extracted[:200]}

@router.post("/{resume_id}/analyze")
async def analyze(
    resume_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resume = await get_resume_by_id(db, resume_id)
    if resume is None or resume.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resume not found")

    result = await analyze_resume(resume.extracted_text)
    analysis = await create_analysis(db, resume.id, result)

    return {"analysis_id": analysis.id, "result": result}