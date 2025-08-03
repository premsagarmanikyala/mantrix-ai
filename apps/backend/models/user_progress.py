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


# New models for dedicated Progress Tracker API
class ProgressCompleteRequest(BaseModel):
    """Request model for marking a module as completed."""
    module_id: str = Field(..., description="Unique identifier for the completed module")
    branch_id: str = Field(..., description="Branch containing the module")
    roadmap_id: str = Field(..., description="Roadmap containing the branch")
    duration_completed: Optional[int] = Field(0, description="Time spent on module in seconds")


class UserProgressEntry(BaseModel):
    """Model representing a user's progress on a specific module."""
    id: str
    user_id: str
    roadmap_id: str
    branch_id: str
    module_id: str
    completed_at: datetime
    duration_completed: int  # in seconds
    
    class Config:
        from_attributes = True


class BranchProgressSummary(BaseModel):
    """Progress summary for a specific branch."""
    branch_id: str = Field(..., description="Unique identifier for the branch")
    completed: int = Field(..., description="Number of completed modules in branch")
    total: int = Field(..., description="Total number of modules in branch")
    duration_done: int = Field(..., description="Total completed duration in seconds")
    duration_total: int = Field(..., description="Total expected duration in seconds")
    progress_percent: float = Field(..., description="Branch completion percentage")
    
    class Config:
        from_attributes = True


class ProgressSummaryResponse(BaseModel):
    """Comprehensive progress summary for a roadmap."""
    roadmap_id: str = Field(..., description="Roadmap identifier")
    total_modules: int = Field(..., description="Total number of modules in roadmap")
    completed_modules: int = Field(..., description="Number of completed modules")
    total_duration: int = Field(..., description="Total expected duration in seconds")
    completed_duration: int = Field(..., description="Total completed duration in seconds")
    progress_percent: float = Field(..., description="Overall completion percentage")
    branches: List[BranchProgressSummary] = Field(default=[], description="Branch-level progress details")
    last_activity: Optional[datetime] = Field(None, description="Timestamp of last progress update")
    
    class Config:
        from_attributes = True