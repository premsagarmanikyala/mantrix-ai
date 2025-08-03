"""
Resume builder API endpoints supporting study, fast, and analyzer modes.
"""

import logging
import uuid
from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import ValidationError
from sqlalchemy.orm import Session

from models.resume import (
    ResumeGenerateRequest, ResumeGenerateResponse,
    ResumeListResponse
)
from models.user_progress import ProgressUpdateRequest, ProgressResponse
from services.resume_service import resume_service
from services.progress_service import ProgressService
from middleware.auth_guard import get_current_user_id
from core.database import get_db

# Configure logging
logger = logging.getLogger(__name__)

# Create router for resume endpoints
resume_router = APIRouter(prefix="/resume", tags=["resume"])


@resume_router.post("/generate", response_model=ResumeGenerateResponse)
async def generate_resume(
    request: ResumeGenerateRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> ResumeGenerateResponse:
    """
    Generate resume based on mode: study (completed modules only), 
    fast (full roadmap), or analyzer (resume + job description analysis).
    
    Args:
        request: Resume generation request with mode and parameters
        current_user_id: Authenticated user ID from token
        db: Database session
        
    Returns:
        Generated resume with optional analysis
        
    Raises:
        HTTPException: If generation fails or invalid parameters
    """
    try:
        logger.info(f"Generating resume for user {current_user_id} in {request.mode} mode")
        
        # Validate mode-specific requirements
        if request.mode in ["study", "fast"] and not request.roadmap_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{request.mode} mode requires roadmap_id"
            )
        
        if request.mode == "analyzer":
            if not request.existing_resume or not request.job_description:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Analyzer mode requires existing_resume and job_description"
                )
        
        # Initialize progress tracking tables
        ProgressService.initialize_progress_table(db)
        
        # Generate resume using service
        response = resume_service.generate_resume(db, current_user_id, request)
        
        logger.info(f"Successfully generated {request.mode} mode resume for user {current_user_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume generation failed: {str(e)}"
        )


@resume_router.get("/my-resumes", response_model=ResumeListResponse)
async def get_user_resumes(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> ResumeListResponse:
    """
    Get all resumes for the authenticated user.
    
    Args:
        current_user_id: Authenticated user ID from token
        db: Database session
        
    Returns:
        List of user's saved resumes with statistics
    """
    try:
        logger.info(f"Fetching resumes for user {current_user_id}")
        
        resumes = resume_service.get_user_resumes(db, current_user_id)
        
        logger.info(f"Retrieved {resumes.total_count} resumes for user {current_user_id}")
        return resumes
        
    except Exception as e:
        logger.error(f"Error fetching user resumes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch resumes: {str(e)}"
        )


@resume_router.post("/progress/complete", response_model=dict)
async def mark_module_complete(
    request: ProgressUpdateRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> dict:
    """
    Mark a module as completed for progress tracking.
    
    Args:
        request: Module completion request
        current_user_id: Authenticated user ID from token
        db: Database session
        
    Returns:
        Success confirmation
    """
    try:
        logger.info(f"Marking module {request.module_id} complete for user {current_user_id}")
        
        # Initialize progress table
        ProgressService.initialize_progress_table(db)
        
        # Mark module as completed
        success = ProgressService.mark_module_complete(
            db=db,
            user_id=current_user_id,
            module_id=request.module_id,
            branch_id=request.branch_id,
            roadmap_id=request.roadmap_id,
            duration=600  # Default 10 minutes - could be extracted from roadmap
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to mark module as completed"
            )
        
        return {
            "message": f"Module {request.module_id} marked as completed",
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking module complete: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update progress: {str(e)}"
        )


@resume_router.get("/progress", response_model=ProgressResponse)
async def get_user_progress(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> ProgressResponse:
    """
    Get comprehensive progress information for the authenticated user.
    
    Args:
        current_user_id: Authenticated user ID from token
        db: Database session
        
    Returns:
        User's learning progress statistics
    """
    try:
        logger.info(f"Fetching progress for user {current_user_id}")
        
        # Initialize progress table
        ProgressService.initialize_progress_table(db)
        
        progress = ProgressService.get_user_progress(db, current_user_id)
        
        logger.info(f"Retrieved progress for user {current_user_id}: {progress.total_modules_completed} modules completed")
        return progress
        
    except Exception as e:
        logger.error(f"Error fetching user progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch progress: {str(e)}"
        )


@resume_router.get("/health")
async def resume_health_check():
    """Health check endpoint for resume service."""
    return {
        "status": "healthy",
        "service": "resume_builder",
        "modes_supported": ["study", "fast", "analyzer"],
        "features": [
            "AI-powered resume generation",
            "Progress-based content filtering",
            "ATS resume analysis",
            "Job description matching"
        ]
    }