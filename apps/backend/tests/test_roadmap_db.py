"""
Tests for roadmap database operations.
"""

import pytest
import asyncio
from typing import List
from unittest.mock import patch
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from db.models import RoadmapDB, AsyncBase
from services.roadmap_service import RoadmapService
from models.roadmap import RoadmapResponse, RoadmapBranch, VideoModule

# Test database URL - using SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_roadmaps.db"


@pytest.fixture
async def test_db():
    """Create test database and session."""
    # Create test engine
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(AsyncBase.metadata.create_all)
    
    # Provide session
    async with TestSessionLocal() as session:
        yield session
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(AsyncBase.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
def sample_roadmap():
    """Create a sample roadmap for testing."""
    return RoadmapResponse(
        id="test_roadmap_123",
        title="Learn Python Programming",
        total_duration=3600,
        branches=[
            RoadmapBranch(
                id="branch_1",
                title="Python Basics",
                videos=[
                    VideoModule(id="video_1", title="Introduction to Python", duration=900),
                    VideoModule(id="video_2", title="Variables and Data Types", duration=1200)
                ]
            ),
            RoadmapBranch(
                id="branch_2", 
                title="Advanced Python",
                videos=[
                    VideoModule(id="video_3", title="Object-Oriented Programming", duration=1500)
                ]
            )
        ]
    )


@pytest.mark.asyncio
async def test_save_roadmap(test_db: AsyncSession, sample_roadmap: RoadmapResponse):
    """Test saving a roadmap to the database."""
    user_id = "test_user_123"
    
    # Save roadmap
    saved_ids = await RoadmapService.save_roadmaps(test_db, [sample_roadmap], user_id)
    
    # Verify saved
    assert len(saved_ids) == 1
    assert saved_ids[0] == sample_roadmap.id
    
    # Check in database
    roadmap_db = await test_db.get(RoadmapDB, sample_roadmap.id)
    assert roadmap_db is not None
    assert roadmap_db.user_id == user_id
    assert roadmap_db.title == sample_roadmap.title
    assert roadmap_db.total_duration == sample_roadmap.total_duration
    assert len(roadmap_db.branches) == 2


@pytest.mark.asyncio
async def test_get_roadmaps_by_user(test_db: AsyncSession, sample_roadmap: RoadmapResponse):
    """Test retrieving roadmaps by user ID."""
    user_id = "test_user_456"
    
    # Save sample roadmap
    await RoadmapService.save_roadmaps(test_db, [sample_roadmap], user_id)
    
    # Retrieve roadmaps
    roadmaps = await RoadmapService.get_roadmaps_by_user(test_db, user_id)
    
    # Verify results
    assert len(roadmaps) == 1
    retrieved_roadmap = roadmaps[0]
    assert retrieved_roadmap.id == sample_roadmap.id
    assert retrieved_roadmap.title == sample_roadmap.title
    assert retrieved_roadmap.total_duration == sample_roadmap.total_duration
    assert len(retrieved_roadmap.branches) == 2
    
    # Check branch structure
    branch = retrieved_roadmap.branches[0]
    assert branch.title == "Python Basics"
    assert len(branch.videos) == 2
    
    video = branch.videos[0]
    assert video.title == "Introduction to Python"
    assert video.duration == 900


@pytest.mark.asyncio
async def test_get_roadmap_by_id(test_db: AsyncSession, sample_roadmap: RoadmapResponse):
    """Test retrieving a specific roadmap by ID."""
    user_id = "test_user_789"
    
    # Save sample roadmap
    await RoadmapService.save_roadmaps(test_db, [sample_roadmap], user_id)
    
    # Retrieve by ID
    retrieved_roadmap = await RoadmapService.get_roadmap_by_id(test_db, sample_roadmap.id)
    
    # Verify result
    assert retrieved_roadmap is not None
    assert retrieved_roadmap.id == sample_roadmap.id
    assert retrieved_roadmap.title == sample_roadmap.title


@pytest.mark.asyncio
async def test_get_nonexistent_roadmap(test_db: AsyncSession):
    """Test retrieving a non-existent roadmap."""
    non_existent_id = "non_existent_roadmap"
    
    # Try to retrieve
    result = await RoadmapService.get_roadmap_by_id(test_db, non_existent_id)
    
    # Should return None
    assert result is None


@pytest.mark.asyncio
async def test_delete_roadmap(test_db: AsyncSession, sample_roadmap: RoadmapResponse):
    """Test deleting a roadmap."""
    user_id = "test_user_delete"
    
    # Save sample roadmap
    await RoadmapService.save_roadmaps(test_db, [sample_roadmap], user_id)
    
    # Verify it exists
    retrieved = await RoadmapService.get_roadmap_by_id(test_db, sample_roadmap.id)
    assert retrieved is not None
    
    # Delete roadmap
    success = await RoadmapService.delete_roadmap(test_db, sample_roadmap.id)
    assert success is True
    
    # Verify it's gone
    retrieved = await RoadmapService.get_roadmap_by_id(test_db, sample_roadmap.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_save_multiple_roadmaps(test_db: AsyncSession):
    """Test saving multiple roadmaps for the same user."""
    user_id = "test_user_multiple"
    
    # Create multiple roadmaps
    roadmaps = [
        RoadmapResponse(
            id=f"roadmap_{i}",
            title=f"Roadmap {i}",
            total_duration=1800,
            branches=[
                RoadmapBranch(
                    id=f"branch_{i}",
                    title=f"Branch {i}",
                    videos=[
                        VideoModule(id=f"video_{i}", title=f"Video {i}", duration=1800)
                    ]
                )
            ]
        )
        for i in range(3)
    ]
    
    # Save all roadmaps
    saved_ids = await RoadmapService.save_roadmaps(test_db, roadmaps, user_id)
    assert len(saved_ids) == 3
    
    # Retrieve all roadmaps for user
    retrieved_roadmaps = await RoadmapService.get_roadmaps_by_user(test_db, user_id)
    assert len(retrieved_roadmaps) == 3
    
    # Verify titles
    titles = [r.title for r in retrieved_roadmaps]
    assert "Roadmap 0" in titles
    assert "Roadmap 1" in titles
    assert "Roadmap 2" in titles


@pytest.mark.asyncio
async def test_pagination(test_db: AsyncSession):
    """Test pagination in get_roadmaps_by_user."""
    user_id = "test_user_pagination"
    
    # Create multiple roadmaps
    roadmaps = [
        RoadmapResponse(
            id=f"roadmap_{i}",
            title=f"Roadmap {i}",
            total_duration=600,
            branches=[
                RoadmapBranch(
                    id=f"branch_{i}",
                    title=f"Branch {i}",
                    videos=[
                        VideoModule(id=f"video_{i}", title=f"Video {i}", duration=600)
                    ]
                )
            ]
        )
        for i in range(5)
    ]
    
    # Save all roadmaps
    await RoadmapService.save_roadmaps(test_db, roadmaps, user_id)
    
    # Test pagination
    first_page = await RoadmapService.get_roadmaps_by_user(test_db, user_id, limit=2, offset=0)
    assert len(first_page) == 2
    
    second_page = await RoadmapService.get_roadmaps_by_user(test_db, user_id, limit=2, offset=2)
    assert len(second_page) == 2
    
    third_page = await RoadmapService.get_roadmaps_by_user(test_db, user_id, limit=2, offset=4)
    assert len(third_page) == 1
    
    # Verify no overlap
    first_titles = {r.title for r in first_page}
    second_titles = {r.title for r in second_page}
    assert len(first_titles & second_titles) == 0  # No intersection


if __name__ == "__main__":
    # Run tests manually if needed
    pytest.main([__file__, "-v"])