from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

class AddRepositoryRequest(BaseModel):
    repo_url: HttpUrl = Field(..., description="Repository URL (GitHub, GitLab, ...)")
    access_token: Optional[str] = Field(None, description="Personal Access Token (nếu repo là private)")

class RepositoryResponse(BaseModel):
    id: int
    name: str
    url: str
    description: Optional[str]
    avatar_url: Optional[str]
    language: Optional[str]
    default_branch: Optional[str]
    is_private: bool
    stars: Optional[int]
    forks: Optional[int]
    owner_id: int
    created_at: datetime
    updated_at: datetime
    last_synced_at: Optional[datetime]

class RepositoryErrorResponse(BaseModel):
    detail: str 