"""
API route definitions for Mantrix application.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from models.schemas import (
    UserCreate, UserResponse, UserUpdate,
    ProjectCreate, ProjectResponse, ProjectUpdate
)
from core.database import get_db
from services.user_service import UserService
from services.project_service import ProjectService

api_router = APIRouter()

# User routes
@api_router.get("/users", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    """Get all users."""
    return UserService.get_all_users(db)


@api_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@api_router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    return UserService.create_user(db, user)


@api_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, 
    user_update: UserUpdate, 
    db: Session = Depends(get_db)
):
    """Update user by ID."""
    user = UserService.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@api_router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user by ID."""
    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


# Project routes
@api_router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(db: Session = Depends(get_db)):
    """Get all projects."""
    return ProjectService.get_all_projects(db)


@api_router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get project by ID."""
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@api_router.post("/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project."""
    return ProjectService.create_project(db, project)


@api_router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int, 
    project_update: ProjectUpdate, 
    db: Session = Depends(get_db)
):
    """Update project by ID."""
    project = ProjectService.update_project(db, project_id, project_update)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete project by ID."""
    success = ProjectService.delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}


# AI/Resume Builder routes
@api_router.post("/resume/generate")
async def generate_resume(user_id: int, db: Session = Depends(get_db)):
    """Generate resume for user using AI."""
    # This would integrate with the resume builder service
    return {"message": "Resume generation started", "user_id": user_id}


@api_router.post("/roadmap/generate")
async def generate_roadmap(project_id: int, db: Session = Depends(get_db)):
    """Generate learning roadmap for project."""
    # This would integrate with the roadmap engine service
    return {"message": "Roadmap generation started", "project_id": project_id}