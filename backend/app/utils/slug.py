"""
Slug generation utilities.
"""
import re
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text


def generate_slug(text: str) -> str:
    """
    Generate a URL-friendly slug from text.
    """
    # Convert to lowercase
    slug = text.lower()
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug


async def generate_unique_slug(
    db: AsyncSession,
    table: str,
    column: str,
    base_slug: str,
    max_length: int = 100
) -> str:
    """
    Generate a unique slug by appending numbers if needed.
    """
    slug = base_slug[:max_length]
    
    # Check if slug is unique
    result = await db.execute(
        text(f"SELECT COUNT(*) FROM {table} WHERE {column} = :slug"),
        {"slug": slug}
    )
    count = result.scalar()
    
    if count == 0:
        return slug
    
    # Find unique slug by appending counter
    counter = 1
    while True:
        candidate = f"{base_slug[:max_length-len(str(counter))-1]}-{counter}"
        result = await db.execute(
            text(f"SELECT COUNT(*) FROM {table} WHERE {column} = :slug"),
            {"slug": candidate}
        )
        count = result.scalar()
        if count == 0:
            return candidate
        counter += 1