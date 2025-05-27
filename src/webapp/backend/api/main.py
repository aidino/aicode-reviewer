"""
FastAPI main application for AI Code Reviewer backend.

This module provides the main FastAPI application instance with all routes
and middleware configuration for the backend API.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .scan_routes import router as scan_router
from .dashboard_routes import router as dashboard_router
from .feedback_routes import router as feedback_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title="AI Code Reviewer API",
    description="Backend API for AI-Powered In-Depth Code Review System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scan_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")


@app.get("/")
async def root() -> JSONResponse:
    """
    Root endpoint providing basic API information.
    
    Returns:
        JSONResponse: Basic API information and status.
    """
    return JSONResponse(content={
        "message": "AI Code Reviewer Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs",
        "endpoints": {
            "scans": "/api/scans",
            "dashboard": "/api/dashboard",
            "feedback": "/api/feedback", 
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    })


@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint for monitoring and load balancer probes.
    
    Returns:
        JSONResponse: Health status information.
    """
    return JSONResponse(content={
        "status": "healthy",
        "service": "AI Code Reviewer Backend",
        "version": "1.0.0",
        "components": {
            "api": "operational",
            "scan_service": "operational",
            "task_queue": "operational"
        }
    })


@app.get("/api/info")
async def api_info() -> JSONResponse:
    """
    API information endpoint.
    
    Returns:
        JSONResponse: Detailed API information and available endpoints.
    """
    return JSONResponse(content={
        "name": "AI Code Reviewer API",
        "version": "1.0.0",
        "description": "Backend API for AI-powered code review and analysis",
        "features": [
            "Multi-language code analysis (Python, Java, Kotlin)",
            "Static analysis with 50+ rules",
            "LLM-powered semantic analysis",
            "Interactive diagram generation",
            "Risk prediction and assessment",
            "Real-time scan progress tracking"
        ],
        "supported_languages": ["python", "java", "kotlin"],
        "scan_types": ["pr", "project"],
        "endpoints": {
            "scans": {
                "POST /scans/initiate": "Initiate new scan",
                "GET /scans/{scan_id}/report": "Get scan report",
                "GET /scans/{scan_id}/status": "Get scan status",
                "GET /scans/jobs/{job_id}/status": "Get job status",
                "GET /scans/": "List scans",
                "DELETE /scans/{scan_id}": "Delete scan"
            }
        }
    })


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors with consistent response format."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors with consistent response format."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An internal error occurred while processing the request"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    ) 