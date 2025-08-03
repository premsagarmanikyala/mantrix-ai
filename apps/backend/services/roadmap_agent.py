"""
AI-powered roadmap generation service using OpenAI GPT-4 and LangChain.
"""

import json
import logging
import os
import uuid
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser

from models.roadmap import RoadmapResponse, RoadmapBranch, VideoModule

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RoadmapAgent:
    """AI agent for generating structured learning roadmaps."""
    
    def __init__(self):
        """Initialize the roadmap agent with OpenAI configuration."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
            
        # Initialize OpenAI chat model - the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=self.api_key,
            temperature=0.7,
            max_tokens=2000
        )
        
        # Initialize JSON output parser
        self.json_parser = JsonOutputParser()
        
        # System prompt template
        self.system_prompt = """You are an expert curriculum designer. Given this user input: "{user_input}", generate 2 to 3 structured learning roadmaps.

Each roadmap should include:
- A title
- A list of 2 to 4 branches
- Each branch should contain 2 to 3 video modules, each with:
  - Title
  - Duration in seconds (between 300 and 1800)
  - is_core: true for essential videos, false for optional/advanced videos

Mark foundational and prerequisite videos as core=true. Advanced, specialized, or optional content should be core=false.

Return valid JSON only. No explanations or extra text."""

    def generate_roadmaps(self, user_input: str) -> tuple[List[RoadmapResponse], List[RoadmapBranch]]:
        """
        Generate 2-3 structured learning roadmaps based on user input.
        
        Args:
            user_input: The user's input describing what they want to learn
            
        Returns:
            Tuple of (List of RoadmapResponse objects, List of unique RoadmapBranch objects)
            
        Raises:
            Exception: If AI generation or parsing fails
        """
        try:
            logger.info(f"Generating roadmaps for user input: {user_input}")
            
            # Create messages for the chat model
            messages = [
                SystemMessage(content=self.system_prompt.format(user_input=user_input)),
                HumanMessage(content=f"Generate learning roadmaps for: {user_input}")
            ]
            
            # Call OpenAI API
            response = self.llm.invoke(messages)
            logger.info(f"OpenAI API response received. Content length: {len(response.content)}")
            
            # Log token usage if available
            if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
                token_usage = response.response_metadata['token_usage']
                logger.info(f"Token usage - Total: {token_usage.get('total_tokens')}, "
                          f"Prompt: {token_usage.get('prompt_tokens')}, "
                          f"Completion: {token_usage.get('completion_tokens')}")
            
            # Parse JSON response
            roadmaps_data = self._parse_ai_response(response.content)
            
            # Convert to Pydantic models
            roadmaps = self._convert_to_roadmap_models(roadmaps_data)
            
            # Generate branches library (de-duplicated branches)
            branches_library = self._generate_branches_library(roadmaps)
            
            logger.info(f"Successfully generated {len(roadmaps)} roadmaps with {len(branches_library)} unique branches")
            return roadmaps, branches_library
            
        except Exception as e:
            logger.error(f"Error generating roadmaps: {str(e)}")
            raise Exception(f"Failed to generate roadmaps: {str(e)}")
    
    def _parse_ai_response(self, response_content: str) -> List[Dict[str, Any]]:
        """
        Parse AI response and extract roadmaps data.
        
        Args:
            response_content: Raw response content from AI
            
        Returns:
            List of roadmap dictionaries
        """
        try:
            # Clean the response content - remove any markdown formatting
            content = response_content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            data = json.loads(content)
            
            # Handle different response formats
            if isinstance(data, list):
                roadmaps_data = data
            elif isinstance(data, dict):
                if 'roadmaps' in data:
                    roadmaps_data = data['roadmaps']
                else:
                    roadmaps_data = [data]
            else:
                raise ValueError("Unexpected response format")
            
            # Validate we have 2-3 roadmaps
            if not isinstance(roadmaps_data, list) or len(roadmaps_data) < 2 or len(roadmaps_data) > 3:
                raise ValueError(f"Expected 2-3 roadmaps, got {len(roadmaps_data) if isinstance(roadmaps_data, list) else 'invalid format'}")
            
            return roadmaps_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            logger.error(f"Response content: {response_content}")
            raise Exception(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Response parsing error: {str(e)}")
            raise Exception(f"Failed to parse AI response: {str(e)}")
    
    def _convert_to_roadmap_models(self, roadmaps_data: List[Dict[str, Any]]) -> List[RoadmapResponse]:
        """
        Convert parsed data to Pydantic roadmap models.
        
        Args:
            roadmaps_data: List of roadmap dictionaries
            
        Returns:
            List of RoadmapResponse objects
        """
        roadmaps = []
        
        for i, roadmap_data in enumerate(roadmaps_data):
            try:
                # Generate IDs if missing
                roadmap_id = roadmap_data.get('id', f"roadmap_{uuid.uuid4().hex[:8]}")
                title = roadmap_data.get('title', f"Learning Roadmap {i+1}")
                
                # Process branches
                branches_data = roadmap_data.get('branches', [])
                branches = []
                total_duration = 0
                
                for j, branch_data in enumerate(branches_data):
                    branch_id = branch_data.get('id', f"branch_{uuid.uuid4().hex[:8]}")
                    branch_title = branch_data.get('title', f"Branch {j+1}")
                    
                    # Process videos
                    videos_data = branch_data.get('videos', branch_data.get('modules', []))
                    videos = []
                    
                    for k, video_data in enumerate(videos_data):
                        video_id = video_data.get('id', f"video_{uuid.uuid4().hex[:8]}")
                        video_title = video_data.get('title', f"Video {k+1}")
                        duration = video_data.get('duration', 600)  # Default 10 minutes
                        is_core = video_data.get('is_core', False)  # Default to false
                        
                        # Ensure duration is within bounds
                        duration = max(300, min(1800, duration))
                        total_duration += duration
                        
                        video = VideoModule(
                            id=video_id,
                            title=video_title,
                            duration=duration,
                            is_core=is_core
                        )
                        videos.append(video)
                    
                    branch = RoadmapBranch(
                        id=branch_id,
                        title=branch_title,
                        videos=videos
                    )
                    branches.append(branch)
                
                roadmap = RoadmapResponse(
                    id=roadmap_id,
                    title=title,
                    total_duration=total_duration,
                    branches=branches
                )
                roadmaps.append(roadmap)
                
            except Exception as e:
                logger.error(f"Error converting roadmap {i}: {str(e)}")
                raise Exception(f"Failed to convert roadmap data: {str(e)}")
        
        return roadmaps
    
    def _generate_fallback_roadmaps(self, user_input: str) -> tuple[List[RoadmapResponse], List[RoadmapBranch]]:
        """
        Generate fallback roadmaps when AI fails.
        This should only be used as a last resort.
        
        Args:
            user_input: The user's input
            
        Returns:
            List of basic roadmap responses
        """
        logger.warning("Generating fallback roadmaps due to AI failure")
        
        fallback_roadmaps = [
            RoadmapResponse(
                id=f"fallback_roadmap_1_{uuid.uuid4().hex[:8]}",
                title=f"Introduction to {user_input}",
                total_duration=3600,  # 1 hour total
                branches=[
                    RoadmapBranch(
                        id=f"branch_1_{uuid.uuid4().hex[:8]}",
                        title="Fundamentals",
                        videos=[
                            VideoModule(id=f"video_1_{uuid.uuid4().hex[:8]}", title="Getting Started", duration=900, is_core=True),
                            VideoModule(id=f"video_2_{uuid.uuid4().hex[:8]}", title="Core Concepts", duration=1200, is_core=True)
                        ]
                    ),
                    RoadmapBranch(
                        id=f"branch_2_{uuid.uuid4().hex[:8]}",
                        title="Practical Application",
                        videos=[
                            VideoModule(id=f"video_3_{uuid.uuid4().hex[:8]}", title="Hands-on Practice", duration=1500, is_core=False)
                        ]
                    )
                ]
            ),
            RoadmapResponse(
                id=f"fallback_roadmap_2_{uuid.uuid4().hex[:8]}",
                title=f"Advanced {user_input}",
                total_duration=4200,  # 70 minutes total
                branches=[
                    RoadmapBranch(
                        id=f"branch_3_{uuid.uuid4().hex[:8]}",
                        title="Advanced Topics",
                        videos=[
                            VideoModule(id=f"video_4_{uuid.uuid4().hex[:8]}", title="Advanced Techniques", duration=1800, is_core=False),
                            VideoModule(id=f"video_5_{uuid.uuid4().hex[:8]}", title="Best Practices", duration=1200, is_core=True),
                            VideoModule(id=f"video_6_{uuid.uuid4().hex[:8]}", title="Case Studies", duration=1200, is_core=False)
                        ]
                    )
                ]
            )
        ]
        
        # Generate branches library from fallback roadmaps
        branches_library = self._generate_branches_library(fallback_roadmaps)
        
        return fallback_roadmaps, branches_library
    
    def _generate_branches_library(self, roadmaps: List[RoadmapResponse]) -> List[RoadmapBranch]:
        """
        Generate a de-duplicated library of all branches across roadmaps.
        
        Args:
            roadmaps: List of roadmap responses
            
        Returns:
            De-duplicated list of unique branches
        """
        seen_branch_titles = set()
        branches_library = []
        
        for roadmap in roadmaps:
            for branch in roadmap.branches:
                # Use title as deduplication key (could also use content similarity)
                if branch.title not in seen_branch_titles:
                    seen_branch_titles.add(branch.title)
                    branches_library.append(branch)
        
        return branches_library
    
    def get_branches_by_ids(self, branch_ids: List[str], all_roadmaps: List[RoadmapResponse]) -> List[RoadmapBranch]:
        """
        Get branches by their IDs from a collection of roadmaps.
        
        Args:
            branch_ids: List of branch IDs to retrieve
            all_roadmaps: All available roadmaps to search through
            
        Returns:
            List of matching branches
        """
        found_branches = []
        
        for roadmap in all_roadmaps:
            for branch in roadmap.branches:
                if branch.id in branch_ids:
                    found_branches.append(branch)
        
        return found_branches


# Global instance
roadmap_agent = RoadmapAgent()