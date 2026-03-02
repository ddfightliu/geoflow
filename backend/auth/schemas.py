"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    email: Optional[EmailStr] = None
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""
    provider: str
    provider_id: str


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    provider: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[int] = None
    username: Optional[str] = None


class OAuthCallback(BaseModel):
    """Schema for OAuth callback."""
    code: str
    state: Optional[str] = None


class OAuthRedirect(BaseModel):
    """Schema for OAuth redirect response."""
    authorization_url: str


class MessageResponse(BaseModel):
    """Schema for generic message response."""
    message: str
    success: bool = True


class ProviderList(BaseModel):
    """Schema for listing available OAuth providers."""
    providers: List[dict]

