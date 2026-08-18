from pydantic import BaseModel, Field


class GitCommitRequest(BaseModel):
    message: str = Field(..., min_length=1)


class GitPushRequest(BaseModel):
    branch_name: str | None = None


class GitCreateBranchRequest(BaseModel):
    branch_name: str = Field(..., min_length=1)
