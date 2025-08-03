"""
API endpoints for learning path recommendations.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from core.database import get_db
from middleware.auth_guard import get_current_user
from services.recommendation_service import RecommendationService
from models.recommendation import RecommendationRequest, RecommendationResponse

# Configure logging
logger = logging.getLogger(__name__)

# Create router
recommendation_router = APIRouter(prefix="/roadmap", tags=["recommendations"])

# Initialize service
recommendation_service = RecommendationService()


@recommendation_router.post("/recommend", response_model=RecommendationResponse)
async def generate_learning_recommendations(
    request: RecommendationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> RecommendationResponse:
    """
    Generate personalized learning path recommendations based on user progress and goals.
    
    **Features:**
    - Gap analysis for target job roles
    - Resume enhancement suggestions
    - Interest-based learning paths
    - AI-powered recommendations using GPT-4
    - Fallback system for reliability
    
    **Modes:**
    - `gap`: Analyze skills needed for target job description
    - `resume`: Suggest improvements to enhance resume/profile
    - `interest`: Recommend paths based on user interests
    
    **Returns:**
    - Personalized learning branch recommendations
    - Detailed module breakdowns with durations
    - Analysis summary and confidence score
    - Actionable next steps
    """
    try:
        user_id = str(current_user.get("user_id") or current_user.get("id") or current_user.get("sub"))
        logger.info(f"Generating {request.mode} recommendations for user {user_id}")
        
        # Validate request parameters
        if request.mode == "gap" and not request.target_job_description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="target_job_description is required for gap analysis mode"
            )
        
        if request.mode == "resume" and not request.existing_resume:
            logger.warning("Resume mode requested without resume content - using profile analysis")
        
        # Generate recommendations
        recommendations = recommendation_service.generate_recommendations(
            db=db,
            user_id=user_id,
            request=request
        )
        
        logger.info(f"Generated {len(recommendations.recommendations)} recommendations with {recommendations.confidence_score:.2f} confidence")
        
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@recommendation_router.get("/recommend/health")
async def recommendation_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for recommendation service.
    
    **Returns:**
    - Service status and capabilities
    - AI integration status
    - Available recommendation modes
    - Feature availability
    """
    try:
        # Check OpenAI availability
        import os
        openai_available = bool(os.getenv("OPENAI_API_KEY"))
        
        return {
            "status": "healthy",
            "service": "Learning Path Recommendations",
            "version": "1.0.0",
            "ai_integration": "OpenAI GPT-4" if openai_available else "Fallback system",
            "modes": ["gap", "interest", "resume"],
            "features": [
                "AI-powered recommendations",
                "Skill gap analysis",
                "Resume enhancement suggestions",
                "Interest-based paths",
                "Confidence scoring",
                "Fallback system"
            ],
            "capabilities": {
                "job_description_analysis": True,
                "resume_analysis": True,
                "user_progress_integration": True,
                "multi_mode_recommendations": True,
                "duration_estimation": True,
                "prerequisite_tracking": True
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "degraded",
            "error": str(e),
            "service": "Learning Path Recommendations"
        }