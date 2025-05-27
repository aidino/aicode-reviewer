"""
Dashboard models for AI Code Reviewer Analytics.

This module contains Pydantic models for dashboard analytics and metrics,
including time range handling, trend data, and comprehensive system health monitoring.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class TimeRange(str, Enum):
    """Time range options for dashboard analytics."""
    LAST_7_DAYS = "LAST_7_DAYS"
    LAST_30_DAYS = "LAST_30_DAYS"
    LAST_90_DAYS = "LAST_90_DAYS"
    LAST_YEAR = "LAST_YEAR"


class TrendDataPoint(BaseModel):
    """Single data point in a trend series."""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    value: float = Field(..., description="Metric value for this date")
    count: int = Field(..., description="Count of items for this date")


class ScanMetrics(BaseModel):
    """Metrics related to code scans."""
    total_scans: int = Field(..., description="Total number of scans")
    active_scans: int = Field(..., description="Currently running scans")
    completed_scans: int = Field(..., description="Successfully completed scans")
    failed_scans: int = Field(..., description="Failed scans")
    avg_scan_duration: float = Field(..., description="Average scan duration in minutes")
    scans_by_type: Dict[str, int] = Field(..., description="Scan counts by type (pr, project, etc.)")
    scans_by_status: Dict[str, int] = Field(..., description="Scan counts by status")


class FindingsMetrics(BaseModel):
    """Metrics related to code analysis findings."""
    total_findings: int = Field(..., description="Total number of findings")
    avg_findings_per_scan: float = Field(..., description="Average findings per scan")
    findings_by_severity: Dict[str, int] = Field(..., description="Findings count by severity")
    findings_by_category: Dict[str, int] = Field(..., description="Findings count by category")
    top_rules: List[Dict[str, Any]] = Field(..., description="Top triggered rules with counts")


class RepositoryMetrics(BaseModel):
    """Metrics related to repository analysis."""
    total_repositories: int = Field(..., description="Total number of analyzed repositories")
    most_scanned_repos: List[Dict[str, Any]] = Field(..., description="Most frequently scanned repositories")
    languages_analyzed: Dict[str, int] = Field(..., description="Count of files by programming language")
    avg_repository_health: float = Field(..., description="Average repository health score (0-1)")


class XAIMetrics(BaseModel):
    """Metrics related to Explainable AI (XAI) analysis."""
    total_xai_analyses: int = Field(default=0, description="Total number of XAI analyses performed")
    avg_confidence_score: float = Field(default=0.0, description="Average confidence score (0-1)")
    confidence_distribution: Dict[str, int] = Field(default_factory=lambda: {"high": 0, "medium": 0, "low": 0}, description="Distribution of confidence levels")
    reasoning_quality_score: float = Field(default=0.0, description="Average reasoning quality score (0-1)")


class FindingsTrend(BaseModel):
    """Trend data for findings over time."""
    total_findings: List[TrendDataPoint] = Field(default_factory=list, description="Overall findings trend")
    severity_trends: Dict[str, List[TrendDataPoint]] = Field(default_factory=dict, description="Trends by severity")
    category_trends: Dict[str, List[TrendDataPoint]] = Field(default_factory=dict, description="Trends by category")


class SystemHealth(BaseModel):
    """System health and status information."""
    status: str = Field(..., description="Overall system status (healthy, degraded, unhealthy)")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Application version")
    uptime: str = Field(..., description="System uptime")
    metrics: Dict[str, Any] = Field(..., description="Key system metrics")
    components: Dict[str, str] = Field(..., description="Component health status")


class DashboardSummary(BaseModel):
    """Comprehensive dashboard summary with all metrics."""
    time_range: TimeRange = Field(..., description="Time range for this summary")
    generated_at: datetime = Field(..., description="When this summary was generated")
    scan_metrics: ScanMetrics = Field(..., description="Scan-related metrics")
    findings_metrics: FindingsMetrics = Field(..., description="Findings-related metrics")
    repository_metrics: RepositoryMetrics = Field(..., description="Repository-related metrics")
    xai_metrics: XAIMetrics = Field(..., description="XAI-related metrics")
    findings_trend: FindingsTrend = Field(..., description="Trend data for findings")
    recent_scans: List[Dict[str, Any]] = Field(..., description="Recent scan activity")
    recent_findings: List[Dict[str, Any]] = Field(..., description="Recent high-priority findings")
    system_health: SystemHealth = Field(..., description="Current system health status")


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Application version")
    uptime: str = Field(..., description="Service uptime")
    components: Dict[str, str] = Field(..., description="Component health status")


class DashboardQuery(BaseModel):
    """Query parameters for dashboard data retrieval."""
    time_range: TimeRange = Field(default=TimeRange.LAST_30_DAYS, description="Time range for data")
    repository_filter: Optional[str] = Field(None, description="Filter by specific repository")
    scan_type_filter: Optional[str] = Field(None, description="Filter by scan type")
    include_trends: bool = Field(default=True, description="Include trend data")
    include_xai: bool = Field(default=True, description="Include XAI metrics") 