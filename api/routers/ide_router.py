from fastapi import APIRouter, HTTPException

from modules.ide.agent import execute_ide_agent

from api.schemas.ide_schema import (
    ProjectPathRequest,
    RunFileRequest,
    IdeChatRequest,
)
from modules.ide.tools import (
    run_file,
    run_project_build,
    run_project_tests,
    run_static_analysis,
)

router = APIRouter(
    prefix="/api/ide",
    tags=["IDE"],
)


@router.post("/run-file")
def run_ide_file(request: RunFileRequest):
    result = run_file(request.path)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/run-tests")
def run_ide_tests(request: ProjectPathRequest):
    result = run_project_tests(request.path)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/build")
def build_ide_project(request: ProjectPathRequest):
    result = run_project_build(request.path)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/static-analysis")
def run_ide_static_analysis(request: ProjectPathRequest):
    result = run_static_analysis(request.path)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/chat")
def chat_with_ide_agent(request: IdeChatRequest):
    answer, updated_chat_history = execute_ide_agent(
        user_question=request.user_question,
        chat_history=request.chat_history,
    )

    return {
        "success": True,
        "answer": answer,
        "chat_history": updated_chat_history,
    }