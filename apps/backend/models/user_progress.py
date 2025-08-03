"""
User progress tracking models for roadmap completion.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ModuleProgress(BaseModel):
    """Individual module completion status."""
    module_id: str = Field(..., description="Unique identifier for the module")
    branch_id: str = Field(..., description="Branch containing this module")
    roadmap_id: str = Field(..., description="Roadmap containing this branch")
    completed_at: datetime = Field(..., description="When the module was completed")
    duration_completed: int = Field(..., description="Duration of completed module in seconds")


class UserProgress(BaseModel):
    """User's overall progress across roadmaps."""
    user_id: str = Field(..., description="User identifier")
    completed_modules: List[ModuleProgress] = Field(default=[], description="List of completed modules")
    total_study_time: int = Field(default=0, description="Total study time in seconds")
    roadmaps_started: List[str] = Field(default=[], description="List of roadmap IDs user has started")
    last_activity: Optional[datetime] = Field(None, description="Last progress update timestamp")


class ProgressUpdateRequest(BaseModel):
    """Request to update user's progress."""
    module_id: str = Field(..., description="Module ID being completed")
    branch_id: str = Field(..., description="Branch ID containing the module")
    roadmap_id: str = Field(..., description="Roadmap ID containing the branch")


class ProgressResponse(BaseModel):
    """Response with user's progress statistics."""
    user_id: str = Field(..., description="User identifier")
    total_modules_completed: int = Field(..., description="Total number of completed modules")
    total_study_time: int = Field(..., description="Total study time in seconds")
    roadmaps_in_progress: int = Field(..., description="Number of roadmaps currently being studied")
    completion_percentage: Dict[str, float] = Field(default={}, description="Completion percentage per roadmap")
    recent_activity: List[ModuleProgress] = Field(default=[], description="Recent module completions")