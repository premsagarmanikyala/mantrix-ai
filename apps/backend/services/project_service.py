"""
Project service for handling project-related business logic.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from models.database import Project
from models.schemas import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service class for project operations."""
    
    @staticmethod
    def get_all_projects(db: Session) -> List[Project]:
        """Get all projects from database."""
        return db.query(Project).all()
    
    @staticmethod
    def get_project_by_id(db: Session, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        return db.query(Project).filter(Project.id == project_id).first()
    
    @staticmethod
    def get_projects_by_owner(db: Session, owner_id: int) -> List[Project]:
        """Get all projects by owner ID."""
        return db.query(Project).filter(Project.owner_id == owner_id).all()
    
    @staticmethod
    def create_project(db: Session, project: ProjectCreate) -> Project:
        """Create a new project."""
        db_project = Project(
            title=project.title,
            description=project.description,
            status=project.status,
            priority=project.priority,
            owner_id=project.owner_id
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    
    @staticmethod
    def update_project(db: Session, project_id: int, project_update: ProjectUpdate) -> Optional[Project]:
        """Update project by ID."""
        db_project = ProjectService.get_project_by_id(db, project_id)
        if not db_project:
            return None
        
        update_data = project_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)
        
        db.commit()
        db.refresh(db_project)
        return db_project
    
    @staticmethod
    def delete_project(db: Session, project_id: int) -> bool:
        """Delete project by ID."""
        db_project = ProjectService.get_project_by_id(db, project_id)
        if not db_project:
            return False
        
        db.delete(db_project)
        db.commit()
        return True