from pathlib import Path
import sys

from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

API_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = API_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.routers.git_router import router as git_router
from api.routers.github_router import router as github_router
from api.routers.workspace_router import router as workspace_router
from api.routers.ide_router import router as ide_router

app = FastAPI(
    title="AI Workbench API",
    description="Backend API for IDE, Git, GitHub, and future AI Workbench modules.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(git_router)
app.include_router(github_router)
app.include_router(workspace_router)
app.include_router(ide_router)


@app.get("/")
def root():
    return {
        "success": True,
        "message": "AI Workbench API is running.",
    }


@app.get("/health")
def health_check():
    return {
        "success": True,
        "status": "healthy",
    }


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
