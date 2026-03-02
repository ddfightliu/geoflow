"""
Database models for user authentication.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from datetime import datetime
from backend.auth.database import Base


class User(Base):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    provider = Column(String, nullable=False)  # github, microsoft, feishu, wechat, alipay, douyin
    provider_id = Column(String, unique=True, index=True, nullable=False)  # OAuth provider user ID
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    extra_data = Column(JSON, nullable=True)  # Store additional provider-specific data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, provider={self.provider})>"

