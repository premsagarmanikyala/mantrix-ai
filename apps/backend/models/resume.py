"""
Resume generation and analysis models.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class ResumeGenerateRequest(BaseModel):
    """Request schema for resume generation."""
    mode: Literal["study", "fast", "analyzer"] = Field(..., description="Resume generation mode")
    roadmap_id: Optional[str] = Field(None, description="Roadmap ID for study/fast modes")
    completed_modules: Optional[List[str]] = Field(None, description="List of completed module IDs for study mode")
    existing_resume: Optional[str] = Field(None, description="Existing resume text for analyzer mode")
    job_description: Optional[str] = Field(None, description="Job description for analyzer mode")
    user_profile: Optional[Dict[str, Any]] = Field(None, description="Optional user profile information")


class ResumeAnalysis(BaseModel):
    """Analysis results for analyzer mode."""
    ats_score: int = Field(..., description="ATS compatibility score (0-100)", ge=0, le=100)
    keyword_match_score: int = Field(..., description="Keyword matching score (0-100)", ge=0, le=100)
    missing_skills: List[str] = Field(default=[], description="Skills missing from resume but required by job")
    recommended_modules: List[str] = Field(default=[], description="Recommended roadmap modules to improve match")
    strengths: List[str] = Field(default=[], description="Resume strengths identified")
    improvement_areas: List[str] = Field(default=[], description="Areas for improvement")


class GeneratedResume(BaseModel):
    """Generated resume content."""
    id: str = Field(..., description="Unique resume identifier")
    user_id: str = Field(..., description="User identifier")
    mode: str = Field(..., description="Generation mode used")
    roadmap_id: Optional[str] = Field(None, description="Source roadmap ID")
    resume_text: str = Field(..., description="Generated resume content")
    skills_included: List[str] = Field(default=[], description="Skills included in resume")
    modules_used: List[str] = Field(default=[], description="Modules used for generation")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    is_draft: bool = Field(default=True, description="Whether this is a draft or final version")


class ResumeGenerateResponse(BaseModel):
    """Response schema for resume generation."""
    resume: GeneratedResume = Field(..., description="Generated resume data")
    analysis: Optional[ResumeAnalysis] = Field(None, description="Analysis results for analyzer mode")
    status: str = Field(default="success", description="Generation status")
    message: str = Field(default="Resume generated successfully", description="Status message")


class SavedResume(BaseModel):
    """Saved resume in database."""
    id: str = Field(..., description="Resume identifier")
    user_id: str = Field(..., description="User identifier")
    title: str = Field(..., description="Resume title/name")
    mode: str = Field(..., description="Generation mode")
    roadmap_id: Optional[str] = Field(None, description="Source roadmap ID")
    content: str = Field(..., description="Resume content")
    job_description: Optional[str] = Field(None, description="Associated job description")
    analysis_data: Optional[Dict[str, Any]] = Field(None, description="Analysis results JSON")
    is_draft: bool = Field(default=True, description="Draft status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ResumeListResponse(BaseModel):
    """Response for listing user's saved resumes."""
    resumes: List[SavedResume] = Field(..., description="List of user's resumes")
    total_count: int = Field(..., description="Total number of resumes")
    study_mode_count: int = Field(default=0, description="Number of study mode resumes")
    fast_mode_count: int = Field(default=0, description="Number of fast mode resumes")
    analyzer_mode_count: int = Field(default=0, description="Number of analyzer mode resumes")