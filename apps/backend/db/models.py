"""
Database models for roadmap storage.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List

from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator, TEXT
import json

from db.database import AsyncBase


class JSONType(TypeDecorator):
    """Custom JSON type that works with both PostgreSQL JSONB and SQLite TEXT."""
    
    impl = TEXT
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(TEXT())

    def process_bind_param(self, value, dialect):
        if value is not None:
            if dialect.name == 'postgresql':
                return value
            else:
                return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if dialect.name == 'postgresql':
                return value
            else:
                return json.loads(value)
        return value


class RoadmapDB(AsyncBase):
    """Database model for storing generated roadmaps."""
    
    __tablename__ = "roadmaps"
    
    id = Column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()), 
        index=True
    )
    user_id = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    total_duration = Column(Integer, nullable=False)  # Duration in seconds
    branches = Column(JSONType, nullable=False)  # JSONB for PostgreSQL, TEXT for SQLite
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "total_duration": self.total_duration,
            "branches": self.branches,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_roadmap_response(cls, roadmap_response, user_id: str):
        """Create RoadmapDB instance from RoadmapResponse."""
        # Convert branches to JSON-serializable format
        branches_data = []
        for branch in roadmap_response.branches:
            branch_data = {
                "id": branch.id,
                "title": branch.title,
                "videos": [
                    {
                        "id": video.id,
                        "title": video.title,
                        "duration": video.duration
                    }
                    for video in branch.videos
                ]
            }
            branches_data.append(branch_data)
        
        return cls(
            id=roadmap_response.id,
            user_id=user_id,
            title=roadmap_response.title,
            total_duration=roadmap_response.total_duration,
            branches=branches_data
        )