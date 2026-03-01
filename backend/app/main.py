"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting ATS Platform API...")
    try:
        await init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")
        print("🚀 Continuing with application startup...")
    
    yield
    
    # Shutdown
    print("👋 Shutting down ATS Platform API...")
    await close_db()
    print("✅ Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-First Application Tracking System API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to ATS Platform API",
        "version": settings.app_version,
        "docs": "/docs",
    }


# Import and include routers
from app.routers import (
    auth,
    organizations,
    jobs,
    candidates,
    applications,
    ai,
    assessments,
    interviews,
    communications,
    analytics,
    settings as settings_router,
    onboarding,
    integrations,
)

app.include_router(auth.router, prefix=f"{settings.api_v1_prefix}")
app.include_router(organizations.router, prefix=f"{settings.api_v1_prefix}")
app.include_router(jobs.router, prefix=f"{settings.api_v1_prefix}")
app.include_router(candidates.router, prefix=f"{settings.api_v1_prefix}")
app.include_router(applications.router, prefix=f"{settings.api_v1_prefix}")
app.include_router(ai.router, prefix=f"{settings.api_v1_prefix}")
app.include_router(assessments.router, prefix=f"{settings.api_v1_prefix}")
app.include_router(interviews.router, prefix=f"{settings.api_v1_prefix}")
app.include_router(communications.router, prefix=f"{settings.api_v1_prefix}")
app.include_router(analytics.router, prefix=f"{settings.api_v1_prefix}")
app.include_router(settings_router.router, prefix=f"{settings.api_v1_prefix}")
app.include_router(onboarding.router, prefix=f"{settings.api_v1_prefix}")
app.include_router(integrations.router, prefix=f"{settings.api_v1_prefix}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
