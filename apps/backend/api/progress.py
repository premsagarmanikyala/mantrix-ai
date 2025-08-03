"""
Progress Tracker API endpoints for learning module completion and analytics.

Provides comprehensive progress tracking with:
- Module completion recording with timestamps and durations
- Progress summaries with branch-level breakdowns
- Frontend-friendly data format for visualizations
- JWT-authenticated user data management
- PostgreSQL persistence with duplicate prevention
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from core.database import get_db
from middleware.auth_guard import get_current_user
from services.progress_service import ProgressService
from models.user_progress import ProgressCompleteRequest, ProgressSummaryResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
progress_router = APIRouter(tags=["progress"])

# Initialize service
progress_service = ProgressService()

@progress_router.post("/progress/complete")
async def complete_module_progress(
    request: ProgressCompleteRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a learning module as completed with duration tracking.
    
    Stores progress in user_progress table with:
    - Completion timestamp
    - Duration spent on module
    - Prevents duplicate entries
    - User ownership validation
    """
    try:
        user_id = str(current_user.get("user_id") or current_user.get("id") or current_user.get("sub"))
        logger.info(f"Recording progress completion for user {user_id}, module {request.module_id}")
        
        # Validate user ownership of roadmap
        if not progress_service.validate_user_roadmap_access(db, user_id, request.roadmap_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Roadmap does not belong to user"
            )
        
        # Record progress completion
        progress_entry = progress_service.complete_module(
            db=db,
            user_id=user_id,
            roadmap_id=request.roadmap_id,
            branch_id=request.branch_id,
            module_id=request.module_id,
            duration_completed=request.duration_completed
        )
        
        if progress_entry:
            logger.info(f"Successfully recorded progress for module {request.module_id}")
            return {
                "status": "success",
                "message": "Module progress recorded successfully",
                "progress_id": progress_entry.id,
                "completed_at": progress_entry.completed_at.isoformat(),
                "total_study_time": progress_entry.duration_completed
            }
        else:
            # Module already completed
            return {
                "status": "already_completed",
                "message": "Module was already marked as completed",
                "module_id": request.module_id
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording progress completion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record progress: {str(e)}"
        )

@progress_router.get("/progress/summary", response_model=ProgressSummaryResponse)
async def get_progress_summary(
    roadmap_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive progress summary for a roadmap.
    
    Returns frontend-friendly data including:
    - Total vs completed modules and durations
    - Progress percentage calculation
    - Branch-level progress breakdowns
    - Visualization-ready data format
    """
    try:
        user_id = str(current_user.get("user_id") or current_user.get("id") or current_user.get("sub"))
        logger.info(f"Generating progress summary for user {user_id}, roadmap {roadmap_id}")
        
        # Validate user ownership of roadmap
        if not progress_service.validate_user_roadmap_access(db, user_id, roadmap_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Roadmap does not belong to user"
            )
        
        # Generate comprehensive progress summary
        summary = progress_service.get_progress_summary(
            db=db,
            user_id=user_id,
            roadmap_id=roadmap_id
        )
        
        if summary:
            logger.info(f"Generated progress summary: {summary.completed_modules}/{summary.total_modules} modules")
            return summary
        else:
            # Return empty summary if no progress or roadmap found
            return ProgressSummaryResponse(
                roadmap_id=roadmap_id,
                total_modules=0,
                completed_modules=0,
                total_duration=0,
                completed_duration=0,
                progress_percent=0.0,
                branches=[]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating progress summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate progress summary: {str(e)}"
        )

@progress_router.get("/progress/health")
async def progress_health_check():
    """Health check endpoint for progress tracking service."""
    try:
        return {
            "status": "healthy",
            "service": "progress-tracker",
            "version": "1.0.0",
            "features": [
                "Module completion tracking",
                "Duration recording",
                "Progress summaries",
                "Branch-level analytics",
                "Duplicate prevention",
                "User ownership validation"
            ],
            "database": "PostgreSQL",
            "authentication": "JWT"
        }
    except Exception as e:
        logger.error(f"Progress service health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Progress service health check failed"
        )