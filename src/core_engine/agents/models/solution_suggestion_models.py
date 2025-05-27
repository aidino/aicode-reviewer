"""
Pydantic models for SolutionSuggestionAgent enhanced features.

This module defines the data models for explainable AI (XAI) capabilities,
multiple solution options, confidence scoring, and evidence-based reasoning.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Confidence levels for solutions and recommendations."""
    VERY_LOW = "very_low"  # 0.0 - 0.2
    LOW = "low"           # 0.2 - 0.4
    MEDIUM = "medium"     # 0.4 - 0.6
    HIGH = "high"         # 0.6 - 0.8
    VERY_HIGH = "very_high"  # 0.8 - 1.0


class SuggestionType(str, Enum):
    """Types of suggestions that can be provided."""
    CODE_REFACTOR = "code_refactor"
    SECURITY_FIX = "security_fix"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    BEST_PRACTICE = "best_practice"
    BUG_FIX = "bug_fix"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    ARCHITECTURE = "architecture"


class EvidenceType(str, Enum):
    """Types of evidence supporting a recommendation."""
    CODE_PATTERN = "code_pattern"
    BEST_PRACTICE = "best_practice"
    SECURITY_PRINCIPLE = "security_principle"
    PERFORMANCE_BENCHMARK = "performance_benchmark"
    INDUSTRY_STANDARD = "industry_standard"
    DOCUMENTATION_REFERENCE = "documentation_reference"
    TESTING_GUIDELINE = "testing_guideline"


class XAIReasoning(BaseModel):
    """Explainable AI reasoning for a solution or recommendation."""
    primary_reason: str = Field(..., description="Main reason for this recommendation")
    supporting_reasons: List[str] = Field(default_factory=list, description="Additional supporting reasons")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    confidence_level: ConfidenceLevel = Field(..., description="Human-readable confidence level")
    evidence: List["Evidence"] = Field(default_factory=list, description="Supporting evidence")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made in this reasoning")
    limitations: List[str] = Field(default_factory=list, description="Known limitations of this approach")
    
    def get_confidence_level(self) -> ConfidenceLevel:
        """Get confidence level based on score."""
        if self.confidence_score >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif self.confidence_score >= 0.6:
            return ConfidenceLevel.HIGH
        elif self.confidence_score >= 0.4:
            return ConfidenceLevel.MEDIUM
        elif self.confidence_score >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW


class Evidence(BaseModel):
    """Evidence supporting a recommendation."""
    type: EvidenceType = Field(..., description="Type of evidence")
    description: str = Field(..., description="Detailed description of the evidence")
    source: Optional[str] = Field(default=None, description="Source of this evidence (e.g., documentation URL)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this evidence")
    code_example: Optional[str] = Field(default=None, description="Code example demonstrating this evidence")


class ProsCons(BaseModel):
    """Pros and cons analysis for a solution approach."""
    pros: List[str] = Field(default_factory=list, description="Advantages of this approach")
    cons: List[str] = Field(default_factory=list, description="Disadvantages of this approach")
    trade_offs: List[str] = Field(default_factory=list, description="Key trade-offs to consider")
    risk_assessment: str = Field(default="", description="Overall risk assessment")


class CodeSuggestion(BaseModel):
    """A single code suggestion with metadata."""
    title: str = Field(..., description="Brief title for this suggestion")
    description: str = Field(..., description="Detailed description of the change")
    suggested_code: str = Field(..., description="The suggested code")
    diff_snippet: Optional[str] = Field(default=None, description="Diff showing the change")
    file_path: Optional[str] = Field(default=None, description="File path where this applies")
    line_start: Optional[int] = Field(default=None, description="Starting line number")
    line_end: Optional[int] = Field(default=None, description="Ending line number")
    reasoning: XAIReasoning = Field(..., description="XAI reasoning for this suggestion")
    impact_assessment: str = Field(default="", description="Assessment of impact if applied")


class AlternativeSolution(BaseModel):
    """An alternative solution approach."""
    approach_name: str = Field(..., description="Name/title of this approach")
    description: str = Field(..., description="Detailed description of the approach")
    code_suggestions: List[CodeSuggestion] = Field(default_factory=list, description="Code suggestions for this approach")
    pros_cons: ProsCons = Field(..., description="Pros and cons analysis")
    reasoning: XAIReasoning = Field(..., description="XAI reasoning for this approach")
    implementation_complexity: str = Field(..., description="Complexity assessment (low/medium/high)")
    estimated_effort: str = Field(default="", description="Estimated implementation effort")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites for this approach")


class SolutionSuggestion(BaseModel):
    """Enhanced solution suggestion with XAI capabilities."""
    # Basic information
    finding_id: str = Field(..., description="ID of the finding this addresses")
    suggestion_type: SuggestionType = Field(..., description="Type of suggestion")
    title: str = Field(..., description="Brief title for the solution")
    summary: str = Field(..., description="Executive summary of the solution")
    
    # Primary solution
    primary_solution: AlternativeSolution = Field(..., description="Recommended primary solution")
    
    # Alternative approaches
    alternative_solutions: List[AlternativeSolution] = Field(
        default_factory=list, 
        description="Alternative solution approaches"
    )
    
    # XAI and explainability
    overall_reasoning: XAIReasoning = Field(..., description="Overall reasoning for the recommendation")
    confidence_breakdown: Dict[str, float] = Field(
        default_factory=dict, 
        description="Confidence scores for different aspects"
    )
    
    # Impact and context
    impact_analysis: str = Field(..., description="Analysis of potential impact")
    context_considerations: List[str] = Field(
        default_factory=list, 
        description="Important context to consider"
    )
    
    # Implementation guidance
    implementation_steps: List[str] = Field(
        default_factory=list, 
        description="Step-by-step implementation guidance"
    )
    best_practices: List[str] = Field(
        default_factory=list, 
        description="Related best practices"
    )
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now, description="When this suggestion was generated")
    llm_model_used: Optional[str] = Field(default=None, description="LLM model used for generation")
    processing_time_ms: Optional[int] = Field(default=None, description="Processing time in milliseconds")
    
    # Raw data for debugging/analysis
    raw_llm_response: Optional[str] = Field(default=None, description="Raw LLM response")
    prompt_used: Optional[str] = Field(default=None, description="Prompt used for generation")


class SuggestionBatch(BaseModel):
    """A batch of solution suggestions for multiple findings."""
    batch_id: str = Field(..., description="Unique ID for this batch")
    scan_id: str = Field(..., description="ID of the associated scan")
    suggestions: List[SolutionSuggestion] = Field(default_factory=list, description="List of suggestions")
    
    # Batch-level metadata
    total_findings: int = Field(..., description="Total number of findings processed")
    successful_suggestions: int = Field(default=0, description="Number of successful suggestions generated")
    failed_suggestions: int = Field(default=0, description="Number of failed suggestion attempts")
    
    # Timing and performance
    batch_start_time: datetime = Field(default_factory=datetime.now, description="When batch processing started")
    batch_end_time: Optional[datetime] = Field(default=None, description="When batch processing completed")
    total_processing_time_ms: Optional[int] = Field(default=None, description="Total batch processing time")
    
    # Quality metrics
    average_confidence: Optional[float] = Field(default=None, description="Average confidence across suggestions")
    suggestion_types_breakdown: Dict[SuggestionType, int] = Field(
        default_factory=dict, 
        description="Count of suggestions by type"
    )


class SuggestionFeedback(BaseModel):
    """Feedback on a solution suggestion for learning and improvement."""
    suggestion_id: str = Field(..., description="ID of the suggestion being reviewed")
    finding_id: str = Field(..., description="ID of the related finding")
    
    # Feedback ratings
    overall_helpfulness: float = Field(..., ge=1.0, le=5.0, description="Overall helpfulness (1-5)")
    accuracy_rating: float = Field(..., ge=1.0, le=5.0, description="Accuracy rating (1-5)")
    clarity_rating: float = Field(..., ge=1.0, le=5.0, description="Clarity rating (1-5)")
    actionability_rating: float = Field(..., ge=1.0, le=5.0, description="How actionable (1-5)")
    
    # Specific feedback
    was_solution_applied: bool = Field(..., description="Whether the solution was actually applied")
    which_alternative_used: Optional[str] = Field(default=None, description="Which alternative was used if not primary")
    modifications_made: Optional[str] = Field(default=None, description="Modifications made to the suggestion")
    
    # Comments
    positive_feedback: Optional[str] = Field(default=None, description="What worked well")
    negative_feedback: Optional[str] = Field(default=None, description="What could be improved")
    suggestions_for_improvement: Optional[str] = Field(default=None, description="Suggestions for improvement")
    
    # Metadata
    reviewer_id: Optional[str] = Field(default=None, description="ID of the reviewer")
    review_date: datetime = Field(default_factory=datetime.now, description="When the review was submitted")


class SuggestionMetrics(BaseModel):
    """Metrics for evaluating suggestion quality and performance."""
    total_suggestions: int = Field(..., description="Total number of suggestions generated")
    average_confidence: float = Field(..., description="Average confidence score")
    confidence_distribution: Dict[ConfidenceLevel, int] = Field(
        default_factory=dict, 
        description="Distribution of confidence levels"
    )
    
    # Performance metrics
    average_generation_time_ms: float = Field(..., description="Average generation time")
    success_rate: float = Field(..., description="Success rate for suggestion generation")
    
    # Quality metrics (if feedback available)
    average_helpfulness: Optional[float] = Field(default=None, description="Average helpfulness rating")
    average_accuracy: Optional[float] = Field(default=None, description="Average accuracy rating")
    application_rate: Optional[float] = Field(default=None, description="Rate at which suggestions are applied")
    
    # Type breakdown
    suggestion_types_count: Dict[SuggestionType, int] = Field(
        default_factory=dict, 
        description="Count by suggestion type"
    )
    
    # Period information
    period_start: datetime = Field(..., description="Start of measurement period")
    period_end: datetime = Field(..., description="End of measurement period")


# Update forward references
XAIReasoning.model_rebuild() 