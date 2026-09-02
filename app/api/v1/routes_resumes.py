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
from fastapi import BackgroundTasks
from app.repositories.analysis_repo import create_pending_analysis, update_analysis_result, get_analysis_by_id
from app.db.session import AsyncSessionLocal

router = APIRouter(prefix="/resumes", tags=["resumes"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def run_analysis_task(analysis_id, resume_text: str):
    async with AsyncSessionLocal() as db:
        try:
            result = await analyze_resume(resume_text)
            await update_analysis_result(db, analysis_id, "completed", result)
        except Exception:
            await update_analysis_result(db, analysis_id, "failed", None)

@router.post("/{resume_id}/analyze")
async def analyze(
    resume_id: str = Path(...),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resume = await get_resume_by_id(db, resume_id)
    if resume is None or resume.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resume not found")

    analysis = await create_pending_analysis(db, resume.id)
    background_tasks.add_task(run_analysis_task, analysis.id, resume.extracted_text)

    return {"analysis_id": analysis.id, "status": "pending"}

@router.get("/analysis/{analysis_id}")
async def get_analysis(
    analysis_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    analysis = await get_analysis_by_id(db, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"id": analysis.id, "status": analysis.status, "result": analysis.result}

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
