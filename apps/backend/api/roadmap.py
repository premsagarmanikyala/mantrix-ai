"""
Roadmap generation API endpoints.
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from models.roadmap import RoadmapGenerateRequest, RoadmapGenerateResponse, RoadmapResponse
from services.roadmap_agent import roadmap_agent

# Configure logging
logger = logging.getLogger(__name__)

# Create router for roadmap endpoints
roadmap_router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@roadmap_router.post("/generate", response_model=RoadmapGenerateResponse)
async def generate_roadmap(request: RoadmapGenerateRequest) -> RoadmapGenerateResponse:
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
            roadmaps = roadmap_agent.generate_roadmaps(request.user_input)
        except Exception as ai_error:
            logger.error(f"AI roadmap generation failed: {str(ai_error)}")
            
            # Try fallback generation
            try:
                logger.warning("Attempting fallback roadmap generation")
                roadmaps = roadmap_agent._generate_fallback_roadmaps(request.user_input)
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
        
        # Create response
        response = RoadmapGenerateResponse(
            roadmaps=roadmaps,
            user_input=request.user_input,
            mode=request.mode
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