"""
Multi-Track Roadmap Merge & Timeline Planning Service
Combines multiple roadmaps with intelligent deduplication and scheduling
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import uuid
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import and_

from services.sync_roadmap_service import SyncRoadmapService


class RoadmapMergeService:
    def __init__(self):
        self.roadmap_service = SyncRoadmapService()
    
    def merge_roadmaps(
        self, 
        roadmap_ids: List[str], 
        user_id: str,
        schedule_mode: str = "none",
        calendar_view: bool = False,
        daily_study_hours: float = 1.0
    ) -> Dict[str, Any]:
        """
        Merge multiple roadmaps into one unified roadmap with optional scheduling
        
        Args:
            roadmap_ids: List of roadmap IDs to merge
            user_id: User performing the merge
            schedule_mode: "none", "auto", or "manual"
            calendar_view: Whether to generate calendar view
            daily_study_hours: Hours per day for auto scheduling
        
        Returns:
            Merged roadmap data with optional calendar schedule
        """
        
        # Fetch all roadmaps to merge
        source_roadmaps = []
        for roadmap_id in roadmap_ids:
            roadmap = self.roadmap_service.get_roadmap(roadmap_id, user_id)
            if roadmap:
                source_roadmaps.append(roadmap)
        
        if len(source_roadmaps) < 2:
            raise ValueError("At least 2 roadmaps required for merging")
        
        # Perform intelligent merge
        merged_roadmap = self._perform_intelligent_merge(source_roadmaps, user_id)
        
        # Generate calendar if requested
        calendar_data = None
        if schedule_mode == "auto" and calendar_view:
            calendar_data = self._generate_auto_schedule(
                merged_roadmap, daily_study_hours
            )
            merged_roadmap['calendar'] = calendar_data
        
        # Save merged roadmap to database
        saved_roadmap = self._save_merged_roadmap(merged_roadmap, roadmap_ids, user_id)
        
        return {
            "merged_roadmap": saved_roadmap,
            "source_count": len(source_roadmaps),
            "schedule_mode": schedule_mode,
            "calendar_enabled": calendar_view
        }
    
    def _perform_intelligent_merge(
        self, 
        source_roadmaps: List[Dict], 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Intelligently merge roadmaps with deduplication and optimization
        """
        
        # Collect all branches from source roadmaps
        all_branches = []
        roadmap_titles = []
        total_source_duration = 0
        
        for roadmap in source_roadmaps:
            roadmap_titles.append(roadmap['title'])
            total_source_duration += roadmap.get('estimatedDuration', 0)
            
            if 'branches' in roadmap:
                for branch in roadmap['branches']:
                    all_branches.append({
                        **branch,
                        'source_roadmap': roadmap['title']
                    })
        
        # Deduplicate branches by similarity
        merged_branches = self._deduplicate_branches(all_branches)
        
        # Calculate final duration
        total_duration = sum(
            branch.get('estimatedDuration', 0) 
            for branch in merged_branches
        )
        
        # Create merged roadmap structure
        merged_title = f"Merged: {' + '.join(roadmap_titles[:3])}"
        if len(roadmap_titles) > 3:
            merged_title += f" (+{len(roadmap_titles) - 3} more)"
        
        merged_roadmap = {
            "id": f"mrg_{uuid.uuid4().hex[:8]}",
            "title": merged_title,
            "description": f"Intelligent merge of {len(source_roadmaps)} learning tracks",
            "estimatedDuration": total_duration,
            "branches": merged_branches,
            "mergedFrom": [r['id'] for r in source_roadmaps],
            "customizedFrom": None,  # This becomes the new base
            "createdAt": datetime.now().isoformat(),
            "userId": user_id
        }
        
        return merged_roadmap
    
    def _deduplicate_branches(self, all_branches: List[Dict]) -> List[Dict]:
        """
        Remove duplicate branches based on title similarity and content overlap
        """
        
        merged_branches = []
        processed_titles = set()
        
        # Group branches by similarity
        branch_groups = defaultdict(list)
        
        for branch in all_branches:
            # Simple title-based grouping (can be enhanced with ML similarity)
            title_key = self._normalize_title(branch['title'])
            branch_groups[title_key].append(branch)
        
        # Merge similar branches
        for title_key, similar_branches in branch_groups.items():
            if len(similar_branches) == 1:
                # No duplicates, add as-is
                merged_branches.append(similar_branches[0])
            else:
                # Merge similar branches
                merged_branch = self._merge_similar_branches(similar_branches)
                merged_branches.append(merged_branch)
        
        return merged_branches
    
    def _merge_similar_branches(self, similar_branches: List[Dict]) -> Dict:
        """
        Merge branches with similar content, preserving core videos
        """
        
        # Use the first branch as base
        base_branch = similar_branches[0].copy()
        
        # Collect all videos from similar branches
        all_videos = []
        video_titles_seen = set()
        
        for branch in similar_branches:
            if 'videos' in branch:
                for video in branch['videos']:
                    video_title = self._normalize_title(video['title'])
                    
                    # Preserve core videos and deduplicate optional ones
                    if video.get('isCore', False) or video_title not in video_titles_seen:
                        all_videos.append(video)
                        video_titles_seen.add(video_title)
        
        # Update merged branch
        base_branch['videos'] = all_videos
        base_branch['estimatedDuration'] = sum(
            video.get('duration', 0) for video in all_videos
        )
        
        # Update description to reflect merge
        source_roadmaps = list(set(
            branch.get('source_roadmap', 'Unknown') 
            for branch in similar_branches
        ))
        base_branch['description'] += f" (Merged from: {', '.join(source_roadmaps)})"
        
        return base_branch
    
    def _normalize_title(self, title: str) -> str:
        """
        Normalize title for similarity comparison
        """
        return title.lower().strip().replace(' ', '').replace('-', '').replace('_', '')
    
    def _generate_auto_schedule(
        self, 
        merged_roadmap: Dict, 
        daily_study_hours: float
    ) -> Dict[str, List[Dict]]:
        """
        Generate automatic 30/60/90-day calendar schedule
        """
        
        calendar = {}
        current_date = datetime.now().date()
        daily_study_seconds = int(daily_study_hours * 3600)
        
        # Prioritize core videos first
        all_videos = []
        for branch in merged_roadmap.get('branches', []):
            for video in branch.get('videos', []):
                all_videos.append({
                    **video,
                    'branch_id': branch['id'],
                    'branch_title': branch['title']
                })
        
        # Sort by core videos first, then by priority/duration
        all_videos.sort(key=lambda v: (
            not v.get('isCore', False),  # Core videos first
            v.get('duration', 0)  # Shorter videos first within each group
        ))
        
        # Distribute videos across calendar days
        video_index = 0
        day_offset = 0
        
        while video_index < len(all_videos) and day_offset < 90:  # 90-day limit
            schedule_date = current_date + timedelta(days=day_offset)
            date_str = schedule_date.isoformat()
            
            # Skip weekends (optional - can be configurable)
            if schedule_date.weekday() >= 5:  # Saturday=5, Sunday=6
                day_offset += 1
                continue
            
            daily_videos = []
            daily_duration = 0
            
            # Fill the day with videos up to daily study limit
            while (video_index < len(all_videos) and 
                   daily_duration < daily_study_seconds):
                
                video = all_videos[video_index]
                video_duration = video.get('duration', 0)
                
                # If video fits in remaining time, add it
                if daily_duration + video_duration <= daily_study_seconds:
                    daily_videos.append({
                        'id': video['id'],
                        'title': video['title'],
                        'duration': video_duration,
                        'isCore': video.get('isCore', False),
                        'branch_title': video['branch_title'],
                        'scheduled_time': '09:00'  # Default start time
                    })
                    daily_duration += video_duration
                    video_index += 1
                else:
                    # Video too long for remaining time, move to next day
                    break
            
            if daily_videos:
                calendar[date_str] = daily_videos
            
            day_offset += 1
        
        return calendar
    
    def _save_merged_roadmap(
        self, 
        merged_roadmap: Dict, 
        source_roadmap_ids: List[str], 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Save merged roadmap to database with proper lineage tracking
        """
        
        try:
            # Prepare roadmap data for database
            roadmap_data = {
                'title': merged_roadmap['title'],
                'description': merged_roadmap['description'],
                'user_input': f"Merged from roadmaps: {', '.join(source_roadmap_ids)}",
                'estimated_duration': merged_roadmap['estimatedDuration'],
                'branches': json.dumps(merged_roadmap['branches']),
                'merged_from': json.dumps(source_roadmap_ids),
                'customized_from': None,  # New base roadmap
                'user_id': user_id
            }
            
            # Use existing roadmap service to save
            saved_roadmap = self.roadmap_service.create_roadmap(roadmap_data)
            
            # Add calendar data if present
            if 'calendar' in merged_roadmap:
                saved_roadmap['calendar'] = merged_roadmap['calendar']
            
            return saved_roadmap
            
        except Exception as e:
            raise Exception(f"Failed to save merged roadmap: {str(e)}")
    
    def get_user_roadmaps_for_merge(self, user_id: str) -> List[Dict]:
        """
        Get user's roadmaps available for merging
        """
        
        roadmaps = self.roadmap_service.get_user_roadmaps(user_id)
        
        # Filter out already merged roadmaps to prevent recursive merging
        mergeable_roadmaps = []
        for roadmap in roadmaps:
            # Only include roadmaps that aren't already merges of other roadmaps
            merged_from = roadmap.get('merged_from')
            if not merged_from or merged_from == '[]':
                mergeable_roadmaps.append({
                    'id': roadmap['id'],
                    'title': roadmap['title'],
                    'description': roadmap.get('description', ''),
                    'estimatedDuration': roadmap.get('estimated_duration', 0),
                    'branchCount': len(json.loads(roadmap.get('branches', '[]')))
                })
        
        return mergeable_roadmaps
    
    def get_merge_preview(
        self, 
        roadmap_ids: List[str], 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Generate a preview of what the merge would look like without saving
        """
        
        # Fetch roadmaps
        source_roadmaps = []
        for roadmap_id in roadmap_ids:
            roadmap = self.roadmap_service.get_roadmap(roadmap_id, user_id)
            if roadmap:
                source_roadmaps.append(roadmap)
        
        if len(source_roadmaps) < 2:
            raise ValueError("At least 2 roadmaps required for preview")
        
        # Generate preview without saving
        preview = self._perform_intelligent_merge(source_roadmaps, user_id)
        
        # Add merge statistics
        original_duration = sum(r.get('estimatedDuration', 0) for r in source_roadmaps)
        duration_saved = original_duration - preview['estimatedDuration']
        
        original_branch_count = sum(
            len(r.get('branches', [])) for r in source_roadmaps
        )
        final_branch_count = len(preview['branches'])
        
        return {
            'preview': preview,
            'statistics': {
                'original_roadmaps': len(source_roadmaps),
                'original_duration': original_duration,
                'final_duration': preview['estimatedDuration'],
                'duration_saved': duration_saved,
                'original_branches': original_branch_count,
                'final_branches': final_branch_count,
                'efficiency_gain': round((duration_saved / original_duration) * 100, 1) if original_duration > 0 else 0
            }
        }