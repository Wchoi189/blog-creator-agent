"""Authentication data models"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str


class User(UserBase):
    """User model (response)"""
    id: str
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # user_id
    type: str  # "access" or "refresh"
    exp: datetime


class APIKeyCreate(BaseModel):
    """API key creation model"""
    name: str = Field(..., description="Friendly name for the API key")
    expires_in_days: Optional[int] = Field(None, description="Days until expiration (null = never)")


class APIKey(BaseModel):
    """API key model (response)"""
    id: str
    name: str
    key: str  # Only shown once on creation
    key_prefix: str  # e.g., "bca_abc..."
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class APIKeyInfo(BaseModel):
    """API key info (without actual key)"""
    id: str
    name: str
    key_prefix: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True
