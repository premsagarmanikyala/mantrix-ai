"""
User progress tracking service for roadmap modules.
"""

import logging
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from models.user_progress import UserProgress, ModuleProgress, ProgressResponse
from models.roadmap import RoadmapResponse

logger = logging.getLogger(__name__)


class ProgressService:
    """Service for tracking and managing user progress."""
    
    @staticmethod
    def mark_module_complete(
        db: Session,
        user_id: str,
        module_id: str,
        branch_id: str,
        roadmap_id: str,
        duration: int = 0
    ) -> bool:
        """
        Mark a module as completed for a user.
        
        Args:
            db: Database session
            user_id: User identifier
            module_id: Module identifier
            branch_id: Branch identifier
            roadmap_id: Roadmap identifier
            duration: Module duration in seconds
            
        Returns:
            Success status
        """
        try:
            # Check if already completed
            existing_query = text("""
                SELECT id FROM user_progress 
                WHERE user_id = :user_id 
                AND module_id = :module_id
            """)
            
            existing = db.execute(existing_query, {
                "user_id": user_id,
                "module_id": module_id
            }).fetchone()
            
            if existing:
                logger.info(f"Module {module_id} already completed by user {user_id}")
                return True
            
            # Insert new progress record
            insert_query = text("""
                INSERT INTO user_progress 
                (user_id, module_id, branch_id, roadmap_id, completed_at, duration_completed)
                VALUES (:user_id, :module_id, :branch_id, :roadmap_id, :completed_at, :duration)
            """)
            
            db.execute(insert_query, {
                "user_id": user_id,
                "module_id": module_id,
                "branch_id": branch_id,
                "roadmap_id": roadmap_id,
                "completed_at": datetime.now(),
                "duration": duration
            })
            
            db.commit()
            logger.info(f"Marked module {module_id} as completed for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking module complete: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def get_user_progress(db: Session, user_id: str) -> ProgressResponse:
        """
        Get comprehensive progress information for a user.
        
        Args:
            db: Database session
            user_id: User identifier
            
        Returns:
            User's progress information
        """
        try:
            # Get all completed modules
            progress_query = text("""
                SELECT module_id, branch_id, roadmap_id, completed_at, duration_completed
                FROM user_progress 
                WHERE user_id = :user_id
                ORDER BY completed_at DESC
            """)
            
            progress_records = db.execute(progress_query, {"user_id": user_id}).fetchall()
            
            # Calculate statistics
            total_modules = len(progress_records)
            total_study_time = sum(record.duration_completed for record in progress_records)
            
            # Group by roadmap for completion percentages
            roadmap_modules = {}
            for record in progress_records:
                roadmap_id = record.roadmap_id
                if roadmap_id not in roadmap_modules:
                    roadmap_modules[roadmap_id] = []
                roadmap_modules[roadmap_id].append(record.module_id)
            
            # Get roadmap total module counts (simplified - using completed modules as basis)
            completion_percentage = {}
            for roadmap_id, completed_modules in roadmap_modules.items():
                # In a full implementation, we'd query the actual roadmap structure
                # For now, we'll use a placeholder calculation
                completion_percentage[roadmap_id] = min(100.0, len(completed_modules) * 20.0)
            
            # Recent activity (last 10 modules)
            recent_activity = []
            for record in progress_records[:10]:
                recent_activity.append(ModuleProgress(
                    module_id=record.module_id,
                    branch_id=record.branch_id,
                    roadmap_id=record.roadmap_id,
                    completed_at=record.completed_at,
                    duration_completed=record.duration_completed
                ))
            
            return ProgressResponse(
                user_id=user_id,
                total_modules_completed=total_modules,
                total_study_time=total_study_time,
                roadmaps_in_progress=len(roadmap_modules),
                completion_percentage=completion_percentage,
                recent_activity=recent_activity
            )
            
        except Exception as e:
            logger.error(f"Error getting user progress: {str(e)}")
            return ProgressResponse(
                user_id=user_id,
                total_modules_completed=0,
                total_study_time=0,
                roadmaps_in_progress=0
            )
    
    @staticmethod
    def get_completed_modules_for_roadmap(
        db: Session,
        user_id: str,
        roadmap_id: str
    ) -> List[str]:
        """
        Get list of completed module IDs for a specific roadmap.
        
        Args:
            db: Database session
            user_id: User identifier
            roadmap_id: Roadmap identifier
            
        Returns:
            List of completed module IDs
        """
        try:
            query = text("""
                SELECT module_id FROM user_progress 
                WHERE user_id = :user_id AND roadmap_id = :roadmap_id
            """)
            
            results = db.execute(query, {
                "user_id": user_id,
                "roadmap_id": roadmap_id
            }).fetchall()
            
            return [result.module_id for result in results]
            
        except Exception as e:
            logger.error(f"Error getting completed modules: {str(e)}")
            return []
    
    @staticmethod
    def initialize_progress_table(db: Session) -> bool:
        """
        Initialize the user_progress table if it doesn't exist.
        
        Args:
            db: Database session
            
        Returns:
            Success status
        """
        try:
            create_table_query = text("""
                CREATE TABLE IF NOT EXISTS user_progress (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    module_id VARCHAR(255) NOT NULL,
                    branch_id VARCHAR(255) NOT NULL,
                    roadmap_id VARCHAR(255) NOT NULL,
                    completed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    duration_completed INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, module_id)
                )
            """)
            
            db.execute(create_table_query)
            db.commit()
            logger.info("User progress table initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing progress table: {str(e)}")
            db.rollback()
            return False