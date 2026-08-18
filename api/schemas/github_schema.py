from pydantic import BaseModel, Field


class CreatePullRequestRequest(BaseModel):
    title: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    base: str = Field("master", min_length=1)


class EditPullRequestRequest(BaseModel):
    title: str | None = None
    body: str | None = None
