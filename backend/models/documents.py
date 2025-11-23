"""Document data models"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Supported document types"""
    PDF = "pdf"
    AUDIO = "audio"
    IMAGE = "image"
    MARKDOWN = "markdown"


class ProcessingStatus(str, Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentUpload(BaseModel):
    """Document upload response"""
    id: str
    filename: str
    file_type: DocumentType
    size: int
    status: ProcessingStatus = ProcessingStatus.PENDING


class DocumentMetadata(BaseModel):
    """Document metadata"""
    title: Optional[str] = None
    author: Optional[str] = None
    page_count: Optional[int] = None
    duration: Optional[float] = None  # For audio
    dimensions: Optional[tuple[int, int]] = None  # For images
    language: Optional[str] = None


class Document(BaseModel):
    """Document model"""
    id: str
    user_id: str
    filename: str
    file_type: DocumentType
    file_path: str
    size: int
    status: ProcessingStatus
    metadata: Optional[DocumentMetadata] = None
    chunk_count: Optional[int] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    """List of documents"""
    documents: List[Document]
    total: int


class DocumentSearch(BaseModel):
    """Document search request"""
    query: str = Field(..., description="Search query")
    document_ids: Optional[List[str]] = Field(None, description="Filter by document IDs")
    top_k: int = Field(5, description="Number of results to return")


class SearchResult(BaseModel):
    """Search result"""
    content: str
    document_id: str
    document_name: str
    score: float
    metadata: dict = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Search response"""
    results: List[SearchResult]
    total: int
