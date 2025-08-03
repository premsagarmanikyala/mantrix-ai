"""
Roadmap request and response schemas for the roadmap generation API.
"""

from typing import List, Literal
from pydantic import BaseModel, Field


class VideoModule(BaseModel):
    """Individual video module within a branch."""
    id: str = Field(..., description="Unique identifier for the video module")
    title: str = Field(..., description="Title of the video module")
    duration: int = Field(..., description="Duration in seconds", ge=300, le=1800)
    is_core: bool = Field(default=False, description="Whether this video is essential (core) or optional")


class RoadmapBranch(BaseModel):
    """Branch of learning content within a roadmap."""
    id: str = Field(..., description="Unique identifier for the branch")
    title: str = Field(..., description="Title of the learning branch")
    videos: List[VideoModule] = Field(..., description="List of video modules in this branch")


class RoadmapResponse(BaseModel):
    """Individual roadmap in the response."""
    id: str = Field(..., description="Unique identifier for the roadmap")
    title: str = Field(..., description="Title of the roadmap")
    total_duration: int = Field(..., description="Total duration of all videos in seconds")
    branches: List[RoadmapBranch] = Field(..., description="Learning branches in the roadmap")
    customized_from: str = Field(None, description="ID of the original roadmap if this is a customized version")


class RoadmapGenerateRequest(BaseModel):
    """Request schema for roadmap generation."""
    user_input: str = Field(..., description="User's input for roadmap generation", min_length=1)
    mode: Literal["full", "custom"] = Field(..., description="Generation mode: full or custom")


class RoadmapGenerateResponse(BaseModel):
    """Response schema for roadmap generation."""
    roadmaps: List[RoadmapResponse] = Field(..., description="List of generated roadmaps", min_items=2, max_items=3)
    user_input: str = Field(..., description="The original user input")
    mode: str = Field(..., description="The generation mode used")
    branches_library: List[RoadmapBranch] = Field(..., description="De-duplicated list of all branches across roadmaps")
    status: str = Field(default="success", description="Generation status")


class RoadmapCustomizeRequest(BaseModel):
    """Request schema for roadmap customization."""
    title: str = Field(..., description="Title for the custom roadmap", min_length=1)
    branch_ids: List[str] = Field(..., description="List of branch IDs to include in custom roadmap", min_items=1)
    customized_from: str = Field(None, description="Optional ID of the original roadmap being customized")


class RoadmapCustomizeResponse(BaseModel):
    """Response schema for roadmap customization."""
    roadmap: RoadmapResponse = Field(..., description="The customized roadmap")
    status: str = Field(default="success", description="Customization status")
    message: str = Field(default="Roadmap customized successfully", description="Status message")