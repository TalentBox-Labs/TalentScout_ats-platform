import asyncio
import sys
sys.path.insert(0, 'backend')

# Load environment variables
from dotenv import load_dotenv
load_dotenv('backend/.env')

from sqlalchemy import select
from app.database import get_db
from app.models.user import User, OrganizationMember
from app.utils.security import verify_password

async def test_login():
    async for db in get_db():
        # Find user by email
        result = await db.execute(select(User).where(User.email == "thomas@workcrew.ai"))
        user = result.scalar_one_or_none()
        print(f"User found: {user}")

        if user:
            password_check = verify_password("admin123", user.hashed_password)
            print(f"Password check: {password_check}")

            # Get user's default organization
            result = await db.execute(
                select(OrganizationMember)
                .where(OrganizationMember.user_id == user.id, OrganizationMember.is_active == True)
                .limit(1)
            )
            member = result.scalar_one_or_none()
            print(f"Member found: {member}")
            org_id = str(member.organization_id) if member else None
            print(f"Org ID: {org_id}")

        break

asyncio.run(test_login())