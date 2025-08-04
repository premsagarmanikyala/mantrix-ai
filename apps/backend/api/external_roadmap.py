"""
API endpoints for external roadmap sources integration.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel

from services.external_roadmap_service import external_roadmap_service, ExternalRoadmap, ExternalRoadmapSource

logger = logging.getLogger(__name__)

# Create router for external roadmap endpoints
external_roadmap_router = APIRouter(prefix="/external-roadmaps", tags=["external-roadmaps"])


class ExternalRoadmapSearchRequest(BaseModel):
    """Request model for searching external roadmaps."""
    query: str
    sources: Optional[List[str]] = None
    limit: Optional[int] = 10


class ExternalRoadmapSearchResponse(BaseModel):
    """Response model for external roadmap search."""
    roadmaps: List[ExternalRoadmap]
    query: str
    sources_searched: List[str]
    total_found: int
    status: str = "success"


@external_roadmap_router.get("/sources", response_model=List[ExternalRoadmapSource])
async def get_external_sources():
    """
    Get list of available external roadmap sources.
    
    Returns:
        List of external roadmap sources with their information
    """
    try:
        sources = await external_roadmap_service.get_available_sources()
        logger.info(f"Retrieved {len(sources)} external roadmap sources")
        return sources
        
    except Exception as e:
        logger.error(f"Error getting external sources: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get external sources: {str(e)}"
        )


@external_roadmap_router.get("/search", response_model=ExternalRoadmapSearchResponse)
async def search_external_roadmaps(
    query: str = Query(..., description="Search query for roadmaps"),
    sources: Optional[str] = Query(None, description="Comma-separated list of source IDs"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results")
):
    """
    Search for roadmaps across external sources.
    
    Args:
        query: Search query (e.g., "javascript", "python", "web development")
        sources: Optional comma-separated list of source IDs to search
        limit: Maximum number of results to return
        
    Returns:
        ExternalRoadmapSearchResponse with matching roadmaps
        
    Raises:
        HTTPException: If search fails
    """
    try:
        logger.info(f"Searching external roadmaps for query: {query}")
        
        # Parse sources parameter
        source_list = None
        if sources:
            source_list = [s.strip() for s in sources.split(",") if s.strip()]
        
        # Search roadmaps
        roadmaps = await external_roadmap_service.search_roadmaps(query, source_list)
        
        # Apply limit
        limited_roadmaps = roadmaps[:limit]
        
        # Get sources that were actually searched
        available_sources = await external_roadmap_service.get_available_sources()
        if source_list:
            sources_searched = [s for s in source_list if s in [src.id for src in available_sources]]
        else:
            sources_searched = [src.id for src in available_sources]
        
        response = ExternalRoadmapSearchResponse(
            roadmaps=limited_roadmaps,
            query=query,
            sources_searched=sources_searched,
            total_found=len(roadmaps)
        )
        
        logger.info(f"Found {len(roadmaps)} roadmaps, returning {len(limited_roadmaps)}")
        return response
        
    except Exception as e:
        logger.error(f"Error searching external roadmaps: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"External roadmap search failed: {str(e)}"
        )


@external_roadmap_router.post("/search", response_model=ExternalRoadmapSearchResponse)
async def search_external_roadmaps_post(request: ExternalRoadmapSearchRequest):
    """
    Search for roadmaps across external sources (POST method).
    
    Args:
        request: Search request with query and optional parameters
        
    Returns:
        ExternalRoadmapSearchResponse with matching roadmaps
        
    Raises:
        HTTPException: If search fails
    """
    try:
        logger.info(f"POST search for external roadmaps: {request.query}")
        
        # Validate request
        if not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
        
        # Search roadmaps
        roadmaps = await external_roadmap_service.search_roadmaps(
            request.query, 
            request.sources
        )
        
        # Apply limit
        limit = request.limit or 10
        limited_roadmaps = roadmaps[:limit]
        
        # Get sources that were actually searched
        available_sources = await external_roadmap_service.get_available_sources()
        if request.sources:
            sources_searched = [s for s in request.sources if s in [src.id for src in available_sources]]
        else:
            sources_searched = [src.id for src in available_sources]
        
        response = ExternalRoadmapSearchResponse(
            roadmaps=limited_roadmaps,
            query=request.query,
            sources_searched=sources_searched,
            total_found=len(roadmaps)
        )
        
        logger.info(f"POST search found {len(roadmaps)} roadmaps, returning {len(limited_roadmaps)}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in POST search external roadmaps: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"External roadmap search failed: {str(e)}"
        )


@external_roadmap_router.get("/roadmap/{roadmap_id}", response_model=ExternalRoadmap)
async def get_external_roadmap_details(roadmap_id: str):
    """
    Get detailed information about a specific external roadmap.
    
    Args:
        roadmap_id: ID of the external roadmap
        
    Returns:
        Detailed external roadmap information
        
    Raises:
        HTTPException: If roadmap not found or error occurs
    """
    try:
        logger.info(f"Getting details for external roadmap: {roadmap_id}")
        
        roadmap = await external_roadmap_service.get_roadmap_details(roadmap_id)
        
        if not roadmap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"External roadmap {roadmap_id} not found"
            )
        
        return roadmap
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting external roadmap details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get roadmap details: {str(e)}"
        )


@external_roadmap_router.get("/health")
async def external_roadmap_health_check():
    """Health check for external roadmap service."""
    try:
        # Test external service availability
        sources = await external_roadmap_service.get_available_sources()
        active_sources = [source.id for source in sources if source.is_active]
        
        # Test a simple search to verify functionality
        test_results = await external_roadmap_service.search_roadmaps("test", ["roadmap_sh"])
        
        return {
            "status": "healthy",
            "service": "external-roadmaps",
            "active_sources": active_sources,
            "total_sources": len(sources),
            "test_search_working": len(test_results) >= 0
        }
        
    except Exception as e:
        logger.error(f"External roadmap health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "external-roadmaps",
            "error": str(e)
        }