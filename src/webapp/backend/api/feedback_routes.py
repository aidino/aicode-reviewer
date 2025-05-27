"""
FastAPI routes for feedback operations.

This module provides REST API endpoints for submitting and retrieving
user feedback on scan results and LLM suggestions.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from ..models.feedback_models import (
    FeedbackRequest,
    FeedbackResponse,
    FeedbackSummary,
    FeedbackDetail,
    FeedbackQuery,
    FeedbackAnalytics,
    FeedbackType,
)
from ..services.feedback_service import FeedbackService

logger = logging.getLogger(__name__)

# Create router for feedback endpoints
router = APIRouter(prefix="/feedback", tags=["feedback"])


def get_feedback_service() -> FeedbackService:
    """
    Dependency to get FeedbackService instance.
    
    Returns:
        FeedbackService instance for handling feedback operations
    """
    return FeedbackService()


@router.post("/", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(
    feedback_request: FeedbackRequest,
    feedback_service: FeedbackService = Depends(get_feedback_service)
) -> FeedbackResponse:
    """
    Submit user feedback for a scan result or LLM suggestion.
    
    This endpoint allows users to provide feedback on:
    - Static analysis findings
    - LLM suggestions and insights
    - Generated diagrams
    - Overall report quality
    
    Args:
        feedback_request: Feedback data from the user
        feedback_service: Injected feedback service
        
    Returns:
        FeedbackResponse with feedback ID and timestamp
        
    Raises:
        HTTPException: 400 for invalid request data, 500 for server errors
    """
    try:
        logger.info(f"Receiving feedback for scan {feedback_request.scan_id}")
        
        # Validate scan_id
        if not feedback_request.scan_id.strip():
            raise HTTPException(
                status_code=400,
                detail="scan_id cannot be empty"
            )
        
        # Submit feedback
        response = await feedback_service.submit_feedback(feedback_request)
        
        logger.info(f"Feedback submitted successfully: {response.feedback_id}")
        return response
        
    except ValueError as e:
        logger.error(f"Invalid feedback request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/summary/{scan_id}", response_model=FeedbackSummary)
async def get_feedback_summary(
    scan_id: str,
    feedback_service: FeedbackService = Depends(get_feedback_service)
) -> FeedbackSummary:
    """
    Get feedback summary for a specific scan.
    
    Returns aggregated statistics about feedback received for a scan,
    including helpfulness ratios and feedback type breakdowns.
    
    Args:
        scan_id: Scan identifier
        feedback_service: Injected feedback service
        
    Returns:
        FeedbackSummary with aggregated statistics
        
    Raises:
        HTTPException: 400 for invalid scan_id, 500 for server errors
    """
    try:
        if not scan_id.strip():
            raise HTTPException(
                status_code=400,
                detail="scan_id cannot be empty"
            )
        
        logger.info(f"Getting feedback summary for scan {scan_id}")
        
        summary = await feedback_service.get_feedback_summary(scan_id)
        
        logger.info(f"Feedback summary retrieved: {summary.total_feedback_count} items")
        return summary
        
    except Exception as e:
        logger.error(f"Error getting feedback summary for scan {scan_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get feedback summary: {str(e)}"
        )


@router.get("/query", response_model=List[FeedbackDetail])
async def query_feedback(
    scan_id: Optional[str] = Query(None, description="Filter by scan ID"),
    feedback_type: Optional[FeedbackType] = Query(None, description="Filter by feedback type"),
    is_helpful: Optional[bool] = Query(None, description="Filter by helpfulness"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    feedback_service: FeedbackService = Depends(get_feedback_service)
) -> List[FeedbackDetail]:
    """
    Query feedback with filtering and pagination.
    
    Allows filtering feedback by various criteria and supports pagination
    for handling large amounts of feedback data.
    
    Args:
        scan_id: Optional scan ID filter
        feedback_type: Optional feedback type filter
        is_helpful: Optional helpfulness filter
        user_id: Optional user ID filter
        limit: Maximum number of results (1-500)
        offset: Number of results to skip for pagination
        feedback_service: Injected feedback service
        
    Returns:
        List of FeedbackDetail matching the query criteria
        
    Raises:
        HTTPException: 400 for invalid parameters, 500 for server errors
    """
    try:
        logger.info(f"Querying feedback with filters: scan_id={scan_id}, "
                   f"type={feedback_type}, helpful={is_helpful}")
        
        query = FeedbackQuery(
            scan_id=scan_id,
            feedback_type=feedback_type,
            is_helpful=is_helpful,
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        feedback_list = await feedback_service.query_feedback(query)
        
        logger.info(f"Feedback query returned {len(feedback_list)} results")
        return feedback_list
        
    except Exception as e:
        logger.error(f"Error querying feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query feedback: {str(e)}"
        )


@router.get("/analytics", response_model=FeedbackAnalytics)
async def get_feedback_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in analytics"),
    feedback_service: FeedbackService = Depends(get_feedback_service)
) -> FeedbackAnalytics:
    """
    Get feedback analytics and insights for LLM improvement.
    
    Generates comprehensive analytics including:
    - Overall helpfulness ratios
    - Performance by feedback type
    - Rule performance statistics
    - Common complaint themes
    - Improvement suggestions
    
    This data can be used for:
    - LLM fine-tuning
    - Static analysis rule improvement
    - User experience optimization
    
    Args:
        days: Number of days to include in analytics (1-365)
        feedback_service: Injected feedback service
        
    Returns:
        FeedbackAnalytics with insights for improvement
        
    Raises:
        HTTPException: 400 for invalid parameters, 500 for server errors
    """
    try:
        logger.info(f"Generating feedback analytics for {days} days")
        
        analytics = await feedback_service.get_feedback_analytics(days)
        
        logger.info(f"Analytics generated: {analytics.total_feedback} total feedback items")
        return analytics
        
    except Exception as e:
        logger.error(f"Error generating feedback analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analytics: {str(e)}"
        )


@router.delete("/{feedback_id}", status_code=204)
async def delete_feedback(
    feedback_id: str,
    feedback_service: FeedbackService = Depends(get_feedback_service)
) -> None:
    """
    Delete a feedback record (admin operation).
    
    This endpoint allows deletion of feedback records, typically used
    for data cleanup or privacy compliance (GDPR, etc.).
    
    Args:
        feedback_id: Unique identifier of the feedback to delete
        feedback_service: Injected feedback service
        
    Raises:
        HTTPException: 400 for invalid ID, 404 if not found, 500 for server errors
    """
    try:
        if not feedback_id.strip():
            raise HTTPException(
                status_code=400,
                detail="feedback_id cannot be empty"
            )
        
        logger.info(f"Deleting feedback {feedback_id}")
        
        # Note: This would need to be implemented in FeedbackService
        # For now, return 404 as the method doesn't exist
        raise HTTPException(
            status_code=404,
            detail="Feedback not found or deletion not implemented"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting feedback {feedback_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete feedback: {str(e)}"
        )


@router.get("/health", status_code=200)
async def feedback_health_check() -> JSONResponse:
    """
    Health check endpoint for feedback service.
    
    Returns:
        JSON response indicating service status
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "feedback",
            "endpoints": [
                "POST /feedback/",
                "GET /feedback/summary/{scan_id}",
                "GET /feedback/query",
                "GET /feedback/analytics",
                "DELETE /feedback/{feedback_id}",
                "GET /feedback/health"
            ]
        }
    ) 