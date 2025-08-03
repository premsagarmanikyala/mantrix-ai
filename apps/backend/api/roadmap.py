"""
Roadmap generation API endpoints.
"""

import logging
import uuid
from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import ValidationError
from sqlalchemy.orm import Session

from models.roadmap import (
    RoadmapGenerateRequest, RoadmapGenerateResponse, RoadmapResponse,
    RoadmapCustomizeRequest, RoadmapCustomizeResponse
)
from services.roadmap_agent import roadmap_agent
from services.sync_roadmap_service import SyncRoadmapService
from middleware.auth_guard import get_current_user_id, get_current_user
from core.database import get_db

# Configure logging
logger = logging.getLogger(__name__)

# Create router for roadmap endpoints
roadmap_router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@roadmap_router.post("/generate", response_model=RoadmapGenerateResponse)
async def generate_roadmap(
    request: RoadmapGenerateRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> RoadmapGenerateResponse:
    """
    Generate AI-powered learning roadmaps based on user input.
    
    This endpoint uses OpenAI GPT-4 and LangChain to generate 2-3 structured 
    learning roadmaps with branches and video modules.
    
    Args:
        request: Request containing user_input and mode
        
    Returns:
        RoadmapGenerateResponse with generated roadmaps
        
    Raises:
        HTTPException: If roadmap generation fails
    """
    try:
        logger.info(f"Generating roadmaps for input: {request.user_input[:50]}...")
        
        # Validate input
        if not request.user_input.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User input cannot be empty"
            )
        
        # Generate roadmaps using AI agent
        try:
            roadmaps, branches_library = roadmap_agent.generate_roadmaps(request.user_input)
        except Exception as ai_error:
            logger.error(f"AI roadmap generation failed: {str(ai_error)}")
            
            # Try fallback generation
            try:
                logger.warning("Attempting fallback roadmap generation")
                roadmaps, branches_library = roadmap_agent._generate_fallback_roadmaps(request.user_input)
            except Exception as fallback_error:
                logger.error(f"Fallback generation also failed: {str(fallback_error)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Roadmap generation failed: {str(ai_error)}"
                )
        
        # Validate response
        if not roadmaps or len(roadmaps) < 2:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate minimum required roadmaps"
            )
        
        # Save roadmaps to database with authenticated user ID
        try:
            saved_ids = SyncRoadmapService.save_roadmaps(db, roadmaps, current_user_id)
            logger.info(f"Saved roadmaps to database for user {current_user_id} with IDs: {saved_ids}")
        except Exception as save_error:
            logger.error(f"Failed to save roadmaps to database: {str(save_error)}")
            # Continue without failing the request - roadmaps are still generated
        
        # Create response
        response = RoadmapGenerateResponse(
            roadmaps=roadmaps,
            user_input=request.user_input,
            mode=request.mode,
            branches_library=branches_library,
            status="success"
        )
        
        logger.info(f"Successfully generated {len(roadmaps)} roadmaps")
        return response
        
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request data: {str(e)}"
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in roadmap generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during roadmap generation"
        )


@roadmap_router.get("/health")
async def roadmap_health_check():
    """Health check for roadmap service."""
    try:
        # Test OpenAI API key availability
        api_key_available = bool(roadmap_agent.api_key)
        
        return {
            "status": "healthy",
            "service": "roadmap-generator",
            "ai_enabled": api_key_available,
            "model": "gpt-4o"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "roadmap-generator",
            "error": str(e)
        }


@roadmap_router.get("/my-roadmaps", response_model=List[RoadmapResponse])
async def get_my_roadmaps(
    limit: int = 50,
    offset: int = 0,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> List[RoadmapResponse]:
    """
    Retrieve all roadmaps for the authenticated user.
    
    Args:
        limit: Maximum number of roadmaps to return (default: 50)
        offset: Number of roadmaps to skip (default: 0)
        current_user_id: Authenticated user ID from token
        db: Database session
        
    Returns:
        List of roadmap responses
        
    Raises:
        HTTPException: If database operation fails
    """
    try:
        logger.info(f"Fetching roadmaps for authenticated user: {current_user_id}")
        
        roadmaps = SyncRoadmapService.get_roadmaps_by_user(
            db=db,
            user_id=current_user_id,
            limit=limit,
            offset=offset
        )
        
        logger.info(f"Found {len(roadmaps)} roadmaps for user {current_user_id}")
        return roadmaps
        
    except Exception as e:
        logger.error(f"Error fetching roadmaps for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch roadmaps: {str(e)}"
        )


@roadmap_router.get("/id/{roadmap_id}", response_model=RoadmapResponse)
async def get_roadmap_by_id(
    roadmap_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> RoadmapResponse:
    """
    Retrieve a specific roadmap by ID (only if owned by authenticated user).
    
    Args:
        roadmap_id: Roadmap ID to fetch
        current_user_id: Authenticated user ID from token
        db: Database session
        
    Returns:
        Roadmap response
        
    Raises:
        HTTPException: If roadmap not found or access denied
    """
    try:
        roadmap = SyncRoadmapService.get_roadmap_by_id(
            db=db,
            roadmap_id=roadmap_id,
            user_id=current_user_id  # Enforce ownership check
        )
        
        if not roadmap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Roadmap not found or access denied"
            )
        
        return roadmap
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching roadmap {roadmap_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch roadmap: {str(e)}"
        )


@roadmap_router.delete("/id/{roadmap_id}")
async def delete_roadmap(
    roadmap_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a roadmap by ID (only if owned by authenticated user).
    
    Args:
        roadmap_id: Roadmap ID to delete
        current_user_id: Authenticated user ID from token
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If roadmap not found or access denied
    """
    try:
        success = SyncRoadmapService.delete_roadmap(
            db=db,
            roadmap_id=roadmap_id,
            user_id=current_user_id  # Enforce ownership check
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Roadmap not found or access denied"
            )
        
        return {"message": "Roadmap deleted successfully"}
    
    except Exception as e:
        logger.error(f"Error deleting roadmap {roadmap_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete roadmap: {str(e)}"
        )


@roadmap_router.post("/customize", response_model=RoadmapCustomizeResponse)
async def customize_roadmap(
    request: RoadmapCustomizeRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> RoadmapCustomizeResponse:
    """
    Create a custom roadmap by selecting specific branches from existing roadmaps.
    
    Args:
        request: Request containing title, branch_ids, and optional customized_from
        current_user_id: Authenticated user ID from token
        db: Database session
        
    Returns:
        RoadmapCustomizeResponse with the customized roadmap
        
    Raises:
        HTTPException: If customization fails
    """
    try:
        logger.info(f"Customizing roadmap for user {current_user_id} with {len(request.branch_ids)} branches")
        
        # Get all user's roadmaps to find matching branches
        user_roadmaps = SyncRoadmapService.get_roadmaps_by_user(db, current_user_id, limit=100)
        
        if not user_roadmaps:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No roadmaps found for user. Generate roadmaps first."
            )
        
        # Find branches by IDs
        selected_branches = []
        total_duration = 0
        
        for roadmap in user_roadmaps:
            for branch in roadmap.branches:
                if branch.id in request.branch_ids:
                    selected_branches.append(branch)
                    # Calculate total duration from branch videos
                    branch_duration = sum(video.duration for video in branch.videos)
                    total_duration += branch_duration
        
        if not selected_branches:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matching branches found for the provided IDs"
            )
        
        if len(selected_branches) != len(request.branch_ids):
            missing_ids = set(request.branch_ids) - {branch.id for branch in selected_branches}
            logger.warning(f"Some branch IDs not found: {missing_ids}")
        
        # Create custom roadmap
        custom_roadmap = RoadmapResponse(
            id=f"custom_roadmap_{uuid.uuid4().hex[:8]}",
            title=request.title,
            total_duration=total_duration,
            branches=selected_branches,
            customized_from=request.customized_from
        )
        
        # Save custom roadmap to database
        try:
            saved_ids = SyncRoadmapService.save_roadmaps(db, [custom_roadmap], current_user_id)
            logger.info(f"Saved custom roadmap to database with ID: {saved_ids[0]}")
            
            # Update the roadmap ID to match the saved ID
            custom_roadmap.id = saved_ids[0]
            
        except Exception as save_error:
            logger.error(f"Failed to save custom roadmap: {str(save_error)}")
            # Continue without failing - roadmap is still created
        
        # Create response
        response = RoadmapCustomizeResponse(
            roadmap=custom_roadmap,
            status="success",
            message=f"Custom roadmap '{request.title}' created with {len(selected_branches)} branches"
        )
        
        logger.info(f"Successfully customized roadmap: {request.title}")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error customizing roadmap: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to customize roadmap: {str(e)}"
        )