"""
Main entry point for AI Code Reviewer application.

This module provides the FastAPI application instance and startup configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings

# Create FastAPI application instance
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered In-Depth Code Review System",
    version="0.1.0",
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    """
    Root endpoint providing basic API information.
    
    Returns:
        dict: Basic API information and status.
    """
    return {
        "message": "AI Code Reviewer API",
        "version": "0.1.0",
        "status": "running",
        "docs_url": "/docs",
    }


@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint for monitoring.
    
    Returns:
        dict: Health status information.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "0.1.0",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    ) 