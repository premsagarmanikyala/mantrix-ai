"""
Data models for learning path recommendation system.
"""

from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Request model for learning path recommendations."""
    mode: Literal["gap", "interest", "resume"] = Field(..., description="Recommendation mode")
    existing_resume: Optional[str] = Field(None, description="User's current resume content")
    target_job_description: Optional[str] = Field(None, description="Target job description for gap analysis")
    skill_interests: Optional[List[str]] = Field(default=[], description="User's skill interests")
    career_level: Optional[str] = Field("intermediate", description="User's career level")
    
    class Config:
        from_attributes = True


class RecommendedModule(BaseModel):
    """Model for a recommended learning module."""
    title: str = Field(..., description="Module title")
    duration: int = Field(..., description="Expected duration in seconds")
    difficulty: str = Field("intermediate", description="Module difficulty level")
    priority: int = Field(1, description="Priority level (1=high, 3=low)")
    
    class Config:
        from_attributes = True


class RecommendedBranch(BaseModel):
    """Model for a recommended learning branch/path."""
    id: str = Field(..., description="Unique branch identifier")
    title: str = Field(..., description="Branch title")
    reason: str = Field(..., description="Why this branch is recommended")
    estimated_duration: int = Field(..., description="Total estimated duration in seconds")
    difficulty: str = Field("intermediate", description="Branch difficulty level")
    prerequisites: List[str] = Field(default=[], description="Required prerequisites")
    modules: List[RecommendedModule] = Field(..., description="Recommended modules in this branch")
    completion_benefit: str = Field(..., description="What user will gain from completing this")
    
    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """Response model for learning path recommendations."""
    user_id: str = Field(..., description="User identifier")
    mode: str = Field(..., description="Recommendation mode used")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    recommendations: List[RecommendedBranch] = Field(..., description="List of recommended branches")
    analysis_summary: str = Field(..., description="Summary of the analysis performed")
    confidence_score: float = Field(..., description="Confidence in recommendations (0-1)")
    next_steps: List[str] = Field(default=[], description="Suggested next steps for the user")
    
    class Config:
        from_attributes = True


class UserSkillProfile(BaseModel):
    """Model representing user's current skill profile."""
    completed_skills: List[str] = Field(default=[], description="Skills acquired from completed modules")
    in_progress_skills: List[str] = Field(default=[], description="Skills from ongoing modules")
    skill_levels: Dict[str, str] = Field(default={}, description="Skill proficiency levels")
    total_study_time: int = Field(0, description="Total study time in seconds")
    active_roadmaps: List[str] = Field(default=[], description="Currently active roadmap IDs")
    completion_rate: float = Field(0.0, description="Overall completion rate")
    
    class Config:
        from_attributes = True


class SkillGapAnalysis(BaseModel):
    """Model for skill gap analysis results."""
    required_skills: List[str] = Field(default=[], description="Skills required for target role")
    current_skills: List[str] = Field(default=[], description="Skills user currently has")
    missing_skills: List[str] = Field(default=[], description="Skills user needs to develop")
    skill_gaps: List[Dict[str, Any]] = Field(default=[], description="Detailed skill gap analysis")
    match_percentage: float = Field(0.0, description="Percentage match with target requirements")
    priority_areas: List[str] = Field(default=[], description="High-priority skill areas to focus on")
    
    class Config:
        from_attributes = True