from pydantic import BaseModel
from typing import Any, Dict, List


class RunFileRequest(BaseModel):
    path: str = ""


class ProjectPathRequest(BaseModel):
    path: str = "."

class IdeChatRequest(BaseModel):
    user_question: str
    chat_history: List[Dict[str, Any]] = []