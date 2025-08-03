"""
Service for managing roadmap database operations.
"""

import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from db.models import RoadmapDB
from models.roadmap import RoadmapResponse, RoadmapBranch, VideoModule

logger = logging.getLogger(__name__)


class RoadmapService:
    """Service for roadmap database operations."""
    
    @staticmethod
    async def save_roadmaps(
        db: AsyncSession, 
        roadmaps: List[RoadmapResponse], 
        user_id: str
    ) -> List[str]:
        """
        Save multiple roadmaps to the database.
        
        Args:
            db: Database session
            roadmaps: List of roadmap responses to save
            user_id: User ID to associate with roadmaps
            
        Returns:
            List of saved roadmap IDs
            
        Raises:
            Exception: If database operation fails
        """
        try:
            saved_ids = []
            
            for roadmap in roadmaps:
                # Create database model from roadmap response
                roadmap_db = RoadmapDB.from_roadmap_response(roadmap, user_id)
                
                db.add(roadmap_db)
                saved_ids.append(roadmap_db.id)
                
                logger.info(f"Prepared roadmap for saving: {roadmap_db.title} (ID: {roadmap_db.id})")
            
            await db.commit()
            logger.info(f"Successfully saved {len(saved_ids)} roadmaps to database")
            
            return saved_ids
            
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error saving roadmaps: {str(e)}")
            raise Exception(f"Failed to save roadmaps: {str(e)}")
        except Exception as e:
            await db.rollback()
            logger.error(f"Unexpected error saving roadmaps: {str(e)}")
            raise Exception(f"Failed to save roadmaps: {str(e)}")
    
    @staticmethod
    async def get_roadmaps_by_user(
        db: AsyncSession, 
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[RoadmapResponse]:
        """
        Retrieve roadmaps for a specific user.
        
        Args:
            db: Database session
            user_id: User ID to fetch roadmaps for
            limit: Maximum number of roadmaps to return
            offset: Number of roadmaps to skip
            
        Returns:
            List of roadmap responses
            
        Raises:
            Exception: If database operation fails
        """
        try:
            # Query roadmaps for user
            stmt = (
                select(RoadmapDB)
                .where(RoadmapDB.user_id == user_id)
                .order_by(RoadmapDB.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            
            result = await db.execute(stmt)
            roadmap_records = result.scalars().all()
            
            logger.info(f"Found {len(roadmap_records)} roadmaps for user {user_id}")
            
            # Convert database models to response models
            roadmaps = []
            for record in roadmap_records:
                roadmap = RoadmapService._convert_db_to_response(record)
                roadmaps.append(roadmap)
            
            return roadmaps
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching roadmaps: {str(e)}")
            raise Exception(f"Failed to fetch roadmaps: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching roadmaps: {str(e)}")
            raise Exception(f"Failed to fetch roadmaps: {str(e)}")
    
    @staticmethod
    async def get_roadmap_by_id(
        db: AsyncSession, 
        roadmap_id: str,
        user_id: Optional[str] = None
    ) -> Optional[RoadmapResponse]:
        """
        Retrieve a specific roadmap by ID.
        
        Args:
            db: Database session
            roadmap_id: Roadmap ID to fetch
            user_id: Optional user ID for additional filtering
            
        Returns:
            Roadmap response or None if not found
        """
        try:
            stmt = select(RoadmapDB).where(RoadmapDB.id == roadmap_id)
            
            if user_id:
                stmt = stmt.where(RoadmapDB.user_id == user_id)
            
            result = await db.execute(stmt)
            record = result.scalar_one_or_none()
            
            if not record:
                return None
            
            return RoadmapService._convert_db_to_response(record)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching roadmap {roadmap_id}: {str(e)}")
            raise Exception(f"Failed to fetch roadmap: {str(e)}")
    
    @staticmethod
    def _convert_db_to_response(record: RoadmapDB) -> RoadmapResponse:
        """
        Convert database record to RoadmapResponse model.
        
        Args:
            record: Database record
            
        Returns:
            RoadmapResponse object
        """
        # Convert branches JSON to RoadmapBranch objects
        branches = []
        for branch_data in record.branches:
            # Convert videos JSON to VideoModule objects
            videos = []
            for video_data in branch_data.get("videos", []):
                video = VideoModule(
                    id=video_data["id"],
                    title=video_data["title"],
                    duration=video_data["duration"]
                )
                videos.append(video)
            
            branch = RoadmapBranch(
                id=branch_data["id"],
                title=branch_data["title"],
                videos=videos
            )
            branches.append(branch)
        
        return RoadmapResponse(
            id=record.id,
            title=record.title,
            total_duration=record.total_duration,
            branches=branches
        )
    
    @staticmethod
    async def delete_roadmap(
        db: AsyncSession, 
        roadmap_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Delete a roadmap by ID.
        
        Args:
            db: Database session
            roadmap_id: Roadmap ID to delete
            user_id: Optional user ID for additional filtering
            
        Returns:
            True if deleted, False if not found
        """
        try:
            stmt = select(RoadmapDB).where(RoadmapDB.id == roadmap_id)
            
            if user_id:
                stmt = stmt.where(RoadmapDB.user_id == user_id)
            
            result = await db.execute(stmt)
            record = result.scalar_one_or_none()
            
            if not record:
                return False
            
            await db.delete(record)
            await db.commit()
            
            logger.info(f"Deleted roadmap {roadmap_id}")
            return True
            
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error deleting roadmap {roadmap_id}: {str(e)}")
            raise Exception(f"Failed to delete roadmap: {str(e)}")