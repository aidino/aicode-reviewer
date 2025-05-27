"""
Models package for core engine agents.

This package contains Pydantic models for various agents including
enhanced models for SolutionSuggestionAgent with XAI capabilities.
"""

from .solution_suggestion_models import (
    ConfidenceLevel,
    SuggestionType,
    EvidenceType,
    XAIReasoning,
    Evidence,
    ProsCons,
    CodeSuggestion,
    AlternativeSolution,
    SolutionSuggestion,
    SuggestionBatch,
    SuggestionFeedback,
    SuggestionMetrics,
)

__all__ = [
    "ConfidenceLevel",
    "SuggestionType", 
    "EvidenceType",
    "XAIReasoning",
    "Evidence",
    "ProsCons",
    "CodeSuggestion",
    "AlternativeSolution",
    "SolutionSuggestion",
    "SuggestionBatch",
    "SuggestionFeedback",
    "SuggestionMetrics",
] 