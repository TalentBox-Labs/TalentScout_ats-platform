#!/usr/bin/env python3
"""Script to initialize database tables."""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine
from app.database import Base
from app.config import settings

def init_db_sync():
    """Initialize database tables synchronously."""
    # Convert async URL to sync URL for table creation
    sync_url = settings.database_url
    if sync_url.startswith("sqlite+aiosqlite://"):
        sync_url = sync_url.replace("sqlite+aiosqlite://", "sqlite:///")
    elif sync_url.startswith("postgresql+asyncpg://"):
        sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")

    print(f"Creating tables with URL: {sync_url}")

    # Create engine
    engine = create_engine(sync_url, echo=True)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db_sync()</content>
<parameter name="filePath">h:\OneDrive\Documents\GitHub\TalentScout_ats-platform\backend\init_tables.py