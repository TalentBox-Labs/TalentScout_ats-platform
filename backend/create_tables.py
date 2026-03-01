#!/usr/bin/env python3
"""Script to create database tables."""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base
from app.config import settings
from sqlalchemy import create_engine

# Import all models
print("Importing models...")
from app.models import (
    user, job, candidate, application, interview, assessment,
    communication, integration
)
print("Models imported successfully")

print(f"Tables registered with Base: {Base.metadata.tables.keys()}")

def create_tables():
    print(f"Database URL: {settings.database_url}")
    # Convert async URL to sync URL
    sync_url = settings.database_url
    if sync_url.startswith("sqlite+aiosqlite://"):
        sync_url = sync_url.replace("sqlite+aiosqlite://", "sqlite:///")
    
    print(f"Sync URL: {sync_url}")
    engine = create_engine(sync_url, echo=True)
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()