"""
Pydantic models for scan-related data structures.

This module defines the data models used by the webapp backend for handling
scan requests, scan results, and report data structures.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ScanType(str, Enum):
    """Enumeration for scan types."""
    PR = "pr"
    PROJECT = "project"


class ScanStatus(str, Enum):
    """Enumeration for scan statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class SeverityLevel(str, Enum):
    """Enumeration for finding severity levels."""
    ERROR = "Error"
    WARNING = "Warning"
    INFO = "Info"
    UNKNOWN = "Unknown"


class StaticAnalysisFinding(BaseModel):
    """Model for a single static analysis finding."""
    rule_id: str = Field(..., description="Unique identifier for the rule")
    message: str = Field(..., description="Human-readable description of the finding")
    line: int = Field(..., description="Line number where the issue was found")
    column: int = Field(..., description="Column number where the issue was found")
    severity: SeverityLevel = Field(..., description="Severity level of the finding")
    category: str = Field(..., description="Category of the finding (e.g., debugging, logging)")
    file: str = Field(..., description="File path where the issue was found")
    suggestion: str = Field(..., description="Suggested fix for the issue")


class LLMReview(BaseModel):
    """Model for LLM analysis review."""
    insights: str = Field(..., description="Raw LLM insights text")
    has_content: bool = Field(..., description="Whether the review contains meaningful content")
    sections: Optional[Dict[str, str]] = Field(default=None, description="Parsed sections of the review")


class DiagramData(BaseModel):
    """Model for diagram data."""
    type: str = Field(..., description="Type of diagram (e.g., class_diagram, sequence_diagram)")
    format: str = Field(..., description="Format of the diagram (e.g., plantuml, mermaid)")
    content: str = Field(..., description="Diagram content/definition")
    title: Optional[str] = Field(default=None, description="Title of the diagram")
    description: Optional[str] = Field(default=None, description="Description of the diagram")


class ScanInfo(BaseModel):
    """Model for scan information metadata."""
    scan_id: str = Field(..., description="Unique identifier for the scan")
    repository: str = Field(..., description="Repository URL or name")
    pr_id: Optional[int] = Field(default=None, description="Pull request ID if applicable")
    branch: Optional[str] = Field(default=None, description="Branch name")
    scan_type: ScanType = Field(..., description="Type of scan performed")
    timestamp: datetime = Field(..., description="When the scan was performed")
    report_version: str = Field(..., description="Version of the report format")


class ScanSummary(BaseModel):
    """Model for scan summary statistics."""
    total_findings: int = Field(..., description="Total number of findings")
    severity_breakdown: Dict[SeverityLevel, int] = Field(..., description="Count of findings by severity")
    category_breakdown: Dict[str, int] = Field(..., description="Count of findings by category")
    scan_status: ScanStatus = Field(..., description="Current status of the scan")
    has_llm_analysis: bool = Field(..., description="Whether LLM analysis was performed")
    error_message: Optional[str] = Field(default=None, description="Error message if scan failed")


class ScanMetadata(BaseModel):
    """Model for additional scan metadata."""
    agent_versions: Dict[str, str] = Field(..., description="Versions of agents used")
    generation_time: datetime = Field(..., description="When the report was generated")
    total_files_analyzed: int = Field(..., description="Total number of files analyzed")
    successful_parses: int = Field(..., description="Number of files successfully parsed")
    error: Optional[str] = Field(default=None, description="Error information if applicable")


class ReportDetail(BaseModel):
    """
    Complete report detail model matching ReportingAgent output structure.
    
    This model represents the full report data generated by ReportingAgent,
    including scan information, summary statistics, findings, LLM insights,
    diagrams, and metadata.
    """
    scan_info: ScanInfo = Field(..., description="Scan metadata and information")
    summary: ScanSummary = Field(..., description="Summary statistics of the scan")
    static_analysis_findings: List[StaticAnalysisFinding] = Field(
        ..., description="List of static analysis findings"
    )
    llm_review: LLMReview = Field(..., description="LLM analysis and insights")
    diagrams: List[DiagramData] = Field(..., description="Generated diagrams")
    metadata: ScanMetadata = Field(..., description="Additional metadata")


class ScanRequest(BaseModel):
    """Model for scan request data."""
    repo_url: str = Field(..., description="Repository URL to scan")
    scan_type: ScanType = Field(..., description="Type of scan to perform")
    pr_id: Optional[int] = Field(default=None, description="Pull request ID for PR scans")
    branch: Optional[str] = Field(default="main", description="Branch to scan for project scans")
    target_branch: Optional[str] = Field(default="main", description="Target branch for PR scans")
    source_branch: Optional[str] = Field(default=None, description="Source branch for PR scans")


class ScanListItem(BaseModel):
    """Model for scan list item (summary view)."""
    scan_id: str = Field(..., description="Unique identifier for the scan")
    repository: str = Field(..., description="Repository name or URL")
    scan_type: ScanType = Field(..., description="Type of scan")
    status: ScanStatus = Field(..., description="Current scan status")
    total_findings: int = Field(..., description="Total number of findings")
    timestamp: datetime = Field(..., description="When the scan was performed")
    pr_id: Optional[int] = Field(default=None, description="Pull request ID if applicable")
    branch: Optional[str] = Field(default=None, description="Branch name")


class ScanResponse(BaseModel):
    """Model for scan response after initiating a scan."""
    scan_id: str = Field(..., description="Unique identifier for the initiated scan")
    status: ScanStatus = Field(..., description="Initial scan status")
    message: str = Field(..., description="Response message")
    estimated_duration: Optional[int] = Field(default=None, description="Estimated duration in seconds")


class ScanInitiateResponse(BaseModel):
    """Model for response when initiating a new scan."""
    scan_id: str = Field(..., description="Unique identifier for the initiated scan")
    job_id: str = Field(..., description="Unique identifier for the background job")
    status: ScanStatus = Field(..., description="Initial scan status")
    message: str = Field(..., description="Response message")
    estimated_duration: Optional[int] = Field(default=None, description="Estimated duration in seconds")
    repository: str = Field(..., description="Repository URL being scanned")
    scan_type: ScanType = Field(..., description="Type of scan being performed") 