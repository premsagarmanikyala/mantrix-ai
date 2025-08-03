"""
API endpoints for roadmap merging and timeline planning
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from middleware.auth import get_current_user
from services.merge_service import RoadmapMergeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/roadmap", tags=["roadmap-merge"])

# Initialize service
merge_service = RoadmapMergeService()


# Request/Response Models
class MergeRequest(BaseModel):
    roadmap_ids: List[str] = Field(..., min_items=2, description="List of roadmap IDs to merge")
    schedule_mode: str = Field(default="none", description="Scheduling mode: none, auto, or manual")
    calendar_view: bool = Field(default=False, description="Generate calendar timeline")
    daily_study_hours: float = Field(default=1.0, ge=0.5, le=8.0, description="Daily study hours for auto scheduling")

class MergePreviewRequest(BaseModel):
    roadmap_ids: List[str] = Field(..., min_items=2, description="List of roadmap IDs to preview merge")

class RoadmapSummary(BaseModel):
    id: str
    title: str
    description: str
    estimatedDuration: int
    branchCount: int

class MergeStatistics(BaseModel):
    original_roadmaps: int
    original_duration: int
    final_duration: int
    duration_saved: int
    original_branches: int
    final_branches: int
    efficiency_gain: float

class MergePreviewResponse(BaseModel):
    preview: Dict[str, Any]
    statistics: MergeStatistics

class MergeResponse(BaseModel):
    merged_roadmap: Dict[str, Any]
    source_count: int
    schedule_mode: str
    calendar_enabled: bool


@router.post("/merge", response_model=MergeResponse)
async def merge_roadmaps(
    request: MergeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Merge multiple roadmaps into one unified roadmap with optional scheduling
    
    - **roadmap_ids**: List of roadmap IDs to merge (minimum 2)
    - **schedule_mode**: "none", "auto", or "manual" scheduling
    - **calendar_view**: Whether to generate calendar timeline
    - **daily_study_hours**: Hours per day for auto scheduling (0.5-8.0)
    
    Returns merged roadmap with deduplication and intelligent scheduling
    """
    
    try:
        user_id = current_user["sub"]
        logger.info(f"User {user_id} merging roadmaps: {request.roadmap_ids}")
        
        # Validate schedule mode
        valid_modes = ["none", "auto", "manual"]
        if request.schedule_mode not in valid_modes:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid schedule_mode. Must be one of: {valid_modes}"
            )
        
        # Perform merge
        result = merge_service.merge_roadmaps(
            roadmap_ids=request.roadmap_ids,
            user_id=user_id,
            schedule_mode=request.schedule_mode,
            calendar_view=request.calendar_view,
            daily_study_hours=request.daily_study_hours
        )
        
        logger.info(f"Successfully merged {result['source_count']} roadmaps for user {user_id}")
        return result
        
    except ValueError as e:
        logger.warning(f"Validation error in merge: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error merging roadmaps: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to merge roadmaps")


@router.post("/merge/preview", response_model=MergePreviewResponse)
async def preview_merge(
    request: MergePreviewRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Preview what a roadmap merge would look like without saving
    
    - **roadmap_ids**: List of roadmap IDs to preview merge
    
    Returns preview of merged roadmap with statistics
    """
    
    try:
        user_id = current_user["sub"]
        logger.info(f"User {user_id} previewing merge of roadmaps: {request.roadmap_ids}")
        
        # Generate preview
        result = merge_service.get_merge_preview(
            roadmap_ids=request.roadmap_ids,
            user_id=user_id
        )
        
        return result
        
    except ValueError as e:
        logger.warning(f"Validation error in merge preview: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating merge preview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate merge preview")


@router.get("/mergeable", response_model=List[RoadmapSummary])
async def get_mergeable_roadmaps(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's roadmaps that are available for merging
    
    Returns list of roadmaps that can be merged (excludes already merged roadmaps)
    """
    
    try:
        user_id = current_user["sub"]
        logger.info(f"Fetching mergeable roadmaps for user {user_id}")
        
        roadmaps = merge_service.get_user_roadmaps_for_merge(user_id)
        
        return roadmaps
        
    except Exception as e:
        logger.error(f"Error fetching mergeable roadmaps: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch mergeable roadmaps")


@router.get("/merge/health")
async def merge_health_check():
    """
    Health check endpoint for merge service
    """
    
    try:
        # Test service initialization
        test_service = RoadmapMergeService()
        
        return {
            "status": "healthy",
            "service": "roadmap_merge",
            "capabilities": [
                "intelligent_branch_deduplication",
                "auto_scheduling",
                "calendar_timeline_generation",
                "merge_preview",
                "lineage_tracking"
            ],
            "supported_schedule_modes": ["none", "auto", "manual"],
            "max_daily_study_hours": 8.0,
            "max_merge_sources": 10
        }
        
    except Exception as e:
        logger.error(f"Merge service health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Merge service unhealthy")