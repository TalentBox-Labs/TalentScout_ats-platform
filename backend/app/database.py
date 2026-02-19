"""Database connection and session management."""
import subprocess
import sys
import os
from typing import AsyncGenerator
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from contextvars import ContextVar
from app.models.user import User
from app.utils.security import get_password_hash
from sqlalchemy import select

# Context variable for test sessions
test_db_session: ContextVar[AsyncSession] = ContextVar('test_db_session', default=None)

# Global for test session
_test_session = None

# Flag to indicate testing mode
_testing_mode = os.getenv('TESTING', 'false').lower() == 'true'

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
    # In testing mode, always use the test session if available
    if _testing_mode:
        if _test_session is not None:
            yield _test_session
            return
        test_session = test_db_session.get()
        if test_session is not None:
            yield test_session
            return
    
    # Check if we have a test session from context or global
    test_session = test_db_session.get()
    if test_session is not None:
        yield test_session
        return
    
    # Check global test session
    if _test_session is not None:
        yield _test_session
        return
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def seed_super_admin() -> None:
    """Seed the super admin user if it doesn't exist."""
    try:
        async with AsyncSessionLocal() as session:
            # Check if super admin already exists
            result = await session.execute(
                select(User).where(User.email == "thomas@workcrew.ai")
            )
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                print("Super admin user already exists")
                return
            
            # Create super admin user
            super_admin = User(
                email="thomas@workcrew.ai",
                hashed_password=get_password_hash("admin123"),  # Default password
                first_name="Thomas",
                last_name="Admin",
                is_active=True,
                is_verified=True,
                is_super_admin=True,
            )
            
            session.add(super_admin)
            await session.commit()
            print("✅ Super admin user seeded: thomas@workcrew.ai")
            
    except Exception as e:
        print(f"Error seeding super admin: {e}")


async def init_db() -> None:
    """Initialize database connection and seed initial data."""
    try:
        # For SQLite, the database file will be created automatically
        # Just test the connection
        async with AsyncSessionLocal() as session:
            await session.execute(sa.text("SELECT 1"))
        print("Database connection established successfully")
        
        # Seed super admin user
        await seed_super_admin()
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise


async def close_db() -> None:
    """Close database connection."""
    await engine.dispose()
