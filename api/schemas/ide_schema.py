from pydantic import BaseModel


class RunFileRequest(BaseModel):
    path: str = ""


class ProjectPathRequest(BaseModel):
    path: str = "."