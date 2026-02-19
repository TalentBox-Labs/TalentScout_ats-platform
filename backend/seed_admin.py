#!/usr/bin/env python3
"""
Script to seed the super admin user.
Run this after database migrations are applied.
"""
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.user import User
from app.utils.security import get_password_hash

# Create sync engine for seeding
sync_database_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
engine = create_engine(sync_database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_super_admin():
    """Seed the super admin user if it doesn't exist."""
    try:
        with SessionLocal() as session:
            # Check if super admin already exists
            result = session.execute(
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
            session.commit()
            print("✅ Super admin user seeded: thomas@workcrew.ai")
            print("   Default password: admin123")
            print("   Please change the password after first login!")

    except Exception as e:
        print(f"Error seeding super admin: {e}")
        raise


if __name__ == "__main__":
    seed_super_admin()