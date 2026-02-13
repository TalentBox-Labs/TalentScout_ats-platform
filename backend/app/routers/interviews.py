"""
Interview management router.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/interviews", tags=["interviews"])