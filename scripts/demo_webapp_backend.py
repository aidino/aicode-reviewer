#!/usr/bin/env python3
"""
Demo script for webapp backend API.

This script demonstrates the webapp backend API endpoints by starting
a FastAPI server and making sample requests to test functionality.
"""

import asyncio
import logging
import sys
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
import uvicorn
import httpx

from src.webapp.backend.api.scan_routes import router as scan_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    logger.info("Starting webapp backend demo...")
    yield
    logger.info("Shutting down webapp backend demo...")


def create_demo_app() -> FastAPI:
    """
    Create FastAPI application for demo.
    
    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI(
        title="AI Code Reviewer - Web Application Backend",
        description="Backend API for AI Code Reviewer web application",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Include scan routes
    app.include_router(scan_router)
    
    @app.get("/")
    async def root():
        """Root endpoint for health check."""
        return {
            "message": "AI Code Reviewer Backend API",
            "version": "1.0.0",
            "status": "healthy"
        }
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "service": "ai-code-reviewer-backend"}
    
    return app


async def test_api_endpoints():
    """
    Test the API endpoints with sample requests.
    """
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        logger.info("Testing API endpoints...")
        
        try:
            # Test root endpoint
            logger.info("Testing root endpoint...")
            response = await client.get(f"{base_url}/")
            logger.info(f"Root endpoint: {response.status_code} - {response.json()}")
            
            # Test health endpoint
            logger.info("Testing health endpoint...")
            response = await client.get(f"{base_url}/health")
            logger.info(f"Health endpoint: {response.status_code} - {response.json()}")
            
            # Test scan endpoints
            logger.info("Testing scan endpoints...")
            
            # Get scan report - demo scan
            logger.info("Testing GET /scans/demo_scan_1/report...")
            response = await client.get(f"{base_url}/scans/demo_scan_1/report")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Demo report - Scan ID: {data['scan_info']['scan_id']}")
                logger.info(f"Demo report - Total findings: {data['summary']['total_findings']}")
                logger.info(f"Demo report - Status: {data['summary']['scan_status']}")
                logger.info(f"Demo report - Has LLM analysis: {data['summary']['has_llm_analysis']}")
            else:
                logger.error(f"Failed to get demo report: {response.status_code} - {response.text}")
            
            # Get scan report - PR scan
            logger.info("Testing GET /scans/pr_scan_123/report...")
            response = await client.get(f"{base_url}/scans/pr_scan_123/report")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"PR report - Scan ID: {data['scan_info']['scan_id']}")
                logger.info(f"PR report - PR ID: {data['scan_info']['pr_id']}")
                logger.info(f"PR report - Total findings: {data['summary']['total_findings']}")
            else:
                logger.error(f"Failed to get PR report: {response.status_code} - {response.text}")
            
            # Get scan report - Project scan
            logger.info("Testing GET /scans/project_scan_456/report...")
            response = await client.get(f"{base_url}/scans/project_scan_456/report")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Project report - Scan ID: {data['scan_info']['scan_id']}")
                logger.info(f"Project report - Repository: {data['scan_info']['repository']}")
                logger.info(f"Project report - Total findings: {data['summary']['total_findings']}")
                logger.info(f"Project report - Files analyzed: {data['metadata']['total_files_analyzed']}")
            else:
                logger.error(f"Failed to get project report: {response.status_code} - {response.text}")
            
            # Test scan status
            logger.info("Testing GET /scans/demo_scan_1/status...")
            response = await client.get(f"{base_url}/scans/demo_scan_1/status")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Status - Scan ID: {data['scan_id']}")
                logger.info(f"Status - Status: {data['status']}")
                logger.info(f"Status - Total findings: {data['total_findings']}")
            else:
                logger.error(f"Failed to get scan status: {response.status_code} - {response.text}")
            
            # Test list scans
            logger.info("Testing GET /scans/...")
            response = await client.get(f"{base_url}/scans/")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"List scans - Count: {len(data)}")
                for scan in data:
                    logger.info(f"  - {scan['scan_id']}: {scan['scan_type']} ({scan['status']})")
            else:
                logger.error(f"Failed to list scans: {response.status_code} - {response.text}")
            
            # Test create scan
            logger.info("Testing POST /scans/...")
            scan_request = {
                "repo_url": "https://github.com/test/demo-repo",
                "scan_type": "pr",
                "pr_id": 42,
                "target_branch": "main",
                "source_branch": "feature/test"
            }
            response = await client.post(f"{base_url}/scans/", json=scan_request)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Create scan - Scan ID: {data['scan_id']}")
                logger.info(f"Create scan - Status: {data['status']}")
                logger.info(f"Create scan - Message: {data['message']}")
            else:
                logger.error(f"Failed to create scan: {response.status_code} - {response.text}")
            
            # Test error cases
            logger.info("Testing error cases...")
            
            # Non-existent scan
            response = await client.get(f"{base_url}/scans/nonexistent_scan/report")
            logger.info(f"Non-existent scan: {response.status_code} (expected 404)")
            
            # Empty scan ID
            response = await client.get(f"{base_url}/scans/ /report")
            logger.info(f"Empty scan ID: {response.status_code} (expected 400)")
            
            logger.info("API endpoint testing completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during API testing: {str(e)}")


def main():
    """
    Main function to run the demo.
    """
    logger.info("AI Code Reviewer - Webapp Backend Demo")
    logger.info("=====================================")
    
    # Create FastAPI app
    app = create_demo_app()
    
    # Start server in background and test endpoints
    import threading
    import time
    
    def run_server():
        """Run the FastAPI server."""
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    logger.info("Starting server...")
    time.sleep(2)
    
    # Test endpoints
    try:
        asyncio.run(test_api_endpoints())
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
    
    logger.info("Demo completed. Press Ctrl+C to exit.")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down demo...")


if __name__ == "__main__":
    main() 