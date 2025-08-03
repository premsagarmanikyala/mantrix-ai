"""
Learning path recommendation service using AI analysis and user progress data.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from models.recommendation import (
    RecommendationRequest, RecommendationResponse, RecommendedBranch, 
    RecommendedModule, UserSkillProfile, SkillGapAnalysis
)
from services.progress_service import ProgressService
from services.roadmap_agent import RoadmapAgent
from openai import OpenAI
import os

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating personalized learning path recommendations."""
    
    def __init__(self):
        self.progress_service = ProgressService()
        self.roadmap_agent = RoadmapAgent()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
    
    def generate_recommendations(
        self,
        db: Session,
        user_id: str,
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """
        Generate personalized learning recommendations based on user data and preferences.
        
        Args:
            db: Database session
            user_id: User identifier
            request: Recommendation request parameters
            
        Returns:
            RecommendationResponse with personalized suggestions
        """
        try:
            logger.info(f"Generating {request.mode} recommendations for user {user_id}")
            
            # Step 1: Build user skill profile
            user_profile = self._build_user_profile(db, user_id)
            logger.info(f"Built user profile: {len(user_profile.completed_skills)} skills, {user_profile.total_study_time}s study time")
            
            # Step 2: Perform analysis based on mode
            if request.mode == "gap":
                analysis = self._analyze_skill_gaps(user_profile, request.target_job_description)
                context = f"Gap analysis for target role with {analysis.match_percentage:.1f}% match"
            elif request.mode == "resume":
                analysis = self._analyze_resume_enhancement(user_profile, request.existing_resume)
                context = "Resume enhancement analysis"
            else:  # interest mode
                analysis = self._analyze_interest_based(user_profile, request.skill_interests)
                context = "Interest-based learning path analysis"
            
            # Step 3: Generate AI-powered recommendations
            recommendations = self._generate_ai_recommendations(
                user_profile, analysis, request, context
            )
            
            # Step 4: Enhance with fallback if AI fails
            if not recommendations:
                logger.warning("AI recommendations failed, using fallback system")
                recommendations = self._generate_fallback_recommendations(user_profile, request)
            
            # Step 5: Build response
            response = RecommendationResponse(
                user_id=user_id,
                mode=request.mode,
                recommendations=recommendations,
                analysis_summary=self._generate_analysis_summary(user_profile, analysis, request.mode),
                confidence_score=self._calculate_confidence_score(user_profile, recommendations),
                next_steps=self._generate_next_steps(recommendations)
            )
            
            logger.info(f"Generated {len(recommendations)} recommendations with {response.confidence_score:.2f} confidence")
            return response
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            # Return basic fallback recommendations
            return self._generate_basic_fallback(user_id, request)
    
    def _build_user_profile(self, db: Session, user_id: str) -> UserSkillProfile:
        """Build comprehensive user skill profile from progress data."""
        try:
            # Get user's progress data
            progress_query = text("""
                SELECT roadmap_id, branch_id, module_id, duration_completed, completed_at
                FROM user_progress 
                WHERE user_id = :user_id 
                ORDER BY completed_at DESC
            """)
            
            progress_results = db.execute(progress_query, {"user_id": user_id}).fetchall()
            
            # Get user's roadmaps
            roadmaps_query = text("""
                SELECT id, user_input, branches_data, created_at
                FROM roadmaps 
                WHERE user_id = :user_id 
                ORDER BY created_at DESC
            """)
            
            roadmap_results = db.execute(roadmaps_query, {"user_id": user_id}).fetchall()
            
            # Extract skills from completed modules
            completed_skills = set()
            in_progress_skills = set()
            total_study_time = 0
            active_roadmaps = []
            
            # Process progress data
            for progress in progress_results:
                total_study_time += progress[3]  # duration_completed
                # Extract skills from module/branch IDs (simplified)
                completed_skills.add(f"skill_{progress[2]}")  # module_id based skill
            
            # Process roadmap data
            for roadmap in roadmap_results:
                active_roadmaps.append(roadmap[0])
                if roadmap[2]:  # branches_data
                    try:
                        branches_data = json.loads(roadmap[2]) if isinstance(roadmap[2], str) else roadmap[2]
                        for branch in branches_data:
                            for video in branch.get("videos", []):
                                if video.get("id") not in [p[2] for p in progress_results]:
                                    in_progress_skills.add(f"skill_{video['id']}")
                    except:
                        pass
            
            # Calculate completion rate
            total_modules = len(completed_skills) + len(in_progress_skills)
            completion_rate = len(completed_skills) / total_modules if total_modules > 0 else 0.0
            
            return UserSkillProfile(
                completed_skills=list(completed_skills),
                in_progress_skills=list(in_progress_skills),
                skill_levels={skill: "intermediate" for skill in completed_skills},
                total_study_time=total_study_time,
                active_roadmaps=active_roadmaps,
                completion_rate=completion_rate
            )
            
        except Exception as e:
            logger.error(f"Error building user profile: {str(e)}")
            return UserSkillProfile()
    
    def _analyze_skill_gaps(self, profile: UserSkillProfile, job_description: Optional[str]) -> SkillGapAnalysis:
        """Analyze skill gaps based on job description."""
        if not job_description:
            return SkillGapAnalysis(
                current_skills=profile.completed_skills,
                priority_areas=["Full-stack development", "System design", "Problem solving"]
            )
        
        # Extract skills from job description (simplified approach)
        jd_lower = job_description.lower()
        required_skills = []
        
        # Common tech skills mapping
        skill_keywords = {
            "react": "React.js",
            "python": "Python",
            "javascript": "JavaScript",
            "node": "Node.js",
            "sql": "SQL",
            "database": "Database Design",
            "api": "API Development",
            "docker": "Docker",
            "aws": "AWS",
            "git": "Git",
            "typescript": "TypeScript",
            "mongodb": "MongoDB",
            "postgresql": "PostgreSQL",
            "machine learning": "Machine Learning",
            "data science": "Data Science"
        }
        
        for keyword, skill in skill_keywords.items():
            if keyword in jd_lower:
                required_skills.append(skill)
        
        # Calculate gaps
        current_skills = profile.completed_skills
        missing_skills = [skill for skill in required_skills if skill not in current_skills]
        
        match_percentage = (len(required_skills) - len(missing_skills)) / len(required_skills) * 100 if required_skills else 0
        
        return SkillGapAnalysis(
            required_skills=required_skills,
            current_skills=current_skills,
            missing_skills=missing_skills,
            match_percentage=match_percentage,
            priority_areas=missing_skills[:3] if missing_skills else ["Advanced topics"]
        )
    
    def _analyze_resume_enhancement(self, profile: UserSkillProfile, resume: Optional[str]) -> SkillGapAnalysis:
        """Analyze resume for enhancement opportunities."""
        if not resume:
            return SkillGapAnalysis(
                current_skills=profile.completed_skills,
                priority_areas=["Portfolio development", "Technical writing", "Leadership skills"]
            )
        
        # Simple resume analysis
        resume_lower = resume.lower()
        missing_areas = []
        
        if "project" not in resume_lower:
            missing_areas.append("Project portfolio")
        if "leadership" not in resume_lower:
            missing_areas.append("Leadership experience")
        if "certification" not in resume_lower:
            missing_areas.append("Professional certifications")
        
        return SkillGapAnalysis(
            current_skills=profile.completed_skills,
            missing_skills=missing_areas,
            priority_areas=missing_areas[:3]
        )
    
    def _analyze_interest_based(self, profile: UserSkillProfile, interests: List[str]) -> SkillGapAnalysis:
        """Analyze learning opportunities based on user interests."""
        return SkillGapAnalysis(
            current_skills=profile.completed_skills,
            priority_areas=interests[:3] if interests else ["Full-stack development", "Data science", "DevOps"]
        )
    
    def _generate_ai_recommendations(
        self,
        profile: UserSkillProfile,
        analysis: SkillGapAnalysis,
        request: RecommendationRequest,
        context: str
    ) -> List[RecommendedBranch]:
        """Generate AI-powered learning recommendations."""
        if not self.openai_client:
            logger.warning("OpenAI client not available, using fallback")
            return []
        
        try:
            # Build AI prompt
            prompt = self._build_recommendation_prompt(profile, analysis, request, context)
            
            # Call OpenAI GPT-4
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert learning path advisor. Provide detailed, actionable learning recommendations based on user progress and goals. Respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.7
            )
            
            # Parse AI response
            ai_content = response.choices[0].message.content
            ai_data = json.loads(ai_content)
            
            # Convert to RecommendedBranch objects
            recommendations = []
            for rec in ai_data.get("recommendations", []):
                modules = [
                    RecommendedModule(
                        title=mod.get("title", ""),
                        duration=mod.get("duration", 600),
                        difficulty=mod.get("difficulty", "intermediate"),
                        priority=mod.get("priority", 1)
                    ) for mod in rec.get("modules", [])
                ]
                
                branch = RecommendedBranch(
                    id=f"rec_{rec.get('title', 'branch').lower().replace(' ', '_')}_{datetime.now().strftime('%s')}",
                    title=rec.get("title", ""),
                    reason=rec.get("reason", ""),
                    estimated_duration=sum(m.duration for m in modules),
                    difficulty=rec.get("difficulty", "intermediate"),
                    prerequisites=rec.get("prerequisites", []),
                    modules=modules,
                    completion_benefit=rec.get("completion_benefit", "Enhanced skills and knowledge")
                )
                recommendations.append(branch)
            
            logger.info(f"Generated {len(recommendations)} AI recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating AI recommendations: {str(e)}")
            return []
    
    def _build_recommendation_prompt(
        self,
        profile: UserSkillProfile,
        analysis: SkillGapAnalysis,
        request: RecommendationRequest,
        context: str
    ) -> str:
        """Build detailed prompt for AI recommendation generation."""
        
        prompt = f"""
        Generate personalized learning path recommendations based on the following user data:

        USER PROFILE:
        - Completed skills: {', '.join(profile.completed_skills[:10])}
        - Study time: {profile.total_study_time // 3600} hours
        - Completion rate: {profile.completion_rate:.1%}
        - Active roadmaps: {len(profile.active_roadmaps)}

        ANALYSIS CONTEXT: {context}
        RECOMMENDATION MODE: {request.mode}

        SKILL ANALYSIS:
        - Required skills: {', '.join(analysis.required_skills[:10])}
        - Missing skills: {', '.join(analysis.missing_skills[:10])}
        - Priority areas: {', '.join(analysis.priority_areas)}
        """
        
        if request.target_job_description:
            prompt += f"\nTARGET JOB: {request.target_job_description[:500]}..."
        
        if request.existing_resume:
            prompt += f"\nCURRENT RESUME: {request.existing_resume[:300]}..."
        
        prompt += """

        Please provide 2-3 learning branch recommendations in JSON format:

        {
          "recommendations": [
            {
              "title": "Branch title",
              "reason": "Why this branch is recommended",
              "difficulty": "beginner|intermediate|advanced",
              "prerequisites": ["List of prerequisites"],
              "completion_benefit": "What user will gain",
              "modules": [
                {
                  "title": "Module title",
                  "duration": 600,
                  "difficulty": "intermediate",
                  "priority": 1
                }
              ]
            }
          ]
        }

        Focus on practical, career-relevant skills that fill identified gaps.
        """
        
        return prompt
    
    def _generate_fallback_recommendations(
        self,
        profile: UserSkillProfile,
        request: RecommendationRequest
    ) -> List[RecommendedBranch]:
        """Generate fallback recommendations when AI is unavailable."""
        
        logger.info("Generating fallback recommendations")
        
        fallback_branches = []
        
        # Common recommendations based on mode
        if request.mode == "gap":
            fallback_branches = [
                {
                    "title": "System Design Fundamentals",
                    "reason": "Essential for senior developer roles and technical interviews",
                    "modules": [
                        {"title": "Scalability Principles", "duration": 900},
                        {"title": "Database Design Patterns", "duration": 1200},
                        {"title": "Microservices Architecture", "duration": 1500}
                    ]
                },
                {
                    "title": "Advanced Problem Solving",
                    "reason": "Critical thinking skills valued by all employers",
                    "modules": [
                        {"title": "Algorithm Optimization", "duration": 800},
                        {"title": "Data Structure Deep Dive", "duration": 1000},
                        {"title": "Performance Analysis", "duration": 700}
                    ]
                }
            ]
        elif request.mode == "resume":
            fallback_branches = [
                {
                    "title": "Portfolio Development",
                    "reason": "Build impressive projects to showcase your skills",
                    "modules": [
                        {"title": "Full-Stack Project Planning", "duration": 600},
                        {"title": "UI/UX Best Practices", "duration": 800},
                        {"title": "Deployment & DevOps", "duration": 1000}
                    ]
                },
                {
                    "title": "Technical Communication",
                    "reason": "Articulate your technical expertise effectively",
                    "modules": [
                        {"title": "Technical Writing", "duration": 500},
                        {"title": "Code Documentation", "duration": 400},
                        {"title": "Presentation Skills", "duration": 600}
                    ]
                }
            ]
        else:  # interest
            fallback_branches = [
                {
                    "title": "Modern Web Development",
                    "reason": "Stay current with latest web technologies",
                    "modules": [
                        {"title": "React Advanced Patterns", "duration": 1000},
                        {"title": "GraphQL & APIs", "duration": 800},
                        {"title": "Performance Optimization", "duration": 900}
                    ]
                },
                {
                    "title": "Cloud & DevOps",
                    "reason": "High-demand skills in modern development",
                    "modules": [
                        {"title": "AWS Fundamentals", "duration": 1200},
                        {"title": "Docker & Containers", "duration": 800},
                        {"title": "CI/CD Pipelines", "duration": 700}
                    ]
                }
            ]
        
        # Convert to RecommendedBranch objects
        recommendations = []
        for i, branch_data in enumerate(fallback_branches):
            modules = [
                RecommendedModule(
                    title=mod["title"],
                    duration=mod["duration"],
                    difficulty="intermediate",
                    priority=1
                ) for mod in branch_data["modules"]
            ]
            
            branch = RecommendedBranch(
                id=f"fallback_{request.mode}_{i}_{datetime.now().strftime('%s')}",
                title=branch_data["title"],
                reason=branch_data["reason"],
                estimated_duration=sum(m.duration for m in modules),
                difficulty="intermediate",
                prerequisites=[],
                modules=modules,
                completion_benefit=f"Master {branch_data['title'].lower()} to advance your career"
            )
            recommendations.append(branch)
        
        return recommendations[:2]  # Return top 2 recommendations
    
    def _generate_analysis_summary(
        self,
        profile: UserSkillProfile,
        analysis: SkillGapAnalysis,
        mode: str
    ) -> str:
        """Generate analysis summary for the user."""
        
        if mode == "gap":
            return f"Analyzed {len(analysis.required_skills)} required skills. You have {analysis.match_percentage:.1f}% match with target role. Focus on {', '.join(analysis.priority_areas[:2])} to close key gaps."
        elif mode == "resume":
            return f"Reviewed your background against {len(profile.completed_skills)} completed skills. Identified {len(analysis.priority_areas)} enhancement areas to strengthen your profile."
        else:
            return f"Based on your {profile.completion_rate:.1%} completion rate and {profile.total_study_time // 3600} hours of study, recommended paths align with your interests and career growth."
    
    def _calculate_confidence_score(
        self,
        profile: UserSkillProfile,
        recommendations: List[RecommendedBranch]
    ) -> float:
        """Calculate confidence score for recommendations."""
        
        base_confidence = 0.7
        
        # Adjust based on user data quality
        if len(profile.completed_skills) > 5:
            base_confidence += 0.1
        if profile.completion_rate > 0.5:
            base_confidence += 0.1
        if len(recommendations) >= 2:
            base_confidence += 0.05
        
        return min(0.95, base_confidence)
    
    def _generate_next_steps(self, recommendations: List[RecommendedBranch]) -> List[str]:
        """Generate actionable next steps for the user."""
        
        if not recommendations:
            return ["Explore available learning paths", "Complete a skills assessment"]
        
        next_steps = []
        if recommendations:
            next_steps.append(f"Start with '{recommendations[0].title}' - {recommendations[0].reason}")
            
        if len(recommendations) > 1:
            next_steps.append(f"Consider '{recommendations[1].title}' as your next focus area")
        
        next_steps.extend([
            "Set aside dedicated study time each week",
            "Track your progress and celebrate milestones",
            "Apply new skills in practice projects"
        ])
        
        return next_steps[:4]  # Return top 4 steps
    
    def _generate_basic_fallback(
        self,
        user_id: str,
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """Generate basic fallback response when all else fails."""
        
        basic_module = RecommendedModule(
            title="Skill Development",
            duration=600,
            difficulty="intermediate",
            priority=1
        )
        
        basic_branch = RecommendedBranch(
            id=f"basic_fallback_{datetime.now().strftime('%s')}",
            title="Continue Learning",
            reason="Keep building your skills with consistent practice",
            estimated_duration=600,
            difficulty="intermediate",
            prerequisites=[],
            modules=[basic_module],
            completion_benefit="Continued skill development and growth"
        )
        
        return RecommendationResponse(
            user_id=user_id,
            mode=request.mode,
            recommendations=[basic_branch],
            analysis_summary="Unable to perform detailed analysis. Here are general recommendations.",
            confidence_score=0.5,
            next_steps=["Continue with your current learning path"]
        )