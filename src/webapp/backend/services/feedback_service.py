"""
FeedbackService for handling user feedback operations.

This service manages feedback storage, retrieval, and analytics for improving
LLM performance and code analysis quality through user input.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, Counter

from ..models.feedback_models import (
    FeedbackRequest,
    FeedbackResponse,
    FeedbackDetail,
    FeedbackSummary,
    FeedbackQuery,
    FeedbackAnalytics,
    FeedbackType,
    FeedbackRating,
)

logger = logging.getLogger(__name__)


class FeedbackService:
    """
    Service for managing user feedback on scan results and LLM suggestions.
    
    This service handles:
    - Storing feedback in PostgreSQL database
    - Retrieving feedback with filtering and pagination
    - Generating analytics and insights for LLM improvement
    - Aggregating feedback statistics
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize FeedbackService.
        
        Args:
            db_connection: Database connection (PostgreSQL)
                         If None, uses in-memory storage for development
        """
        self.db_connection = db_connection
        
        # In-memory storage for development/testing
        # In production, this would be replaced with PostgreSQL
        self._feedback_storage: Dict[str, FeedbackDetail] = {}
        self._scan_feedback_index: Dict[str, List[str]] = defaultdict(list)
        
        logger.info("FeedbackService initialized")
    
    async def submit_feedback(self, feedback_request: FeedbackRequest) -> FeedbackResponse:
        """
        Submit new feedback for a scan result or LLM suggestion.
        
        Args:
            feedback_request: Feedback data from user
            
        Returns:
            FeedbackResponse with feedback ID and timestamp
            
        Raises:
            ValueError: If feedback data is invalid
            Exception: If database operation fails
        """
        try:
            # Validate feedback request
            if not feedback_request.scan_id:
                raise ValueError("scan_id is required")
            
            if not feedback_request.feedback_type:
                raise ValueError("feedback_type is required")
            
            # Generate unique feedback ID
            feedback_id = str(uuid.uuid4())
            timestamp = datetime.utcnow()
            
            # Create feedback detail record
            feedback_detail = FeedbackDetail(
                feedback_id=feedback_id,
                scan_id=feedback_request.scan_id,
                finding_id=feedback_request.finding_id,
                feedback_type=feedback_request.feedback_type,
                is_helpful=feedback_request.is_helpful,
                rating=feedback_request.rating,
                comment=feedback_request.comment,
                user_id=feedback_request.user_id,
                item_content=feedback_request.item_content,
                rule_id=feedback_request.rule_id,
                suggestion_type=feedback_request.suggestion_type,
                timestamp=timestamp,
                metadata={
                    "user_agent": "webapp",
                    "submission_method": "api",
                    "version": "1.0"
                }
            )
            
            # Store feedback (in production, this would use PostgreSQL)
            await self._store_feedback(feedback_detail)
            
            logger.info(f"Feedback submitted: {feedback_id} for scan {feedback_request.scan_id}")
            
            return FeedbackResponse(
                feedback_id=feedback_id,
                message="Feedback submitted successfully",
                timestamp=timestamp
            )
            
        except ValueError as e:
            logger.error(f"Invalid feedback request: {e}")
            raise
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            raise Exception(f"Failed to submit feedback: {str(e)}")
    
    async def get_feedback_summary(self, scan_id: str) -> FeedbackSummary:
        """
        Get feedback summary for a specific scan.
        
        Args:
            scan_id: Scan identifier
            
        Returns:
            FeedbackSummary with aggregated statistics
        """
        try:
            feedback_list = await self._get_feedback_by_scan(scan_id)
            
            total_count = len(feedback_list)
            helpful_count = sum(1 for f in feedback_list if f.is_helpful)
            not_helpful_count = total_count - helpful_count
            
            # Count by feedback type
            type_counts = Counter(f.feedback_type for f in feedback_list)
            feedback_types = {ftype: count for ftype, count in type_counts.items()}
            
            # Calculate average rating if ratings exist
            ratings = [f.rating for f in feedback_list if f.rating]
            average_rating = None
            if ratings:
                rating_values = {
                    FeedbackRating.VERY_HELPFUL: 5,
                    FeedbackRating.HELPFUL: 4,
                    FeedbackRating.NEUTRAL: 3,
                    FeedbackRating.NOT_HELPFUL: 2,
                    FeedbackRating.VERY_UNHELPFUL: 1
                }
                avg = sum(rating_values.get(r, 3) for r in ratings) / len(ratings)
                average_rating = round(avg, 2)
            
            return FeedbackSummary(
                scan_id=scan_id,
                total_feedback_count=total_count,
                helpful_count=helpful_count,
                not_helpful_count=not_helpful_count,
                feedback_types=feedback_types,
                average_rating=average_rating
            )
            
        except Exception as e:
            logger.error(f"Error getting feedback summary for scan {scan_id}: {e}")
            raise Exception(f"Failed to get feedback summary: {str(e)}")
    
    async def query_feedback(self, query: FeedbackQuery) -> List[FeedbackDetail]:
        """
        Query feedback with filtering and pagination.
        
        Args:
            query: Query parameters for filtering feedback
            
        Returns:
            List of FeedbackDetail matching the query
        """
        try:
            # Get all feedback (in production, this would be a database query)
            all_feedback = list(self._feedback_storage.values())
            
            # Apply filters
            filtered_feedback = []
            for feedback in all_feedback:
                if query.scan_id and feedback.scan_id != query.scan_id:
                    continue
                if query.feedback_type and feedback.feedback_type != query.feedback_type:
                    continue
                if query.is_helpful is not None and feedback.is_helpful != query.is_helpful:
                    continue
                if query.user_id and feedback.user_id != query.user_id:
                    continue
                if query.start_date and feedback.timestamp < query.start_date:
                    continue
                if query.end_date and feedback.timestamp > query.end_date:
                    continue
                
                filtered_feedback.append(feedback)
            
            # Sort by timestamp (newest first)
            filtered_feedback.sort(key=lambda f: f.timestamp, reverse=True)
            
            # Apply pagination
            start_idx = query.offset
            end_idx = start_idx + query.limit
            paginated_feedback = filtered_feedback[start_idx:end_idx]
            
            logger.info(f"Queried feedback: {len(paginated_feedback)} results")
            return paginated_feedback
            
        except Exception as e:
            logger.error(f"Error querying feedback: {e}")
            raise Exception(f"Failed to query feedback: {str(e)}")
    
    async def get_feedback_analytics(self, days: int = 30) -> FeedbackAnalytics:
        """
        Generate analytics and insights from feedback data.
        
        Args:
            days: Number of days to include in analytics
            
        Returns:
            FeedbackAnalytics with insights for LLM improvement
        """
        try:
            # Get feedback from specified time period
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = FeedbackQuery(
                start_date=start_date,
                end_date=end_date,
                limit=500  # Maximum allowed limit for analytics
            )
            
            feedback_list = await self.query_feedback(query)
            
            if not feedback_list:
                return FeedbackAnalytics(
                    total_feedback=0,
                    helpfulness_ratio=0.0,
                    feedback_by_type={},
                    rule_performance={},
                    common_complaints=[],
                    improvement_suggestions=["Continue monitoring feedback for improvement opportunities"],
                    time_period={"start": start_date.isoformat(), "end": end_date.isoformat()}
                )
            
            # Calculate basic metrics
            total_feedback = len(feedback_list)
            helpful_count = sum(1 for f in feedback_list if f.is_helpful)
            helpfulness_ratio = helpful_count / total_feedback if total_feedback > 0 else 0.0
            
            # Analyze by feedback type
            feedback_by_type = self._analyze_feedback_by_type(feedback_list)
            
            # Analyze rule performance
            rule_performance = self._analyze_rule_performance(feedback_list)
            
            # Extract common complaints and suggestions
            common_complaints = self._extract_common_complaints(feedback_list)
            improvement_suggestions = self._generate_improvement_suggestions(feedback_list)
            
            return FeedbackAnalytics(
                total_feedback=total_feedback,
                helpfulness_ratio=round(helpfulness_ratio, 3),
                feedback_by_type=feedback_by_type,
                rule_performance=rule_performance,
                common_complaints=common_complaints,
                improvement_suggestions=improvement_suggestions,
                time_period={
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": days
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating feedback analytics: {e}")
            raise Exception(f"Failed to generate analytics: {str(e)}")
    
    async def _store_feedback(self, feedback: FeedbackDetail) -> None:
        """
        Store feedback in database (PostgreSQL in production).
        
        Args:
            feedback: Feedback detail to store
        """
        # In production, this would execute a PostgreSQL INSERT
        # For now, using in-memory storage
        self._feedback_storage[feedback.feedback_id] = feedback
        self._scan_feedback_index[feedback.scan_id].append(feedback.feedback_id)
    
    async def _get_feedback_by_scan(self, scan_id: str) -> List[FeedbackDetail]:
        """
        Get all feedback for a specific scan.
        
        Args:
            scan_id: Scan identifier
            
        Returns:
            List of feedback for the scan
        """
        feedback_ids = self._scan_feedback_index.get(scan_id, [])
        return [self._feedback_storage[fid] for fid in feedback_ids if fid in self._feedback_storage]
    
    def _analyze_feedback_by_type(self, feedback_list: List[FeedbackDetail]) -> Dict[FeedbackType, Dict]:
        """Analyze feedback statistics by type."""
        analysis = {}
        
        for ftype in FeedbackType:
            type_feedback = [f for f in feedback_list if f.feedback_type == ftype]
            if type_feedback:
                helpful_count = sum(1 for f in type_feedback if f.is_helpful)
                total_count = len(type_feedback)
                analysis[ftype] = {
                    "total": total_count,
                    "helpful": helpful_count,
                    "not_helpful": total_count - helpful_count,
                    "helpfulness_ratio": helpful_count / total_count if total_count > 0 else 0.0
                }
        
        return analysis
    
    def _analyze_rule_performance(self, feedback_list: List[FeedbackDetail]) -> Dict[str, Dict]:
        """Analyze performance of static analysis rules."""
        rule_stats = defaultdict(lambda: {"total": 0, "helpful": 0})
        
        for feedback in feedback_list:
            if feedback.rule_id and feedback.feedback_type == FeedbackType.FINDING:
                rule_stats[feedback.rule_id]["total"] += 1
                if feedback.is_helpful:
                    rule_stats[feedback.rule_id]["helpful"] += 1
        
        # Calculate helpfulness ratio for each rule
        rule_performance = {}
        for rule_id, stats in rule_stats.items():
            helpfulness_ratio = stats["helpful"] / stats["total"] if stats["total"] > 0 else 0.0
            rule_performance[rule_id] = {
                "total_feedback": stats["total"],
                "helpful_feedback": stats["helpful"],
                "helpfulness_ratio": round(helpfulness_ratio, 3)
            }
        
        return rule_performance
    
    def _extract_common_complaints(self, feedback_list: List[FeedbackDetail]) -> List[str]:
        """Extract common themes from negative feedback comments."""
        negative_feedback = [f for f in feedback_list if not f.is_helpful and f.comment.strip()]
        
        # Simple keyword analysis (in production, could use NLP)
        complaint_keywords = [
            "false positive", "incorrect", "wrong", "not relevant", "too many",
            "confusing", "unclear", "unhelpful", "obvious", "trivial"
        ]
        
        complaints = []
        for keyword in complaint_keywords:
            count = sum(1 for f in negative_feedback if keyword.lower() in f.comment.lower())
            if count > 0:
                complaints.append(f"'{keyword}' mentioned in {count} feedback(s)")
        
        return complaints[:5]  # Top 5 complaints
    
    def _generate_improvement_suggestions(self, feedback_list: List[FeedbackDetail]) -> List[str]:
        """Generate improvement suggestions based on feedback patterns."""
        suggestions = []
        
        # Analyze patterns in feedback
        low_helpful_types = []
        for ftype in FeedbackType:
            type_feedback = [f for f in feedback_list if f.feedback_type == ftype]
            if type_feedback:
                helpful_ratio = sum(1 for f in type_feedback if f.is_helpful) / len(type_feedback)
                if helpful_ratio < 0.5:  # Less than 50% helpful
                    low_helpful_types.append(ftype.value)
        
        if low_helpful_types:
            suggestions.append(f"Improve {', '.join(low_helpful_types)} analysis quality")
        
        # Check for common issues
        false_positive_count = sum(1 for f in feedback_list 
                                 if not f.is_helpful and "false positive" in f.comment.lower())
        if false_positive_count > 5:
            suggestions.append("Reduce false positive rate in static analysis rules")
        
        unclear_count = sum(1 for f in feedback_list 
                          if not f.is_helpful and any(word in f.comment.lower() 
                          for word in ["unclear", "confusing", "hard to understand"]))
        if unclear_count > 3:
            suggestions.append("Improve clarity of LLM suggestions and explanations")
        
        if not suggestions:
            suggestions.append("Continue monitoring feedback for improvement opportunities")
        
        return suggestions[:3]  # Top 3 suggestions 