from fastapi import APIRouter, HTTPException

from api.schemas.workspace_schema import (
    CreateFileRequest,
    OptionalWorkspacePathRequest,
    ReadFileRequest,
    ReplaceTextRequest,
    SearchTextRequest,
    UpdateFileRequest,
    WorkspacePathRequest,
)
from modules.ide.tools import (
    create_file,
    get_workspace_context,
    list_code_files,
    list_files,
    open_file,
    open_folder,
    read_file,
    replace_text,
    search_text,
    set_workspace,
    update_file,
)

router = APIRouter(
    prefix="/api/workspace",
    tags=["Workspace"],
)


@router.get("/context")
def get_context():
    return get_workspace_context()


@router.post("/set")
def set_workspace_folder(request: WorkspacePathRequest):
    result = set_workspace(request.path)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/open-file")
def open_workspace_file(request: WorkspacePathRequest):
    result = open_file(request.path)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/open-folder")
def open_workspace_folder(request: WorkspacePathRequest):
    result = open_folder(request.path)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/list-files")
def list_workspace_files(request: OptionalWorkspacePathRequest):
    result = list_files(request.path)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/list-code-files")
def list_workspace_code_files(request: OptionalWorkspacePathRequest):
    result = list_code_files(request.path)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/read-file")
def read_workspace_file(request: ReadFileRequest):
    result = read_file(
        path=request.path,
        max_chars=request.max_chars,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/search")
def search_workspace_text(request: SearchTextRequest):
    result = search_text(
        query=request.query,
        path=request.path,
        max_matches=request.max_matches,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result

@router.post("/create-file")
def create_workspace_file(request: CreateFileRequest):
    result = create_file(
        path=request.path,
        content=request.content,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/update-file")
def update_workspace_file(request: UpdateFileRequest):
    result = update_file(
        path=request.path,
        content=request.content,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/replace-text")
def replace_workspace_text(request: ReplaceTextRequest):
    result = replace_text(
        path=request.path,
        old_text=request.old_text,
        new_text=request.new_text,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result)

    return result