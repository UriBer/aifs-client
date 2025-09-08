"""
User and authentication models.
"""

from sqlalchemy import Column, String, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    id = Column(String(255), primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    preferences = Column(JSON, nullable=True)  # User preferences and settings
    
    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}', email='{self.email}')>"


class APIKey(Base):
    """API key model for API authentication."""
    
    __tablename__ = "api_keys"
    
    id = Column(String(255), primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    key_hash = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    permissions = Column(JSON, nullable=True)  # API key permissions
    
    def __repr__(self):
        return f"<APIKey(id='{self.id}', name='{self.name}', user_id='{self.user_id}')>"
