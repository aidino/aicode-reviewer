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

from src.webapp.backend.models.scan_models import (
    ReportDetail, ScanRequest, ScanResponse, ScanListItem, ScanStatus
)
from src.webapp.backend.services.scan_service import ScanService

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


@router.get("/{scan_id}/status")
async def get_scan_status(
    scan_id: str,
    scan_service: ScanService = Depends(get_scan_service)
) -> JSONResponse:
    """
    Get the current status of a scan.
    
    Args:
        scan_id (str): Unique identifier for the scan
        scan_service (ScanService): Injected scan service dependency
        
    Returns:
        JSONResponse: Scan status information
    """
    logger.info(f"GET /scans/{scan_id}/status - Checking scan status")
    
    try:
        # For now, use the report to determine status
        # TODO: Implement dedicated status tracking
        report = scan_service.get_scan_report(scan_id)
        
        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan not found for scan ID: {scan_id}"
            )
        
        return JSONResponse(content={
            "scan_id": scan_id,
            "status": report.summary.scan_status.value,
            "total_findings": report.summary.total_findings,
            "has_llm_analysis": report.summary.has_llm_analysis,
            "timestamp": report.scan_info.timestamp.isoformat(),
            "repository": report.scan_info.repository
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan status for {scan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving scan status"
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