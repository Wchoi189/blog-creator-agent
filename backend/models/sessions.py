"""Session data models"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    """Create session request"""
    name: Optional[str] = Field(None, description="Session name")
    llm_provider: str = Field("openai", description="LLM provider (openai, ollama)")
    llm_model: str = Field("gpt-4-turbo-preview", description="LLM model")


class Session(BaseModel):
    """Session model"""
    id: str
    user_id: str
    name: str
    llm_provider: str
    llm_model: str
    created_at: datetime
    updated_at: datetime
    document_ids: List[str] = Field(default_factory=list)
    draft_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class SessionList(BaseModel):
    """List of sessions"""
    sessions: List[Session]
    total: int


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatHistory(BaseModel):
    """Chat history for a session"""
    session_id: str
    messages: List[ChatMessage]
