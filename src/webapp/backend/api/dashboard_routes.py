"""
Dashboard API routes for AI Code Review System.

Provides REST endpoints for dashboard analytics, metrics, and system health.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status

from ..models.dashboard_models import (
    DashboardSummary, DashboardQuery, TimeRange, SystemHealth
)
from ..services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Dependency injection
def get_dashboard_service() -> DashboardService:
    """Get dashboard service instance."""
    return DashboardService()


@router.get("/summary", response_model=DashboardSummary, status_code=status.HTTP_200_OK)
async def get_dashboard_summary(
    time_range: TimeRange = Query(default=TimeRange.LAST_30_DAYS, description="Time range for analytics"),
    repository: Optional[str] = Query(default=None, description="Filter by repository"),
    scan_type: Optional[str] = Query(default=None, description="Filter by scan type"),
    include_trends: bool = Query(default=True, description="Include trend data"),
    include_xai: bool = Query(default=True, description="Include XAI metrics"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get comprehensive dashboard summary with analytics and metrics.
    
    Returns aggregated data including:
    - Scan metrics and statistics
    - Findings breakdown and trends
    - Repository analytics
    - XAI (Explainable AI) insights
    - System health indicators
    
    Args:
        time_range: Time period for analytics (default: last 30 days)
        repository: Optional repository filter
        scan_type: Optional scan type filter ('pr' or 'project')
        include_trends: Whether to include trend data
        include_xai: Whether to include XAI metrics
        dashboard_service: Injected dashboard service
        
    Returns:
        DashboardSummary: Comprehensive dashboard data
        
    Raises:
        HTTPException: If data retrieval fails
    """
    try:
        logger.info(f"Dashboard summary requested for {time_range}")
        
        # Validate scan_type if provided
        if scan_type and scan_type not in ["pr", "project"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="scan_type must be 'pr' or 'project'"
            )
        
        # Create query object
        query = DashboardQuery(
            time_range=time_range,
            repository_filter=repository,
            scan_type_filter=scan_type,
            include_trends=include_trends,
            include_xai=include_xai
        )
        
        # Get dashboard data
        summary = await dashboard_service.get_dashboard_summary(query)
        
        logger.info(f"Dashboard summary generated successfully for {time_range}")
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating dashboard summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dashboard summary: {str(e)}"
        )


@router.get("/health", response_model=SystemHealth, status_code=status.HTTP_200_OK)
async def get_dashboard_health(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get dashboard service health check.
    
    Returns system health information including:
    - Service status
    - System uptime
    - Basic metrics
    - Version information
    
    Args:
        dashboard_service: Injected dashboard service
        
    Returns:
        SystemHealth: Health status and metrics
        
    Raises:
        HTTPException: If health check fails
    """
    try:
        logger.info("Dashboard health check requested")
        
        health_response = await dashboard_service.get_health_check()
        
        logger.info("Dashboard health check completed successfully")
        return health_response
        
    except Exception as e:
        logger.error(f"Dashboard health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Dashboard service unhealthy: {str(e)}"
        )


@router.get("/metrics/scans", status_code=status.HTTP_200_OK)
async def get_scan_metrics(
    time_range: TimeRange = Query(default=TimeRange.LAST_30_DAYS),
    repository: Optional[str] = Query(default=None),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get scan-specific metrics.
    
    Returns detailed scan analytics including:
    - Total scans and status breakdown
    - Average scan duration
    - Scan types distribution
    - Success/failure rates
    
    Args:
        time_range: Time period for metrics
        repository: Optional repository filter
        dashboard_service: Injected dashboard service
        
    Returns:
        Dict: Scan metrics data
    """
    try:
        logger.info(f"Scan metrics requested for {time_range}")
        
        query = DashboardQuery(
            time_range=time_range,
            repository_filter=repository,
            include_trends=False,
            include_xai=False
        )
        
        summary = await dashboard_service.get_dashboard_summary(query)
        
        return {
            "scan_metrics": summary.scan_metrics,
            "time_range": time_range,
            "generated_at": summary.generated_at
        }
        
    except Exception as e:
        logger.error(f"Error getting scan metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scan metrics: {str(e)}"
        )


@router.get("/metrics/findings", status_code=status.HTTP_200_OK)
async def get_findings_metrics(
    time_range: TimeRange = Query(default=TimeRange.LAST_30_DAYS),
    repository: Optional[str] = Query(default=None),
    include_trends: bool = Query(default=True),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get findings-specific metrics and trends.
    
    Returns detailed findings analytics including:
    - Total findings and severity breakdown
    - Findings by category
    - Top triggered rules
    - Trend data over time
    
    Args:
        time_range: Time period for metrics
        repository: Optional repository filter
        include_trends: Whether to include trend data
        dashboard_service: Injected dashboard service
        
    Returns:
        Dict: Findings metrics and trends
    """
    try:
        logger.info(f"Findings metrics requested for {time_range}")
        
        query = DashboardQuery(
            time_range=time_range,
            repository_filter=repository,
            include_trends=include_trends,
            include_xai=False
        )
        
        summary = await dashboard_service.get_dashboard_summary(query)
        
        response_data = {
            "findings_metrics": summary.findings_metrics,
            "time_range": time_range,
            "generated_at": summary.generated_at
        }
        
        if include_trends:
            response_data["findings_trend"] = summary.findings_trend
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error getting findings metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get findings metrics: {str(e)}"
        )


@router.get("/metrics/xai", status_code=status.HTTP_200_OK)
async def get_xai_metrics(
    time_range: TimeRange = Query(default=TimeRange.LAST_30_DAYS),
    repository: Optional[str] = Query(default=None),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get Explainable AI (XAI) metrics.
    
    Returns XAI analytics including:
    - AI confidence scores distribution
    - Reasoning quality metrics
    - XAI analysis coverage
    
    Args:
        time_range: Time period for metrics
        repository: Optional repository filter
        dashboard_service: Injected dashboard service
        
    Returns:
        Dict: XAI metrics data
    """
    try:
        logger.info(f"XAI metrics requested for {time_range}")
        
        query = DashboardQuery(
            time_range=time_range,
            repository_filter=repository,
            include_trends=False,
            include_xai=True
        )
        
        summary = await dashboard_service.get_dashboard_summary(query)
        
        return {
            "xai_metrics": summary.xai_metrics,
            "time_range": time_range,
            "generated_at": summary.generated_at
        }
        
    except Exception as e:
        logger.error(f"Error getting XAI metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get XAI metrics: {str(e)}"
        )


@router.get("/recent", status_code=status.HTTP_200_OK)
async def get_recent_activity(
    limit: int = Query(default=10, ge=1, le=50, description="Number of items to return"),
    activity_type: str = Query(default="all", description="Type of activity (scans, findings, or all)"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get recent system activity.
    
    Returns recent scans and findings for dashboard activity feed.
    
    Args:
        limit: Maximum number of items to return
        activity_type: Type of activity to retrieve
        dashboard_service: Injected dashboard service
        
    Returns:
        Dict: Recent activity data
        
    Raises:
        HTTPException: If activity type is invalid
    """
    try:
        logger.info(f"Recent activity requested: {activity_type}")
        
        if activity_type not in ["all", "scans", "findings"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="activity_type must be 'all', 'scans', or 'findings'"
            )
        
        query = DashboardQuery(
            time_range=TimeRange.LAST_7_DAYS,
            include_trends=False,
            include_xai=False
        )
        
        summary = await dashboard_service.get_dashboard_summary(query)
        
        response_data = {
            "activity_type": activity_type,
            "limit": limit,
            "generated_at": summary.generated_at
        }
        
        if activity_type in ["all", "scans"]:
            response_data["recent_scans"] = summary.recent_scans[:limit]
        
        if activity_type in ["all", "findings"]:
            response_data["recent_findings"] = summary.recent_findings[:limit]
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent activity: {str(e)}"
        ) 