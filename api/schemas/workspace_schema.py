from pydantic import BaseModel, Field


class WorkspacePathRequest(BaseModel):
    path: str = Field(..., min_length=1)


class OptionalWorkspacePathRequest(BaseModel):
    path: str = "."


class ReadFileRequest(BaseModel):
    path: str
    max_chars: int = 30000


class SearchTextRequest(BaseModel):
    query: str = Field(..., min_length=1)
    path: str = "."
    max_matches: int = 100

class CreateFileRequest(BaseModel):
    path: str = Field(..., min_length=1)
    content: str = ""


class UpdateFileRequest(BaseModel):
    path: str
    content: str


class ReplaceTextRequest(BaseModel):
    path: str = ""
    old_text: str = Field(..., min_length=1)
    new_text: str = ""