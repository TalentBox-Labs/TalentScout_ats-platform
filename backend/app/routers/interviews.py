"""
Interview management router.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/interviews", tags=["interviews"])