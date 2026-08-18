from fastapi import APIRouter, HTTPException

from api.schemas.git_schema import (
    GitCommitRequest,
    GitCreateBranchRequest,
    GitPushRequest,
)
from modules.github.tools import (
    git_add_all,
    git_commit,
    git_create_branch,
    git_current_branch,
    git_diff,
    git_push,
    git_status,
)

router = APIRouter(
    prefix="/api/git",
    tags=["Git"],
)


@router.get("/status")
def get_git_status():
    return git_status()


@router.get("/diff")
def get_git_diff():
    return git_diff()


@router.get("/branch")
def get_git_branch():
    return git_current_branch()


@router.post("/create-branch")
def create_git_branch(request: GitCreateBranchRequest):
    result = git_create_branch(request.branch_name)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/stage")
def stage_git_changes():
    result = git_add_all()

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/commit")
def commit_git_changes(request: GitCommitRequest):
    result = git_commit(request.message)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/push")
def push_git_branch(request: GitPushRequest):
    branch_name = request.branch_name

    if not branch_name:
        branch_result = git_current_branch()

        if not branch_result.get("success"):
            raise HTTPException(status_code=400, detail=branch_result)

        branch_name = branch_result.get("stdout", "").strip()

    if not branch_name:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "Current branch could not be detected.",
            },
        )

    result = git_push(branch_name)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result
