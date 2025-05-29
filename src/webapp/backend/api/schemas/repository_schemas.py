from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
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
    
    # 🆕 Additional fields for frontend compatibility
    cached_path: Optional[str] = None
    last_commit_hash: Optional[str] = None
    cache_expires_at: Optional[datetime] = None
    cache_size_mb: Optional[int] = None
    auto_sync_enabled: bool = True
    
    class Config:
        from_attributes = True

class RepositoryListResponse(BaseModel):
    """Response schema for repository list with summary statistics."""
    repositories: List[RepositoryResponse]
    total_count: int
    summary: dict = Field(default_factory=dict, description="Summary statistics about repositories")

class RepositoryErrorResponse(BaseModel):
    detail: str 