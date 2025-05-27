"""
Pydantic models for feedback-related data structures.

This module defines the data models used by the webapp backend for handling
user feedback on scan findings and LLM suggestions. This data can be used
for improving LLM performance and fine-tuning.
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class FeedbackType(str, Enum):
    """Enumeration for feedback types."""
    FINDING = "finding"
    LLM_SUGGESTION = "llm_suggestion"
    LLM_INSIGHT = "llm_insight"
    DIAGRAM = "diagram"
    OVERALL_REPORT = "overall_report"


class FeedbackRating(str, Enum):
    """Enumeration for feedback ratings."""
    VERY_HELPFUL = "very_helpful"
    HELPFUL = "helpful"
    NEUTRAL = "neutral"
    NOT_HELPFUL = "not_helpful"
    VERY_UNHELPFUL = "very_unhelpful"


class FeedbackRequest(BaseModel):
    """Model for feedback request data."""
    scan_id: str = Field(..., description="ID of the scan being reviewed")
    finding_id: Optional[str] = Field(default=None, description="ID of the specific finding (if applicable)")
    feedback_type: FeedbackType = Field(..., description="Type of item being reviewed")
    is_helpful: bool = Field(..., description="Whether the item was helpful")
    rating: Optional[FeedbackRating] = Field(default=None, description="Detailed rating")
    comment: str = Field(default="", description="Optional detailed comment")
    user_id: Optional[str] = Field(default=None, description="User ID if authentication is enabled")
    
    # Context information for better understanding
    item_content: Optional[str] = Field(default=None, description="Content of the item being reviewed")
    rule_id: Optional[str] = Field(default=None, description="Rule ID for static analysis findings")
    suggestion_type: Optional[str] = Field(default=None, description="Type of LLM suggestion")


class FeedbackResponse(BaseModel):
    """Model for feedback response."""
    feedback_id: str = Field(..., description="Unique identifier for the feedback record")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(..., description="When the feedback was recorded")


class FeedbackSummary(BaseModel):
    """Model for feedback summary statistics."""
    scan_id: str = Field(..., description="Scan ID")
    total_feedback_count: int = Field(..., description="Total number of feedback items")
    helpful_count: int = Field(..., description="Number of helpful feedback items")
    not_helpful_count: int = Field(..., description="Number of not helpful feedback items")
    feedback_types: dict[FeedbackType, int] = Field(..., description="Count by feedback type")
    average_rating: Optional[float] = Field(default=None, description="Average rating score")


class FeedbackDetail(BaseModel):
    """Model for detailed feedback information."""
    feedback_id: str = Field(..., description="Unique identifier for the feedback")
    scan_id: str = Field(..., description="Associated scan ID")
    finding_id: Optional[str] = Field(default=None, description="Associated finding ID")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    is_helpful: bool = Field(..., description="Whether marked as helpful")
    rating: Optional[FeedbackRating] = Field(default=None, description="Detailed rating")
    comment: str = Field(..., description="User comment")
    user_id: Optional[str] = Field(default=None, description="User who provided feedback")
    item_content: Optional[str] = Field(default=None, description="Content that was reviewed")
    rule_id: Optional[str] = Field(default=None, description="Associated rule ID")
    suggestion_type: Optional[str] = Field(default=None, description="Type of suggestion")
    timestamp: datetime = Field(..., description="When feedback was created")
    
    # Optional metadata for ML/analytics
    metadata: Optional[dict] = Field(default=None, description="Additional metadata for analysis")


class FeedbackQuery(BaseModel):
    """Model for feedback query parameters."""
    scan_id: Optional[str] = Field(default=None, description="Filter by scan ID")
    feedback_type: Optional[FeedbackType] = Field(default=None, description="Filter by feedback type")
    is_helpful: Optional[bool] = Field(default=None, description="Filter by helpfulness")
    user_id: Optional[str] = Field(default=None, description="Filter by user ID")
    start_date: Optional[datetime] = Field(default=None, description="Filter from date")
    end_date: Optional[datetime] = Field(default=None, description="Filter to date")
    limit: int = Field(default=50, ge=1, le=500, description="Maximum number of results")
    offset: int = Field(default=0, ge=0, description="Number of results to skip")


class FeedbackAnalytics(BaseModel):
    """Model for feedback analytics and insights."""
    total_feedback: int = Field(..., description="Total feedback count")
    helpfulness_ratio: float = Field(..., description="Ratio of helpful to total feedback")
    feedback_by_type: dict[FeedbackType, dict] = Field(..., description="Statistics by feedback type")
    rule_performance: dict[str, dict] = Field(..., description="Performance metrics by rule")
    common_complaints: list[str] = Field(..., description="Most common negative feedback themes")
    improvement_suggestions: list[str] = Field(..., description="Suggested improvements based on feedback")
    time_period: dict = Field(..., description="Time period for analytics") 