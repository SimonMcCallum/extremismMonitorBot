"""
Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment}")
    print(f"Debug: {settings.debug}")

    # Initialize database
    await init_db()
    print("Database initialized")

    yield

    # Shutdown
    print("Shutting down...")
    await close_db()
    print("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered Discord bot API for extremism monitoring and community management",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-11-20T00:00:00Z"
    }


@app.get(f"{settings.api_prefix}/status")
async def api_status():
    """API status endpoint."""
    return {
        "api": "operational",
        "version": settings.app_version,
        "environment": settings.environment
    }


# Include API routers (to be added)
# from api.v1 import servers, users, risks, analytics
# app.include_router(servers.router, prefix=f"{settings.api_prefix}/servers", tags=["servers"])
# app.include_router(users.router, prefix=f"{settings.api_prefix}/users", tags=["users"])
# app.include_router(risks.router, prefix=f"{settings.api_prefix}/risks", tags=["risks"])
# app.include_router(analytics.router, prefix=f"{settings.api_prefix}/analytics", tags=["analytics"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
