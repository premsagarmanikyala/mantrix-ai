"""
Service for integrating with external open APIs for roadmap generation.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ExternalRoadmapSource(BaseModel):
    """Model for external roadmap source information."""
    id: str
    name: str
    description: str
    base_url: str
    is_active: bool = True


class ExternalRoadmapStep(BaseModel):
    """Model for individual steps in external roadmaps."""
    title: str
    description: str
    type: str
    estimated_time: int  # in minutes


class ExternalRoadmap(BaseModel):
    """Model for roadmaps from external sources."""
    id: str
    title: str
    description: str
    source: str
    source_url: Optional[str] = None
    topics: List[str] = []
    difficulty: Optional[str] = None
    estimated_duration: Optional[int] = None  # in minutes
    steps: List[ExternalRoadmapStep] = []


class ExternalRoadmapService:
    """Service for fetching roadmaps from external open APIs."""
    
    def __init__(self):
        self.sources = [
            ExternalRoadmapSource(
                id="github_awesome",
                name="GitHub Awesome Lists",
                description="Community-curated learning roadmaps from GitHub",
                base_url="https://api.github.com/repos"
            ),
            ExternalRoadmapSource(
                id="roadmap_sh",
                name="Roadmap.sh",
                description="Developer roadmaps for various technologies",
                base_url="https://roadmap.sh/roadmaps"
            ),
            ExternalRoadmapSource(
                id="freecodecamp",
                name="FreeCodeCamp",
                description="Free coding bootcamp curriculum roadmaps",
                base_url="https://api.freecodecamp.org"
            )
        ]
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_available_sources(self) -> List[ExternalRoadmapSource]:
        """Get list of available external roadmap sources."""
        return [source for source in self.sources if source.is_active]
    
    async def search_roadmaps(self, query: str, sources: Optional[List[str]] = None) -> List[ExternalRoadmap]:
        """
        Search for roadmaps across multiple external sources.
        
        Args:
            query: Search query (e.g., "javascript", "python", "web development")
            sources: List of source IDs to search (None for all sources)
            
        Returns:
            List of external roadmaps matching the query
        """
        if sources is None:
            sources = [source.id for source in self.sources if source.is_active]
        
        tasks = []
        for source_id in sources:
            if source_id == "github_awesome":
                tasks.append(self._search_github_awesome(query))
            elif source_id == "roadmap_sh":
                tasks.append(self._search_roadmap_sh(query))
            elif source_id == "freecodecamp":
                tasks.append(self._search_freecodecamp(query))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results and filter out exceptions
        roadmaps = []
        for result in results:
            if isinstance(result, list):
                roadmaps.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"Source search failed: {str(result)}")
        
        return roadmaps
    
    async def _search_github_awesome(self, query: str) -> List[ExternalRoadmap]:
        """Search GitHub awesome lists for learning resources."""
        try:
            # Search for awesome lists related to the query
            search_url = f"https://api.github.com/search/repositories"
            params = {
                "q": f"awesome {query} topic:awesome-list",
                "sort": "stars",
                "order": "desc",
                "per_page": 5
            }
            
            response = await self.client.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            roadmaps = []
            for repo in data.get("items", []):
                # Get repository contents to analyze structure
                try:
                    readme_url = f"https://api.github.com/repos/{repo['full_name']}/readme"
                    readme_response = await self.client.get(readme_url)
                    
                    if readme_response.status_code == 200:
                        readme_data = readme_response.json()
                        
                        roadmap = ExternalRoadmap(
                            id=f"github_{repo['id']}",
                            title=f"Awesome {query.title()} - {repo['name']}",
                            description=repo.get("description", "Community-curated learning resources"),
                            source="GitHub Awesome Lists",
                            source_url=repo["html_url"],
                            topics=repo.get("topics", []),
                            difficulty="Mixed",
                            estimated_duration=240,  # 4 hours estimated reading time
                            steps=[
                                ExternalRoadmapStep(
                                    title="Explore Repository",
                                    description="Browse the curated list of resources",
                                    type="reading",
                                    estimated_time=60
                                ),
                                ExternalRoadmapStep(
                                    title="Select Learning Resources",
                                    description="Choose specific resources based on your goals",
                                    type="planning",
                                    estimated_time=30
                                ),
                                ExternalRoadmapStep(
                                    title="Follow Learning Path",
                                    description="Work through selected resources systematically",
                                    type="practice",
                                    estimated_time=150
                                )
                            ]
                        )
                        roadmaps.append(roadmap)
                except Exception as e:
                    logger.warning(f"Failed to get README for {repo['full_name']}: {str(e)}")
                    continue
            
            return roadmaps
            
        except Exception as e:
            logger.error(f"GitHub awesome search failed: {str(e)}")
            return []
    
    async def _search_roadmap_sh(self, query: str) -> List[ExternalRoadmap]:
        """Search roadmap.sh for technology roadmaps."""
        # Note: roadmap.sh doesn't have a public API, so we'll provide static popular roadmaps
        # that match common queries
        try:
            roadmap_mapping = {
                "frontend": {
                    "title": "Frontend Developer Roadmap",
                    "description": "Step-by-step guide to becoming a modern frontend developer",
                    "topics": ["html", "css", "javascript", "react", "vue"],
                    "steps": [
                        {"title": "Learn HTML", "description": "Semantic HTML and accessibility", "type": "learning", "estimated_time": 40},
                        {"title": "Learn CSS", "description": "Styling, layouts, and responsive design", "type": "learning", "estimated_time": 60},
                        {"title": "Learn JavaScript", "description": "Programming fundamentals and DOM manipulation", "type": "learning", "estimated_time": 120},
                        {"title": "Choose a Framework", "description": "React, Vue, or Angular", "type": "learning", "estimated_time": 80},
                        {"title": "Build Projects", "description": "Apply skills in real projects", "type": "practice", "estimated_time": 200}
                    ]
                },
                "backend": {
                    "title": "Backend Developer Roadmap",
                    "description": "Complete guide to backend development",
                    "topics": ["python", "nodejs", "databases", "apis", "deployment"],
                    "steps": [
                        {"title": "Choose a Language", "description": "Python, Node.js, or Java", "type": "learning", "estimated_time": 60},
                        {"title": "Learn Databases", "description": "SQL and NoSQL databases", "type": "learning", "estimated_time": 80},
                        {"title": "Build APIs", "description": "REST and GraphQL APIs", "type": "learning", "estimated_time": 100},
                        {"title": "Learn DevOps", "description": "Deployment and monitoring", "type": "learning", "estimated_time": 120},
                        {"title": "Build Full Applications", "description": "End-to-end backend projects", "type": "practice", "estimated_time": 240}
                    ]
                },
                "devops": {
                    "title": "DevOps Roadmap",
                    "description": "Path to becoming a DevOps engineer",
                    "topics": ["linux", "docker", "kubernetes", "ci/cd", "monitoring"],
                    "steps": [
                        {"title": "Learn Linux", "description": "Command line and system administration", "type": "learning", "estimated_time": 80},
                        {"title": "Learn Containerization", "description": "Docker and container orchestration", "type": "learning", "estimated_time": 60},
                        {"title": "Learn Cloud Platforms", "description": "AWS, GCP, or Azure", "type": "learning", "estimated_time": 120},
                        {"title": "Learn CI/CD", "description": "Automation and deployment pipelines", "type": "learning", "estimated_time": 80},
                        {"title": "Learn Monitoring", "description": "Logging, metrics, and alerting", "type": "learning", "estimated_time": 60}
                    ]
                }
            }
            
            roadmaps = []
            query_lower = query.lower()
            
            for key, roadmap_data in roadmap_mapping.items():
                if (key in query_lower or 
                    any(topic in query_lower for topic in roadmap_data["topics"]) or
                    any(topic in key for topic in query_lower.split())):
                    
                    total_time = sum(step["estimated_time"] for step in roadmap_data["steps"])
                    
                    roadmap = ExternalRoadmap(
                        id=f"roadmapsh_{key}",
                        title=roadmap_data["title"],
                        description=roadmap_data["description"],
                        source="Roadmap.sh",
                        source_url=f"https://roadmap.sh/{key}",
                        topics=roadmap_data["topics"],
                        difficulty="Beginner to Advanced",
                        estimated_duration=total_time,
                        steps=[
                            ExternalRoadmapStep(
                                title=step["title"],
                                description=step["description"],
                                type=step["type"],
                                estimated_time=step["estimated_time"]
                            ) for step in roadmap_data["steps"]
                        ]
                    )
                    roadmaps.append(roadmap)
            
            return roadmaps
            
        except Exception as e:
            logger.error(f"Roadmap.sh search failed: {str(e)}")
            return []
    
    async def _search_freecodecamp(self, query: str) -> List[ExternalRoadmap]:
        """Search FreeCodeCamp curriculum for relevant courses."""
        try:
            # FreeCodeCamp curriculum mapping
            curriculum_mapping = {
                "javascript": {
                    "title": "JavaScript Algorithms and Data Structures",
                    "description": "Learn JavaScript fundamentals and algorithmic thinking",
                    "topics": ["javascript", "algorithms", "data-structures"],
                    "steps": [
                        {"title": "Basic JavaScript", "description": "Variables, functions, and control flow", "type": "interactive", "estimated_time": 180},
                        {"title": "ES6", "description": "Modern JavaScript features", "type": "interactive", "estimated_time": 120},
                        {"title": "Regular Expressions", "description": "Pattern matching and text processing", "type": "interactive", "estimated_time": 60},
                        {"title": "Data Structures", "description": "Objects, arrays, and advanced structures", "type": "interactive", "estimated_time": 90},
                        {"title": "Algorithms", "description": "Problem-solving and algorithmic thinking", "type": "interactive", "estimated_time": 150}
                    ]
                },
                "python": {
                    "title": "Scientific Computing with Python",
                    "description": "Learn Python for data analysis and scientific computing",
                    "topics": ["python", "data-analysis", "scientific-computing"],
                    "steps": [
                        {"title": "Python Basics", "description": "Syntax, data types, and control structures", "type": "interactive", "estimated_time": 120},
                        {"title": "Data Analysis", "description": "NumPy, Pandas, and data manipulation", "type": "interactive", "estimated_time": 180},
                        {"title": "Data Visualization", "description": "Matplotlib and Seaborn", "type": "interactive", "estimated_time": 90},
                        {"title": "Machine Learning", "description": "Introduction to ML with Python", "type": "interactive", "estimated_time": 150},
                        {"title": "Projects", "description": "Real-world data science projects", "type": "project", "estimated_time": 240}
                    ]
                },
                "web": {
                    "title": "Responsive Web Design",
                    "description": "Learn HTML, CSS, and responsive design principles",
                    "topics": ["html", "css", "responsive-design", "accessibility"],
                    "steps": [
                        {"title": "Learn HTML", "description": "Structure and semantic markup", "type": "interactive", "estimated_time": 90},
                        {"title": "Learn CSS", "description": "Styling and layout techniques", "type": "interactive", "estimated_time": 120},
                        {"title": "Visual Design", "description": "Typography, color theory, and design principles", "type": "interactive", "estimated_time": 60},
                        {"title": "Accessibility", "description": "Creating inclusive web experiences", "type": "interactive", "estimated_time": 45},
                        {"title": "Responsive Design", "description": "Mobile-first and flexible layouts", "type": "interactive", "estimated_time": 75}
                    ]
                }
            }
            
            roadmaps = []
            query_lower = query.lower()
            
            for key, curriculum_data in curriculum_mapping.items():
                if (key in query_lower or 
                    any(topic in query_lower for topic in curriculum_data["topics"]) or
                    "freecodecamp" in query_lower or
                    "fcc" in query_lower):
                    
                    total_time = sum(step["estimated_time"] for step in curriculum_data["steps"])
                    
                    roadmap = ExternalRoadmap(
                        id=f"fcc_{key}",
                        title=f"FreeCodeCamp: {curriculum_data['title']}",
                        description=curriculum_data["description"],
                        source="FreeCodeCamp",
                        source_url=f"https://www.freecodecamp.org/learn/{key.replace('_', '-')}",
                        topics=curriculum_data["topics"],
                        difficulty="Beginner",
                        estimated_duration=total_time,
                        steps=[
                            ExternalRoadmapStep(
                                title=step["title"],
                                description=step["description"],
                                type=step["type"],
                                estimated_time=step["estimated_time"]
                            ) for step in curriculum_data["steps"]
                        ]
                    )
                    roadmaps.append(roadmap)
            
            return roadmaps
            
        except Exception as e:
            logger.error(f"FreeCodeCamp search failed: {str(e)}")
            return []
    
    async def get_roadmap_details(self, roadmap_id: str) -> Optional[ExternalRoadmap]:
        """Get detailed information about a specific external roadmap."""
        try:
            # Parse roadmap ID to determine source
            if roadmap_id.startswith("github_"):
                return await self._get_github_roadmap_details(roadmap_id)
            elif roadmap_id.startswith("roadmapsh_"):
                return await self._get_roadmapsh_details(roadmap_id)
            elif roadmap_id.startswith("fcc_"):
                return await self._get_fcc_details(roadmap_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get roadmap details for {roadmap_id}: {str(e)}")
            return None
    
    async def _get_github_roadmap_details(self, roadmap_id: str) -> Optional[ExternalRoadmap]:
        """Get detailed GitHub roadmap information."""
        # Implementation would fetch more detailed information from GitHub API
        # For now, return basic info
        return None
    
    async def _get_roadmapsh_details(self, roadmap_id: str) -> Optional[ExternalRoadmap]:
        """Get detailed roadmap.sh information."""
        # Implementation would scrape or use API if available
        return None
    
    async def _get_fcc_details(self, roadmap_id: str) -> Optional[ExternalRoadmap]:
        """Get detailed FreeCodeCamp curriculum information."""
        # Implementation would fetch from FreeCodeCamp API
        return None
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Global instance
external_roadmap_service = ExternalRoadmapService()