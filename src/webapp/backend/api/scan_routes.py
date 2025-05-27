"""
FastAPI routes for scan-related endpoints.

This module defines the API routes for managing code scans and retrieving
scan reports. It handles requests for creating scans, checking scan status,
and retrieving detailed scan reports.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from ..models.scan_models import (
    ReportDetail, ScanRequest, ScanResponse, ScanListItem, ScanStatus, ScanInitiateResponse
)
from ..services.scan_service import ScanService

# Configure logging
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/scans", tags=["scans"])


def get_scan_service() -> ScanService:
    """
    Dependency function to get ScanService instance.
    
    Returns:
        ScanService: Service instance for handling scan operations
    """
    return ScanService()


@router.get("/{scan_id}/report", response_model=ReportDetail)
async def get_scan_report(
    scan_id: str,
    scan_service: ScanService = Depends(get_scan_service)
) -> ReportDetail:
    """
    Retrieve a complete scan report by scan ID.
    
    This endpoint retrieves the full scan report including static analysis findings,
    LLM insights, diagram data, and metadata for a specific scan.
    
    Args:
        scan_id (str): Unique identifier for the scan
        scan_service (ScanService): Injected scan service dependency
        
    Returns:
        ReportDetail: Complete report data including findings, insights, and diagrams
        
    Raises:
        HTTPException: 404 if scan not found, 500 for internal errors
    """
    logger.info(f"GET /scans/{scan_id}/report - Retrieving scan report")
    
    try:
        # Validate scan_id format
        if not scan_id or not scan_id.strip():
            logger.warning("Empty scan_id provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scan ID cannot be empty"
            )
        
        # Retrieve report from service
        report = scan_service.get_scan_report(scan_id)
        
        if report is None:
            logger.warning(f"Scan report not found for scan_id: {scan_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan report not found for scan ID: {scan_id}"
            )
        
        logger.info(f"Successfully retrieved report for scan_id: {scan_id}")
        logger.debug(f"Report summary: {report.summary.total_findings} findings, "
                    f"status: {report.summary.scan_status}")
        
        return report
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error retrieving scan report for {scan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving scan report"
        )


@router.post("/initiate", response_model=ScanInitiateResponse)
async def initiate_scan(
    scan_request: ScanRequest,
    scan_service: ScanService = Depends(get_scan_service)
) -> ScanInitiateResponse:
    """
    Initiate a new code scan asynchronously.
    
    This endpoint accepts a scan request and starts the scan process in the background.
    It returns immediately with a scan ID and job ID that can be used to track progress.
    
    Args:
        scan_request (ScanRequest): Scan configuration including repository URL, type, and parameters
        scan_service (ScanService): Injected scan service dependency
        
    Returns:
        ScanInitiateResponse: Response with scan ID, job ID, and initial status
        
    Raises:
        HTTPException: 400 for validation errors, 500 for internal errors
    """
    logger.info(f"POST /scans/initiate - Initiating scan for {scan_request.repo_url}")
    
    try:
        # Validate scan request
        if not scan_request.repo_url or not scan_request.repo_url.strip():
            logger.warning("Empty repository URL provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Repository URL cannot be empty"
            )
        
        # Validate PR ID for PR scans
        if scan_request.scan_type.value == "pr" and not scan_request.pr_id:
            logger.warning("PR scan requested but no PR ID provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PR ID is required for PR scans"
            )
        
        # Initiate the scan asynchronously
        response = await scan_service.initiate_scan(scan_request)
        
        logger.info(f"Successfully initiated scan: {response.scan_id}")
        logger.debug(f"Scan details: repository={response.repository}, type={response.scan_type}, job_id={response.job_id}")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error initiating scan for {scan_request.repo_url}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while initiating scan"
        )


@router.get("/{scan_id}/status")
async def get_scan_status(
    scan_id: str,
    scan_service: ScanService = Depends(get_scan_service)
) -> JSONResponse:
    """
    Get the current status of a scan.
    
    This endpoint checks both active task queue and completed scan reports
    to provide comprehensive status information.
    
    Args:
        scan_id (str): Unique identifier for the scan
        scan_service (ScanService): Injected scan service dependency
        
    Returns:
        JSONResponse: Scan status information including progress if available
    """
    logger.info(f"GET /scans/{scan_id}/status - Checking scan status")
    
    try:
        # First check if scan is in progress via task queue
        task_status = scan_service.get_scan_status_by_scan_id(scan_id)
        
        if task_status:
            # Scan is in progress or recently completed
            logger.debug(f"Found task status for scan {scan_id}: {task_status['status']}")
            return JSONResponse(content={
                "scan_id": scan_id,
                "status": task_status["status"],
                "progress": task_status.get("progress", 0),
                "duration_seconds": task_status.get("duration_seconds"),
                "error_message": task_status.get("error_message"),
                "repository": task_status["repository"],
                "scan_type": task_status["scan_type"],
                "created_at": task_status["created_at"],
                "started_at": task_status.get("started_at"),
                "completed_at": task_status.get("completed_at"),
                "is_active_task": True
            })
        
        # If not in task queue, check for completed report
        report = scan_service.get_scan_report(scan_id)
        
        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan not found for scan ID: {scan_id}"
            )
        
        # Return completed scan status from report
        return JSONResponse(content={
            "scan_id": scan_id,
            "status": report.summary.scan_status.value,
            "total_findings": report.summary.total_findings,
            "has_llm_analysis": report.summary.has_llm_analysis,
            "timestamp": report.scan_info.timestamp.isoformat(),
            "repository": report.scan_info.repository,
            "scan_type": report.scan_info.scan_type.value,
            "progress": 100,  # Completed scans are 100% done
            "is_active_task": False
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan status for {scan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving scan status"
        )


@router.get("/jobs/{job_id}/status")
async def get_job_status(
    job_id: str,
    scan_service: ScanService = Depends(get_scan_service)
) -> JSONResponse:
    """
    Get the current status of a background job.
    
    This endpoint provides detailed task status information including progress,
    timing, and error details for background scan jobs.
    
    Args:
        job_id (str): Unique identifier for the background job
        scan_service (ScanService): Injected scan service dependency
        
    Returns:
        JSONResponse: Job status information with progress details
    """
    logger.info(f"GET /scans/jobs/{job_id}/status - Checking job status")
    
    try:
        task_status = scan_service.get_task_status(job_id)
        
        if task_status is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job not found for job ID: {job_id}"
            )
        
        logger.debug(f"Found job status: {task_status['status']}")
        return JSONResponse(content=task_status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status for {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving job status"
        )


@router.post("/", response_model=ScanResponse)
async def create_scan(
    scan_request: ScanRequest,
    scan_service: ScanService = Depends(get_scan_service)
) -> ScanResponse:
    """
    Create a new code scan.
    
    Args:
        scan_request (ScanRequest): Scan configuration and parameters
        scan_service (ScanService): Injected scan service dependency
        
    Returns:
        ScanResponse: Response with scan ID and initial status
    """
    logger.info(f"POST /scans - Creating new scan for {scan_request.repo_url}")
    
    try:
        # TODO: Implement actual scan creation logic
        # For now, return a mock response
        
        scan_id = f"{scan_request.scan_type.value}_{hash(scan_request.repo_url) % 10000}"
        
        logger.info(f"Created scan with ID: {scan_id}")
        
        return ScanResponse(
            scan_id=scan_id,
            status=ScanStatus.PENDING,
            message=f"Scan created successfully. ID: {scan_id}",
            estimated_duration=300  # 5 minutes estimate
        )
        
    except Exception as e:
        logger.error(f"Error creating scan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating scan"
        )


@router.get("/", response_model=list[ScanListItem])
async def list_scans(
    limit: int = 20,
    offset: int = 0,
    scan_service: ScanService = Depends(get_scan_service)
) -> list[ScanListItem]:
    """
    List all scans with pagination.
    
    Args:
        limit (int): Maximum number of scans to return (default: 20)
        offset (int): Number of scans to skip (default: 0)
        scan_service (ScanService): Injected scan service dependency
        
    Returns:
        list[ScanListItem]: List of scan summary items
    """
    logger.info(f"GET /scans - Listing scans (limit={limit}, offset={offset})")
    
    try:
        # TODO: Implement actual scan listing logic
        # For now, return mock data
        
        mock_scans = [
            ScanListItem(
                scan_id="demo_scan_1",
                repository="https://github.com/example/ai-code-reviewer-demo",
                scan_type="pr",
                status=ScanStatus.COMPLETED,
                total_findings=5,
                timestamp="2025-01-28T10:30:00",
                pr_id=42
            ),
            ScanListItem(
                scan_id="pr_scan_123",
                repository="https://github.com/user/example-repo",
                scan_type="pr",
                status=ScanStatus.COMPLETED,
                total_findings=3,
                timestamp="2025-01-28T09:15:00",
                pr_id=123
            ),
            ScanListItem(
                scan_id="project_scan_456",
                repository="https://github.com/company/large-project",
                scan_type="project",
                status=ScanStatus.COMPLETED,
                total_findings=15,
                timestamp="2025-01-28T08:00:00",
                branch="main"
            )
        ]
        
        # Apply pagination
        start_idx = offset
        end_idx = min(offset + limit, len(mock_scans))
        paginated_scans = mock_scans[start_idx:end_idx]
        
        logger.info(f"Returning {len(paginated_scans)} scans")
        return paginated_scans
        
    except Exception as e:
        logger.error(f"Error listing scans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while listing scans"
        )


@router.delete("/{scan_id}")
async def delete_scan(
    scan_id: str,
    scan_service: ScanService = Depends(get_scan_service)
) -> JSONResponse:
    """
    Delete a scan and its associated data.
    
    Args:
        scan_id (str): Unique identifier for the scan to delete
        scan_service (ScanService): Injected scan service dependency
        
    Returns:
        JSONResponse: Confirmation of deletion
    """
    logger.info(f"DELETE /scans/{scan_id} - Deleting scan")
    
    try:
        # TODO: Implement actual scan deletion logic
        # For now, just return success
        
        # Check if scan exists first
        report = scan_service.get_scan_report(scan_id)
        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan not found for scan ID: {scan_id}"
            )
        
        logger.info(f"Successfully deleted scan: {scan_id}")
        
        return JSONResponse(content={
            "message": f"Scan {scan_id} deleted successfully",
            "scan_id": scan_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scan {scan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deleting scan"
        ) 