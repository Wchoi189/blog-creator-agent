"""Blog generation data models"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class BlogStatus(str, Enum):
    """Blog draft status"""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    PUBLISHED = "published"
    FAILED = "failed"


class BlogGenerateRequest(BaseModel):
    """Request to generate a blog post"""
    document_ids: List[str] = Field(..., description="Document IDs to use as source")
    title: Optional[str] = Field(None, description="Blog post title")
    instructions: Optional[str] = Field(None, description="Additional instructions for generation")
    categories: Optional[List[str]] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)


class BlogRefineRequest(BaseModel):
    """Request to refine a blog draft"""
    feedback: str = Field(..., description="User feedback for refinement")


class BlogDraft(BaseModel):
    """Blog draft model"""
    id: str
    user_id: str
    session_id: str
    title: str
    content: str
    status: BlogStatus
    version: int = 1
    document_ids: List[str]
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    published_url: Optional[str] = None

    class Config:
        from_attributes = True


class BlogDraftUpdate(BaseModel):
    """Update blog draft"""
    title: Optional[str] = None
    content: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class BlogExportRequest(BaseModel):
    """Request to export blog"""
    format: str = Field("markdown", description="Export format (markdown, html)")


class BlogPublishRequest(BaseModel):
    """Request to publish blog to GitHub"""
    repository: str = Field(..., description="GitHub repository (owner/repo)")
    branch: str = Field("main", description="Git branch")
    path: Optional[str] = Field("_posts", description="Path in repository")


class BlogPublishResponse(BaseModel):
    """Blog publish response"""
    success: bool
    published_url: str
    commit_sha: str
    filename: str
