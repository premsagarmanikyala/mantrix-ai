"""
Pydantic models for request/response schemas.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# User schemas
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str
    full_name: str
    bio: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""
    pass


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Project schemas
class ProjectBase(BaseModel):
    """Base project schema."""
    title: str
    description: Optional[str] = None
    status: str = "active"
    priority: str = "medium"


class ProjectCreate(ProjectBase):
    """Project creation schema."""
    owner_id: int


class ProjectUpdate(BaseModel):
    """Project update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Project response schema."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# AI/Resume schemas
class ResumeGenerateRequest(BaseModel):
    """Resume generation request schema."""
    user_id: int
    template_style: str = "modern"
    include_projects: bool = True


class RoadmapGenerateRequest(BaseModel):
    """Roadmap generation request schema."""
    project_id: int
    skill_level: str = "beginner"  # beginner, intermediate, advanced
    timeframe: str = "3_months"  # 1_month, 3_months, 6_months, 1_year