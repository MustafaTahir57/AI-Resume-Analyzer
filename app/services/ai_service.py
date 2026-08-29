# app/services/ai_service.py
import httpx
import json
from app.core.config import settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

async def analyze_resume(resume_text: str, job_description: str | None = None) -> dict:
    prompt = f"""You are an expert resume reviewer. Analyze this resume and return ONLY valid JSON (no markdown, no extra text) with this exact structure:
{{
  "ats_score": <number 0-100>,
  "extracted_skills": [<list of strings>],
  "missing_technologies": [<list of strings>],
  "strengths": [<list of strings>],
  "weaknesses": [<list of strings>],
  "formatting_suggestions": [<list of strings>],
  "grammar_issues": [<list of strings>]
}}

Resume text:
{resume_text}

{"Job description to match against: " + job_description if job_description else ""}
"""

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "messages": [{"role": "user", "content": prompt}],
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

    ai_text = result["choices"][0]["message"]["content"]
    return json.loads(ai_text)