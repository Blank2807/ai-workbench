from fastapi import APIRouter, HTTPException

from api.services.response_formatter import format_pr_checks

from api.schemas.github_schema import (
    CreatePullRequestRequest,
    EditPullRequestRequest,
)
from modules.github.tools import (
    github_create_pr,
    github_pr_checks,
    github_pr_edit,
    github_pr_status,
    github_pr_view,
)

router = APIRouter(
    prefix="/api/github",
    tags=["GitHub"],
)


@router.post("/create-pr")
def create_pull_request(request: CreatePullRequestRequest):
    result = github_create_pr(
        title=request.title,
        body=request.body,
        base=request.base,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.get("/pr-status")
def get_pull_request_status():
    result = github_pr_status()

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.get("/pr-checks")
def get_pull_request_checks():
    result = github_pr_checks()
    formatted = format_pr_checks(result)
    if not result.get("success") and formatted.get("status") != "pending":
        raise HTTPException(status_code=400, detail=formatted)

    return formatted


@router.get("/pr-view")
def view_pull_request():
    result = github_pr_view()

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/pr-edit")
def edit_pull_request(request: EditPullRequestRequest):
    if not request.title and not request.body:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "Either title or body is required.",
            },
        )

    result = github_pr_edit(
        title=request.title or "",
        body=request.body or "",
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result