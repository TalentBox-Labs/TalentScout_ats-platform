"""Database connection and session management."""
import subprocess
import sys
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Alias for backward compatibility
async_session_maker = AsyncSessionLocal

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database using Alembic migrations or create tables directly."""
    try:
        # Run Alembic migrations to create/update database schema
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Database migrations completed successfully: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Database migrations failed: {e.stderr}")
        print("Attempting to create tables directly...")

        # Fallback: Create tables directly using SQLAlchemy
        try:
            # Import all models to ensure they are registered with Base
            from app.models import (
                user, job, candidate, application, interview, assessment,
                communication, integration
            )
            
            # Convert async URL to sync URL for table creation
            sync_url = settings.database_url
            if sync_url.startswith("sqlite+aiosqlite://"):
                sync_url = sync_url.replace("sqlite+aiosqlite://", "sqlite:///")
            elif sync_url.startswith("postgresql+asyncpg://"):
                sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")

            from sqlalchemy import create_engine
            sync_engine = create_engine(sync_url, echo=settings.debug)
            Base.metadata.create_all(bind=sync_engine)
            print("Database tables created successfully using SQLAlchemy!")
        except Exception as create_e:
            print(f"Failed to create tables directly: {create_e}")
            print("Continuing with application startup...")


async def close_db() -> None:
    """Close database connection."""
    await engine.dispose()
