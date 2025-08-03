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

    def complete_module(self, db: Session, user_id: str, roadmap_id: str, 
                       branch_id: str, module_id: str, duration_completed: int):
        """
        Mark a module as completed with duplicate prevention.
        Returns progress entry if successful, None if already completed.
        """
        from models.user_progress import UserProgressEntry
        import uuid
        
        try:
            # Initialize progress table if needed
            self.initialize_progress_table(db)
            
            # Check if module already completed
            check_query = text("""
                SELECT id FROM user_progress 
                WHERE user_id = :user_id 
                AND roadmap_id = :roadmap_id 
                AND branch_id = :branch_id 
                AND module_id = :module_id
            """)
            
            existing = db.execute(check_query, {
                "user_id": user_id,
                "roadmap_id": roadmap_id,
                "branch_id": branch_id,
                "module_id": module_id
            }).fetchone()
            
            if existing:
                logger.info(f"Module {module_id} already completed for user {user_id}")
                return None
            
            # Insert new progress entry
            progress_id = f"progress_{uuid.uuid4().hex[:8]}"
            completed_at = datetime.utcnow()
            
            insert_query = text("""
                INSERT INTO user_progress 
                (id, user_id, roadmap_id, branch_id, module_id, completed_at, duration_completed)
                VALUES (:id, :user_id, :roadmap_id, :branch_id, :module_id, :completed_at, :duration_completed)
            """)
            
            db.execute(insert_query, {
                "id": progress_id,
                "user_id": user_id,
                "roadmap_id": roadmap_id,
                "branch_id": branch_id,
                "module_id": module_id,
                "completed_at": completed_at,
                "duration_completed": duration_completed
            })
            
            db.commit()
            
            logger.info(f"Marked module {module_id} as completed for user {user_id}")
            
            return UserProgressEntry(
                id=progress_id,
                user_id=user_id,
                roadmap_id=roadmap_id,
                branch_id=branch_id,
                module_id=module_id,
                completed_at=completed_at,
                duration_completed=duration_completed
            )
            
        except Exception as e:
            logger.error(f"Error completing module: {str(e)}")
            db.rollback()
            return None

    def validate_user_roadmap_access(self, db: Session, user_id: str, roadmap_id: str) -> bool:
        """Validate that user has access to the specified roadmap."""
        try:
            # Check if roadmap exists and belongs to user
            query = text("""
                SELECT id FROM roadmaps 
                WHERE id = :roadmap_id AND user_id = :user_id
            """)
            
            result = db.execute(query, {
                "roadmap_id": roadmap_id,
                "user_id": user_id
            }).fetchone()
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Error validating roadmap access: {str(e)}")
            return False

    def get_progress_summary(self, db: Session, user_id: str, roadmap_id: str):
        """Generate comprehensive progress summary for a roadmap."""
        from models.user_progress import ProgressSummaryResponse, BranchProgressSummary
        
        try:
            # Initialize progress table if needed
            self.initialize_progress_table(db)
            
            # Get roadmap data
            roadmap_query = text("""
                SELECT branches_data FROM roadmaps 
                WHERE id = :roadmap_id AND user_id = :user_id
            """)
            
            roadmap_result = db.execute(roadmap_query, {
                "roadmap_id": roadmap_id,
                "user_id": user_id
            }).fetchone()
            
            if not roadmap_result:
                logger.warning(f"Roadmap {roadmap_id} not found for user {user_id}")
                return None
            
            # Parse roadmap structure
            branches_data = roadmap_result[0]
            if isinstance(branches_data, str):
                import json
                branches_data = json.loads(branches_data)
            
            # Calculate total modules and duration from roadmap
            total_modules = 0
            total_duration = 0
            branch_totals = {}
            
            for branch in branches_data:
                branch_id = branch["id"]
                videos = branch.get("videos", [])
                branch_module_count = len(videos)
                branch_duration = sum(video.get("duration", 0) for video in videos)
                
                total_modules += branch_module_count
                total_duration += branch_duration
                
                branch_totals[branch_id] = {
                    "total_modules": branch_module_count,
                    "total_duration": branch_duration,
                    "name": branch.get("title", f"Branch {branch_id}")
                }
            
            # Get completed progress
            progress_query = text("""
                SELECT branch_id, module_id, duration_completed, completed_at
                FROM user_progress 
                WHERE user_id = :user_id AND roadmap_id = :roadmap_id
            """)
            
            progress_result = db.execute(progress_query, {
                "user_id": user_id,
                "roadmap_id": roadmap_id
            }).fetchall()
            
            # Calculate completed stats
            completed_modules = len(progress_result)
            completed_duration = sum(row[2] for row in progress_result)
            last_activity = max((row[3] for row in progress_result), default=None)
            
            # Calculate branch-level progress
            branch_progress = {}
            for row in progress_result:
                branch_id = row[0]
                if branch_id not in branch_progress:
                    branch_progress[branch_id] = {
                        "completed": 0,
                        "duration_done": 0
                    }
                branch_progress[branch_id]["completed"] += 1
                branch_progress[branch_id]["duration_done"] += row[2]
            
            # Build branch summaries
            branches = []
            for branch_id, totals in branch_totals.items():
                progress = branch_progress.get(branch_id, {"completed": 0, "duration_done": 0})
                
                branch_progress_percent = 0.0
                if totals["total_modules"] > 0:
                    branch_progress_percent = (progress["completed"] / totals["total_modules"]) * 100
                
                branches.append(BranchProgressSummary(
                    branch_id=branch_id,
                    completed=progress["completed"],
                    total=totals["total_modules"],
                    duration_done=progress["duration_done"],
                    duration_total=totals["total_duration"],
                    progress_percent=round(branch_progress_percent, 1)
                ))
            
            # Calculate overall progress percentage
            progress_percent = 0.0
            if total_modules > 0:
                progress_percent = (completed_modules / total_modules) * 100
            
            return ProgressSummaryResponse(
                roadmap_id=roadmap_id,
                total_modules=total_modules,
                completed_modules=completed_modules,
                total_duration=total_duration,
                completed_duration=completed_duration,
                progress_percent=round(progress_percent, 1),
                branches=branches,
                last_activity=last_activity
            )
            
        except Exception as e:
            logger.error(f"Error generating progress summary: {str(e)}")
            return None