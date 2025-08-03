"""
Database configuration and connection management for roadmaps.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

# Create async engine for PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mantrix.db")

# Convert sync PostgreSQL URL to async if needed and handle SSL parameters
if DATABASE_URL.startswith("postgresql://"):
    # Replace postgresql:// with postgresql+asyncpg://
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    # For asyncpg, keep sslmode=require as it's supported
    # No need to change SSL parameters
elif DATABASE_URL.startswith("sqlite"):
    DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

async_engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Base for async models
AsyncBase = declarative_base()


async def get_async_db():
    """Dependency for async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_async_tables():
    """Create all async tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(AsyncBase.metadata.create_all)