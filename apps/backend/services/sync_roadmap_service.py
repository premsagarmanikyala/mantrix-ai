"""
Synchronous roadmap service for database operations.
"""

import json
import logging
import uuid
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.roadmap import RoadmapResponse, RoadmapBranch, VideoModule

logger = logging.getLogger(__name__)


class SyncRoadmapService:
    """Synchronous service for roadmap database operations."""
    
    @staticmethod
    def save_roadmaps(db: Session, roadmaps: List[RoadmapResponse], user_id: str) -> List[str]:
        """
        Save multiple roadmaps to the database synchronously.
        
        Args:
            db: Database session
            roadmaps: List of roadmap responses to save
            user_id: User ID to associate with roadmaps
            
        Returns:
            List of saved roadmap IDs
        """
        try:
            saved_ids = []
            
            for roadmap in roadmaps:
                # Convert branches to JSON
                branches_json = json.dumps([
                    {
                        "id": branch.id,
                        "title": branch.title,
                        "videos": [
                            {
                                "id": video.id,
                                "title": video.title,
                                "duration": video.duration
                            }
                            for video in branch.videos
                        ]
                    }
                    for branch in roadmap.branches
                ])
                
                # Insert roadmap
                insert_sql = text("""
                    INSERT INTO roadmaps (id, user_id, title, total_duration, branches)
                    VALUES (:id, :user_id, :title, :total_duration, :branches)
                """)
                
                db.execute(insert_sql, {
                    'id': roadmap.id,
                    'user_id': user_id,
                    'title': roadmap.title,
                    'total_duration': roadmap.total_duration,
                    'branches': branches_json
                })
                
                saved_ids.append(roadmap.id)
                logger.info(f"Saved roadmap: {roadmap.title} (ID: {roadmap.id})")
            
            db.commit()
            logger.info(f"Successfully saved {len(saved_ids)} roadmaps to database")
            return saved_ids
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error saving roadmaps: {str(e)}")
            raise Exception(f"Failed to save roadmaps: {str(e)}")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error saving roadmaps: {str(e)}")
            raise Exception(f"Failed to save roadmaps: {str(e)}")
    
    @staticmethod
    def get_roadmaps_by_user(
        db: Session, 
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
        """
        try:
            # Query roadmaps for user
            select_sql = text("""
                SELECT id, user_id, title, total_duration, branches, created_at
                FROM roadmaps 
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """)
            
            result = db.execute(select_sql, {
                'user_id': user_id,
                'limit': limit,
                'offset': offset
            })
            
            roadmap_records = result.fetchall()
            logger.info(f"Found {len(roadmap_records)} roadmaps for user {user_id}")
            
            # Convert database records to response models
            roadmaps = []
            for record in roadmap_records:
                roadmap = SyncRoadmapService._convert_record_to_response(record)
                roadmaps.append(roadmap)
            
            return roadmaps
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching roadmaps: {str(e)}")
            raise Exception(f"Failed to fetch roadmaps: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching roadmaps: {str(e)}")
            raise Exception(f"Failed to fetch roadmaps: {str(e)}")
    
    @staticmethod
    def get_roadmap_by_id(
        db: Session, 
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
            select_sql = text("""
                SELECT id, user_id, title, total_duration, branches, created_at
                FROM roadmaps 
                WHERE id = :roadmap_id
            """)
            
            params = {'roadmap_id': roadmap_id}
            
            if user_id:
                select_sql = text("""
                    SELECT id, user_id, title, total_duration, branches, created_at
                    FROM roadmaps 
                    WHERE id = :roadmap_id AND user_id = :user_id
                """)
                params['user_id'] = user_id
            
            result = db.execute(select_sql, params)
            record = result.fetchone()
            
            if not record:
                return None
            
            return SyncRoadmapService._convert_record_to_response(record)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching roadmap {roadmap_id}: {str(e)}")
            raise Exception(f"Failed to fetch roadmap: {str(e)}")
    
    @staticmethod
    def delete_roadmap(
        db: Session, 
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
            delete_sql = text("DELETE FROM roadmaps WHERE id = :roadmap_id")
            params = {'roadmap_id': roadmap_id}
            
            if user_id:
                delete_sql = text("DELETE FROM roadmaps WHERE id = :roadmap_id AND user_id = :user_id")
                params['user_id'] = user_id
            
            result = db.execute(delete_sql, params)
            db.commit()
            
            deleted_count = result.rowcount
            logger.info(f"Deleted {deleted_count} roadmap(s) with ID {roadmap_id}")
            
            return deleted_count > 0
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting roadmap {roadmap_id}: {str(e)}")
            raise Exception(f"Failed to delete roadmap: {str(e)}")
    
    @staticmethod
    def _convert_record_to_response(record) -> RoadmapResponse:
        """
        Convert database record to RoadmapResponse model.
        
        Args:
            record: Database record (tuple or Row object)
            
        Returns:
            RoadmapResponse object
        """
        # Handle both tuple and Row objects
        if hasattr(record, '_asdict'):
            record_dict = record._asdict()
            branches_json = record_dict['branches']
        else:
            # Tuple format: id, user_id, title, total_duration, branches, created_at
            branches_json = record[4]
        
        # Parse branches JSON
        branches_data = json.loads(branches_json)
        
        # Convert branches JSON to RoadmapBranch objects
        branches = []
        for branch_data in branches_data:
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
        
        # Create response object
        if hasattr(record, '_asdict'):
            record_dict = record._asdict()
            return RoadmapResponse(
                id=record_dict['id'],
                title=record_dict['title'],
                total_duration=record_dict['total_duration'],
                branches=branches
            )
        else:
            return RoadmapResponse(
                id=record[0],
                title=record[2],
                total_duration=record[3],
                branches=branches
            )