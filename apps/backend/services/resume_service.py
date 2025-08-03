"""
Resume generation service with AI integration for study, fast, and analyzer modes.
"""

import logging
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from models.resume import (
    ResumeGenerateRequest, ResumeGenerateResponse, GeneratedResume,
    ResumeAnalysis, SavedResume, ResumeListResponse
)
from models.roadmap import RoadmapResponse
from services.sync_roadmap_service import SyncRoadmapService
from services.progress_service import ProgressService
from core.database import get_db

logger = logging.getLogger(__name__)


class ResumeService:
    """AI-powered resume generation and analysis service."""
    
    def __init__(self):
        """Initialize the resume service with OpenAI configuration."""
        import os
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found - using fallback generation")
            self.llm = None
        else:
            # Initialize OpenAI chat model - the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
            self.llm = ChatOpenAI(
                model="gpt-4o",
                api_key=self.api_key,
                temperature=0.7
            )
    
    def generate_resume(
        self,
        db: Session,
        user_id: str,
        request: ResumeGenerateRequest
    ) -> ResumeGenerateResponse:
        """
        Generate resume based on mode and user progress.
        
        Args:
            db: Database session
            user_id: User identifier
            request: Resume generation request
            
        Returns:
            Generated resume response
        """
        try:
            logger.info(f"Generating resume for user {user_id} in {request.mode} mode")
            
            if request.mode == "study":
                return self._generate_study_mode_resume(db, user_id, request)
            elif request.mode == "fast":
                return self._generate_fast_mode_resume(db, user_id, request)
            elif request.mode == "analyzer":
                return self._generate_analyzer_mode_resume(db, user_id, request)
            else:
                raise ValueError(f"Invalid mode: {request.mode}")
                
        except Exception as e:
            logger.error(f"Error generating resume: {str(e)}")
            raise Exception(f"Resume generation failed: {str(e)}")
    
    def _generate_study_mode_resume(
        self,
        db: Session,
        user_id: str,
        request: ResumeGenerateRequest
    ) -> ResumeGenerateResponse:
        """Generate resume based only on completed modules."""
        if not request.roadmap_id:
            raise ValueError("roadmap_id is required for study mode")
        
        # Get user's completed modules for this roadmap
        completed_module_ids = ProgressService.get_completed_modules_for_roadmap(
            db, user_id, request.roadmap_id
        )
        
        if not completed_module_ids:
            # Generate minimal resume if no modules completed
            resume_text = self._generate_minimal_resume(user_id)
            skills_included = []
            modules_used = []
        else:
            # Get roadmap data
            roadmap = SyncRoadmapService.get_roadmap_by_id(db, request.roadmap_id, user_id)
            if not roadmap:
                raise ValueError("Roadmap not found")
            
            # Extract skills and content from completed modules only
            completed_content = self._extract_completed_content(roadmap, completed_module_ids)
            resume_text, skills_included = self._generate_resume_with_ai(
                completed_content, request.mode, user_id
            )
            modules_used = completed_module_ids
        
        # Create resume object
        resume = GeneratedResume(
            id=f"resume_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            mode=request.mode,
            roadmap_id=request.roadmap_id,
            resume_text=resume_text,
            skills_included=skills_included,
            modules_used=modules_used
        )
        
        # Save to database
        self._save_resume_to_db(db, resume, None, None)
        
        return ResumeGenerateResponse(
            resume=resume,
            status="success",
            message=f"Study mode resume generated with {len(modules_used)} completed modules"
        )
    
    def _generate_fast_mode_resume(
        self,
        db: Session,
        user_id: str,
        request: ResumeGenerateRequest
    ) -> ResumeGenerateResponse:
        """Generate resume from entire roadmap regardless of completion."""
        if not request.roadmap_id:
            raise ValueError("roadmap_id is required for fast mode")
        
        # Get full roadmap data
        roadmap = SyncRoadmapService.get_roadmap_by_id(db, request.roadmap_id, user_id)
        if not roadmap:
            raise ValueError("Roadmap not found")
        
        # Extract all skills and content from roadmap
        full_content = self._extract_full_roadmap_content(roadmap)
        resume_text, skills_included = self._generate_resume_with_ai(
            full_content, request.mode, user_id
        )
        
        # Get all module IDs from roadmap
        all_modules = []
        for branch in roadmap.branches:
            for video in branch.videos:
                all_modules.append(video.id)
        
        # Create resume object
        resume = GeneratedResume(
            id=f"resume_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            mode=request.mode,
            roadmap_id=request.roadmap_id,
            resume_text=resume_text,
            skills_included=skills_included,
            modules_used=all_modules
        )
        
        # Save to database
        self._save_resume_to_db(db, resume, None, None)
        
        return ResumeGenerateResponse(
            resume=resume,
            status="success",
            message=f"Fast mode resume generated with full roadmap content ({len(all_modules)} modules)"
        )
    
    def _generate_analyzer_mode_resume(
        self,
        db: Session,
        user_id: str,
        request: ResumeGenerateRequest
    ) -> ResumeGenerateResponse:
        """Analyze existing resume against job description."""
        if not request.existing_resume or not request.job_description:
            raise ValueError("existing_resume and job_description are required for analyzer mode")
        
        # Analyze resume vs job description
        analysis = self._analyze_resume_vs_job(request.existing_resume, request.job_description)
        
        # Generate improved resume suggestions
        improved_resume_text = self._improve_resume_with_ai(
            request.existing_resume, request.job_description, analysis
        )
        
        # Create resume object with analysis
        resume = GeneratedResume(
            id=f"resume_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            mode=request.mode,
            roadmap_id=None,
            resume_text=improved_resume_text,
            skills_included=analysis.missing_skills + analysis.strengths,
            modules_used=analysis.recommended_modules
        )
        
        # Save to database with job description
        self._save_resume_to_db(db, resume, request.job_description, analysis)
        
        return ResumeGenerateResponse(
            resume=resume,
            analysis=analysis,
            status="success",
            message=f"Resume analyzed with ATS score: {analysis.ats_score}/100"
        )
    
    def _extract_completed_content(self, roadmap: RoadmapResponse, completed_module_ids: List[str]) -> Dict[str, Any]:
        """Extract content from completed modules only."""
        content = {
            "skills": [],
            "topics": [],
            "completed_modules": [],
            "roadmap_title": roadmap.title
        }
        
        for branch in roadmap.branches:
            branch_skills = []
            branch_topics = []
            
            for video in branch.videos:
                if video.id in completed_module_ids:
                    # Extract skills from video title
                    video_skills = self._extract_skills_from_title(video.title)
                    branch_skills.extend(video_skills)
                    branch_topics.append(video.title)
                    content["completed_modules"].append({
                        "id": video.id,
                        "title": video.title,
                        "branch": branch.title,
                        "duration": video.duration,
                        "is_core": video.is_core
                    })
            
            if branch_skills:  # Only include branch if it has completed modules
                content["skills"].extend(branch_skills)
                content["topics"].append(f"{branch.title}: {', '.join(branch_topics)}")
        
        return content
    
    def _extract_full_roadmap_content(self, roadmap: RoadmapResponse) -> Dict[str, Any]:
        """Extract all content from roadmap."""
        content = {
            "skills": [],
            "topics": [],
            "all_modules": [],
            "roadmap_title": roadmap.title
        }
        
        for branch in roadmap.branches:
            branch_skills = []
            branch_topics = []
            
            for video in branch.videos:
                # Extract skills from video title
                video_skills = self._extract_skills_from_title(video.title)
                branch_skills.extend(video_skills)
                branch_topics.append(video.title)
                content["all_modules"].append({
                    "id": video.id,
                    "title": video.title,
                    "branch": branch.title,
                    "duration": video.duration,
                    "is_core": video.is_core
                })
            
            content["skills"].extend(branch_skills)
            content["topics"].append(f"{branch.title}: {', '.join(branch_topics)}")
        
        return content
    
    def _extract_skills_from_title(self, title: str) -> List[str]:
        """Extract potential skills from a video/module title."""
        # Common technical skills keywords
        tech_keywords = [
            "React", "JavaScript", "Python", "Node.js", "HTML", "CSS", "SQL",
            "AWS", "Docker", "Git", "API", "REST", "GraphQL", "MongoDB",
            "PostgreSQL", "Machine Learning", "AI", "FastAPI", "Express",
            "Vue", "Angular", "TypeScript", "Java", "C++", "Go", "Rust"
        ]
        
        found_skills = []
        title_lower = title.lower()
        
        for keyword in tech_keywords:
            if keyword.lower() in title_lower:
                found_skills.append(keyword)
        
        # Extract additional patterns
        if "database" in title_lower:
            found_skills.append("Database Design")
        if "test" in title_lower:
            found_skills.append("Testing")
        if "deploy" in title_lower:
            found_skills.append("Deployment")
        if "security" in title_lower:
            found_skills.append("Security")
        
        return found_skills
    
    def _generate_resume_with_ai(
        self,
        content: Dict[str, Any],
        mode: str,
        user_id: str
    ) -> Tuple[str, List[str]]:
        """Generate resume content using AI."""
        if not self.llm:
            return self._generate_fallback_resume(content, mode), content.get("skills", [])
        
        try:
            # Create AI prompt
            system_prompt = f"""You are an expert resume writer. Generate a professional resume based on the following learning content.
            
Mode: {mode}
Content: {json.dumps(content, indent=2)}

Create a resume with these sections:
- Professional Summary
- Technical Skills
- Experience (based on learning modules)
- Education/Certifications

Format as clean, ATS-friendly text. Focus on skills and knowledge from the provided content."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Generate a professional resume for user learning content in {mode} mode.")
            ]
            
            response = self.llm.invoke(messages)
            resume_text = response.content
            
            # Extract skills mentioned in the resume
            skills_included = content.get("skills", [])
            
            return resume_text, skills_included
            
        except Exception as e:
            logger.error(f"AI resume generation failed: {str(e)}")
            fallback_resume = self._generate_fallback_resume(content, mode)
            fallback_skills = content.get("skills", [])
            return fallback_resume, fallback_skills
    
    def _analyze_resume_vs_job(self, resume_text: str, job_description: str) -> ResumeAnalysis:
        """Analyze resume against job description using AI."""
        if not self.llm:
            return self._generate_fallback_analysis(resume_text, job_description)
        
        try:
            system_prompt = """You are an ATS (Applicant Tracking System) analyzer. 
            Compare the resume against the job description and provide detailed analysis.
            
            Return JSON with:
            - ats_score: 0-100 (ATS compatibility)
            - keyword_match_score: 0-100 (keyword matching)
            - missing_skills: array of missing skills
            - recommended_modules: array of learning modules to improve match
            - strengths: array of resume strengths
            - improvement_areas: array of areas to improve
            
            Be specific and actionable."""
            
            analysis_prompt = f"""
Resume:
{resume_text}

Job Description:
{job_description}

Analyze the match and provide specific recommendations."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=analysis_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse AI response
            try:
                response_content = response.content
                if isinstance(response_content, str):
                    analysis_data = json.loads(response_content)
                    return ResumeAnalysis(**analysis_data)
                else:
                    logger.error("AI response content is not a string")
                    return self._generate_fallback_analysis(resume_text, job_description)
            except json.JSONDecodeError:
                logger.error("Failed to parse AI analysis response")
                return self._generate_fallback_analysis(resume_text, job_description)
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return self._generate_fallback_analysis(resume_text, job_description)
    
    def _improve_resume_with_ai(
        self,
        existing_resume: str,
        job_description: str,
        analysis: ResumeAnalysis
    ) -> str:
        """Generate improved resume based on analysis."""
        if not self.llm:
            return f"{existing_resume}\n\n[SUGGESTIONS BASED ON ANALYSIS]\nMissing Skills: {', '.join(analysis.missing_skills)}"
        
        try:
            improvement_prompt = f"""Improve this resume based on the job description and analysis:

Original Resume:
{existing_resume}

Job Description:
{job_description}

Missing Skills: {', '.join(analysis.missing_skills)}
Improvement Areas: {', '.join(analysis.improvement_areas)}

Generate an improved version that addresses the gaps while maintaining truthfulness."""
            
            messages = [
                SystemMessage(content="You are a professional resume writer. Improve resumes based on analysis."),
                HumanMessage(content=improvement_prompt)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content
            if isinstance(content, str):
                return content
            else:
                logger.warning("AI response content is not a string, converting")
                return str(content)
            
        except Exception as e:
            logger.error(f"Resume improvement failed: {str(e)}")
            return existing_resume
    
    def _generate_fallback_resume(self, content: Dict[str, Any], mode: str) -> str:
        """Generate fallback resume when AI is unavailable."""
        skills = content.get("skills", [])
        topics = content.get("topics", [])
        roadmap_title = content.get("roadmap_title", "Technical Learning")
        
        resume_template = f"""PROFESSIONAL SUMMARY
Motivated professional with hands-on experience in {roadmap_title.lower()}. 
Completed comprehensive training in modern development practices.

TECHNICAL SKILLS
{', '.join(skills) if skills else 'Various technical skills acquired through structured learning'}

RELEVANT EXPERIENCE
Learning & Development
• Completed structured learning program: {roadmap_title}
• Gained practical experience in: {', '.join(topics[:3]) if topics else 'core technical concepts'}
• Applied knowledge through hands-on projects and exercises

EDUCATION & CERTIFICATIONS
• Completed: {roadmap_title}
• Mode: {mode.title()} Learning Track
• Status: {"In Progress" if mode == "fast" else "Completed Modules"}
"""
        
        return resume_template
    
    def _generate_fallback_analysis(self, resume_text: str, job_description: str) -> ResumeAnalysis:
        """Generate fallback analysis when AI is unavailable."""
        # Simple keyword matching
        resume_lower = resume_text.lower()
        job_lower = job_description.lower()
        
        common_skills = ["python", "javascript", "react", "node", "sql", "api", "git"]
        missing_skills = []
        strengths = []
        
        for skill in common_skills:
            if skill in job_lower and skill not in resume_lower:
                missing_skills.append(skill.title())
            elif skill in resume_lower:
                strengths.append(skill.title())
        
        # Basic scoring
        keyword_matches = len(strengths)
        total_keywords = len(common_skills)
        keyword_score = int((keyword_matches / total_keywords) * 100) if total_keywords > 0 else 50
        ats_score = min(85, keyword_score + 15)  # Add base ATS score
        
        return ResumeAnalysis(
            ats_score=ats_score,
            keyword_match_score=keyword_score,
            missing_skills=missing_skills,
            recommended_modules=[f"Learn {skill}" for skill in missing_skills[:3]],
            strengths=strengths,
            improvement_areas=["Add more specific technical details", "Include measurable achievements"]
        )
    
    def _generate_minimal_resume(self, user_id: str) -> str:
        """Generate minimal resume for users with no completed modules."""
        return f"""PROFESSIONAL SUMMARY
Motivated professional beginning structured learning journey in technology.
Committed to continuous learning and skill development.

TECHNICAL SKILLS
Currently developing technical skills through comprehensive learning programs.

LEARNING & DEVELOPMENT
• Enrolled in structured technical learning program
• Focused on building foundational knowledge
• Committed to hands-on practical application

EDUCATION & TRAINING
• Active learner in technical skill development
• Study Mode: Progress-based learning approach
"""
    
    def _save_resume_to_db(
        self,
        db: Session,
        resume: GeneratedResume,
        job_description: Optional[str] = None,
        analysis: Optional[ResumeAnalysis] = None
    ) -> bool:
        """Save generated resume to database."""
        try:
            # Initialize resumes table if not exists
            self._initialize_resumes_table(db)
            
            analysis_json = analysis.dict() if analysis else None
            
            insert_query = text("""
                INSERT INTO user_resumes 
                (id, user_id, title, mode, roadmap_id, content, job_description, 
                 analysis_data, is_draft, created_at, updated_at)
                VALUES 
                (:id, :user_id, :title, :mode, :roadmap_id, :content, :job_description,
                 :analysis_data, :is_draft, :created_at, :updated_at)
            """)
            
            db.execute(insert_query, {
                "id": resume.id,
                "user_id": resume.user_id,
                "title": f"{resume.mode.title()} Mode Resume",
                "mode": resume.mode,
                "roadmap_id": resume.roadmap_id,
                "content": resume.resume_text,
                "job_description": job_description,
                "analysis_data": json.dumps(analysis_json) if analysis_json else None,
                "is_draft": resume.is_draft,
                "created_at": resume.created_at,
                "updated_at": resume.created_at
            })
            
            db.commit()
            logger.info(f"Saved resume {resume.id} for user {resume.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving resume: {str(e)}")
            db.rollback()
            return False
    
    def get_user_resumes(self, db: Session, user_id: str) -> ResumeListResponse:
        """Get all resumes for a user."""
        try:
            query = text("""
                SELECT id, user_id, title, mode, roadmap_id, content, job_description,
                       analysis_data, is_draft, created_at, updated_at
                FROM user_resumes 
                WHERE user_id = :user_id
                ORDER BY created_at DESC
            """)
            
            results = db.execute(query, {"user_id": user_id}).fetchall()
            
            resumes = []
            mode_counts = {"study": 0, "fast": 0, "analyzer": 0}
            
            for row in results:
                analysis_data = json.loads(row.analysis_data) if row.analysis_data else None
                
                resume = SavedResume(
                    id=row.id,
                    user_id=row.user_id,
                    title=row.title,
                    mode=row.mode,
                    roadmap_id=row.roadmap_id,
                    content=row.content,
                    job_description=row.job_description,
                    analysis_data=analysis_data,
                    is_draft=row.is_draft,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
                
                resumes.append(resume)
                if row.mode in mode_counts:
                    mode_counts[row.mode] += 1
            
            return ResumeListResponse(
                resumes=resumes,
                total_count=len(resumes),
                study_mode_count=mode_counts["study"],
                fast_mode_count=mode_counts["fast"],
                analyzer_mode_count=mode_counts["analyzer"]
            )
            
        except Exception as e:
            logger.error(f"Error getting user resumes: {str(e)}")
            return ResumeListResponse(resumes=[], total_count=0)
    
    def _initialize_resumes_table(self, db: Session) -> bool:
        """Initialize the user_resumes table if it doesn't exist."""
        try:
            # Start fresh transaction
            db.rollback()
            
            create_table_query_pg = text("""
                CREATE TABLE IF NOT EXISTS user_resumes (
                    id VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    title VARCHAR(500) NOT NULL,
                    mode VARCHAR(50) NOT NULL,
                    roadmap_id VARCHAR(255),
                    content TEXT NOT NULL,
                    job_description TEXT,
                    analysis_data JSONB,
                    is_draft BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            """)
            
            db.execute(create_table_query_pg)
            
            # Create indexes separately for PostgreSQL
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_user_resumes_user_id ON user_resumes (user_id)"))
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_user_resumes_mode ON user_resumes (mode)"))
            
            db.commit()
            logger.info("User resumes table initialized successfully (PostgreSQL)")
            return True
                
        except Exception as pg_error:
            logger.error(f"Error initializing resumes table: {str(pg_error)}")
            db.rollback()
            return False


# Global instance
resume_service = ResumeService()