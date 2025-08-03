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
from models.roadmap import RoadmapGenerateRequest, RoadmapGenerateResponse
from core.database import get_db
from services.user_service import UserService
from services.project_service import ProjectService
from services.roadmap_agent import roadmap_agent
from api.roadmap import roadmap_router
from api.resume import resume_router
from api.auth import auth_router

api_router = APIRouter()

# Include routers
api_router.include_router(auth_router)  # Auth routes at /api/auth
api_router.include_router(roadmap_router)  # Roadmap routes at /api/v1/roadmap

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


@api_router.post("/project/{project_id}/roadmap/generate")
async def generate_project_roadmap(project_id: int, db: Session = Depends(get_db)):
    """Generate learning roadmap for a specific project."""
    # Get project details
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Use project title and description as input for roadmap generation
        user_input = f"{project.title}. {project.description or ''}"
        roadmaps = roadmap_agent.generate_roadmaps(user_input.strip())
        
        return {
            "message": "Roadmap generation completed",
            "project_id": project_id,
            "roadmaps": [roadmap.dict() for roadmap in roadmaps]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate roadmap for project: {str(e)}"
        )


def setup_routes():
    """Set up all API routes."""
    # Include all routers
    from api.progress import progress_router
    from api.recommendation import recommendation_router
    
    api_router.include_router(auth_router)
    api_router.include_router(roadmap_router, prefix="/v1")
    api_router.include_router(resume_router, prefix="/v1")
    api_router.include_router(progress_router, prefix="/v1")
    api_router.include_router(recommendation_router, prefix="/v1")
    
    return api_router