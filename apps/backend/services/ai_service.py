"""
AI service for handling AI-related functionality like resume building and roadmap generation.
"""

from typing import Dict, Any, Optional
import json
from sqlalchemy.orm import Session

from models.database import User, Project
from services.user_service import UserService
from services.project_service import ProjectService
from core.config import settings


class AIService:
    """Service class for AI operations."""
    
    @staticmethod
    def generate_resume(db: Session, user_id: int, template_style: str = "modern") -> Dict[str, Any]:
        """
        Generate a resume for a user using AI.
        This is a placeholder implementation that would integrate with OpenAI or similar.
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        
        # Get user's projects
        projects = ProjectService.get_projects_by_owner(db, user_id)
        
        # This would normally call an AI service like OpenAI
        # For now, we'll return a structured response
        resume_data = {
            "user_id": user_id,
            "template_style": template_style,
            "personal_info": {
                "name": user.full_name,
                "email": user.email,
                "bio": user.bio or "Passionate developer and problem solver"
            },
            "projects": [
                {
                    "title": project.title,
                    "description": project.description,
                    "status": project.status,
                    "priority": project.priority
                }
                for project in projects
            ],
            "skills": AIService._extract_skills_from_projects(projects),
            "generated_at": "2025-08-03T00:00:00Z",
            "status": "generated"
        }
        
        return resume_data
    
    @staticmethod
    def generate_roadmap(db: Session, project_id: int, skill_level: str = "beginner", timeframe: str = "3_months") -> Dict[str, Any]:
        """
        Generate a learning roadmap for a project.
        This is a placeholder implementation that would integrate with AI services.
        """
        project = ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise ValueError("Project not found")
        
        # This would normally call an AI service to generate a personalized roadmap
        roadmap_data = {
            "project_id": project_id,
            "project_title": project.title,
            "skill_level": skill_level,
            "timeframe": timeframe,
            "milestones": AIService._generate_milestones(project.title, skill_level, timeframe),
            "resources": AIService._generate_resources(project.title),
            "estimated_hours": AIService._estimate_hours(timeframe),
            "generated_at": "2025-08-03T00:00:00Z",
            "status": "generated"
        }
        
        return roadmap_data
    
    @staticmethod
    def _extract_skills_from_projects(projects: list) -> list:
        """Extract skills from project descriptions (placeholder logic)."""
        skills = set()
        
        # This would use NLP/AI to extract skills from project descriptions
        # For now, we'll use simple keyword matching
        skill_keywords = {
            "python": "Python",
            "javascript": "JavaScript",
            "react": "React",
            "fastapi": "FastAPI",
            "sql": "SQL",
            "api": "API Development",
            "web": "Web Development",
            "mobile": "Mobile Development",
            "ai": "Artificial Intelligence",
            "ml": "Machine Learning"
        }
        
        for project in projects:
            if project.description:
                description_lower = project.description.lower()
                for keyword, skill in skill_keywords.items():
                    if keyword in description_lower:
                        skills.add(skill)
        
        return list(skills)
    
    @staticmethod
    def _generate_milestones(project_title: str, skill_level: str, timeframe: str) -> list:
        """Generate learning milestones (placeholder logic)."""
        milestones = []
        
        if "web" in project_title.lower():
            if skill_level == "beginner":
                milestones = [
                    {"week": 1, "title": "HTML & CSS Fundamentals", "description": "Learn basic web structure and styling"},
                    {"week": 3, "title": "JavaScript Basics", "description": "Variables, functions, and DOM manipulation"},
                    {"week": 6, "title": "React Introduction", "description": "Components, props, and state management"},
                    {"week": 9, "title": "API Integration", "description": "Fetching data and handling responses"},
                    {"week": 12, "title": "Project Deployment", "description": "Deploy your web application"}
                ]
        else:
            milestones = [
                {"week": 1, "title": "Project Planning", "description": "Define requirements and architecture"},
                {"week": 4, "title": "Core Development", "description": "Implement main functionality"},
                {"week": 8, "title": "Testing & Optimization", "description": "Test and optimize the application"},
                {"week": 12, "title": "Deployment & Documentation", "description": "Deploy and document the project"}
            ]
        
        return milestones
    
    @staticmethod
    def _generate_resources(project_title: str) -> list:
        """Generate learning resources (placeholder logic)."""
        return [
            {"type": "documentation", "title": "Official Documentation", "url": "https://docs.example.com"},
            {"type": "tutorial", "title": "Getting Started Guide", "url": "https://tutorial.example.com"},
            {"type": "video", "title": "Video Course", "url": "https://video.example.com"},
            {"type": "book", "title": "Recommended Reading", "url": "https://book.example.com"}
        ]
    
    @staticmethod
    def _estimate_hours(timeframe: str) -> int:
        """Estimate learning hours based on timeframe."""
        timeframe_hours = {
            "1_month": 40,
            "3_months": 120,
            "6_months": 240,
            "1_year": 480
        }
        return timeframe_hours.get(timeframe, 120)