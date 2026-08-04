from fastapi import FastAPI

app = FastAPI(title="AI Resume Analyzer", version="1.0.0")

@app.get("/health")
async def health_check():
    return{"status": "ok"}
