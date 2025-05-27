"""
Unit tests for FeedbackService.

Tests the business logic for handling user feedback on scan results
and LLM suggestions, including storage, retrieval, and analytics.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import uuid

from src.webapp.backend.services.feedback_service import FeedbackService
from src.webapp.backend.models.feedback_models import (
    FeedbackRequest,
    FeedbackResponse,
    FeedbackDetail,
    FeedbackSummary,
    FeedbackQuery,
    FeedbackAnalytics,
    FeedbackType,
    FeedbackRating,
)


@pytest.fixture
def feedback_service():
    """Create FeedbackService instance for testing."""
    return FeedbackService()


@pytest.fixture
def sample_feedback_request():
    """Create sample feedback request."""
    return FeedbackRequest(
        scan_id="scan_123",
        finding_id="finding_456",
        feedback_type=FeedbackType.FINDING,
        is_helpful=True,
        rating=FeedbackRating.HELPFUL,
        comment="This finding was very useful",
        user_id="user_789",
        item_content="print('debug message')",
        rule_id="print_statements",
        suggestion_type="code_quality"
    )


@pytest.fixture
def sample_feedback_detail():
    """Create sample feedback detail."""
    return FeedbackDetail(
        feedback_id="feedback_123",
        scan_id="scan_123",
        finding_id="finding_456",
        feedback_type=FeedbackType.FINDING,
        is_helpful=True,
        rating=FeedbackRating.HELPFUL,
        comment="Very helpful finding",
        user_id="user_789",
        item_content="print('debug')",
        rule_id="print_statements",
        suggestion_type=None,
        timestamp=datetime.utcnow(),
        metadata={"version": "1.0"}
    )


class TestFeedbackServiceInitialization:
    """Test cases for FeedbackService initialization."""
    
    def test_init_without_db_connection(self):
        """Test initialization without database connection."""
        service = FeedbackService()
        assert service.db_connection is None
        assert isinstance(service._feedback_storage, dict)
        assert isinstance(service._scan_feedback_index, dict)
    
    def test_init_with_db_connection(self):
        """Test initialization with database connection."""
        mock_db = MagicMock()
        service = FeedbackService(db_connection=mock_db)
        assert service.db_connection is mock_db
    
    def test_init_creates_empty_storage(self):
        """Test that initialization creates empty storage."""
        service = FeedbackService()
        assert len(service._feedback_storage) == 0
        assert len(service._scan_feedback_index) == 0


class TestSubmitFeedback:
    """Test cases for feedback submission."""
    
    @pytest.mark.asyncio
    async def test_submit_feedback_success(self, feedback_service, sample_feedback_request):
        """Test successful feedback submission."""
        response = await feedback_service.submit_feedback(sample_feedback_request)
        
        # Verify response
        assert isinstance(response, FeedbackResponse)
        assert response.message == "Feedback submitted successfully"
        assert isinstance(response.feedback_id, str)
        assert isinstance(response.timestamp, datetime)
        
        # Verify feedback was stored
        assert len(feedback_service._feedback_storage) == 1
        assert response.feedback_id in feedback_service._feedback_storage
        
        # Verify scan index was updated
        assert "scan_123" in feedback_service._scan_feedback_index
        assert response.feedback_id in feedback_service._scan_feedback_index["scan_123"]
    
    @pytest.mark.asyncio
    async def test_submit_feedback_empty_scan_id(self, feedback_service):
        """Test feedback submission with empty scan_id."""
        request = FeedbackRequest(
            scan_id="",
            feedback_type=FeedbackType.FINDING,
            is_helpful=True,
            comment="Test"
        )
        
        with pytest.raises(ValueError, match="scan_id is required"):
            await feedback_service.submit_feedback(request)
    
    @pytest.mark.asyncio
    async def test_submit_feedback_missing_feedback_type(self, feedback_service):
        """Test feedback submission with missing feedback_type."""
        # Test that Pydantic validation works - this should raise ValidationError
        with pytest.raises(Exception):  # Pydantic ValidationError when creating model
            request = FeedbackRequest(
                scan_id="scan_123",
                feedback_type=None,  # This would cause Pydantic validation error
                is_helpful=True,
                comment="Test"
            )
    
    @pytest.mark.asyncio
    async def test_submit_feedback_creates_metadata(self, feedback_service, sample_feedback_request):
        """Test that feedback submission creates proper metadata."""
        response = await feedback_service.submit_feedback(sample_feedback_request)
        
        stored_feedback = feedback_service._feedback_storage[response.feedback_id]
        assert stored_feedback.metadata is not None
        assert stored_feedback.metadata["user_agent"] == "webapp"
        assert stored_feedback.metadata["submission_method"] == "api"
        assert stored_feedback.metadata["version"] == "1.0"
    
    @pytest.mark.asyncio
    async def test_submit_feedback_storage_error(self, feedback_service, sample_feedback_request):
        """Test feedback submission with storage error."""
        # Mock storage to raise exception
        with patch.object(feedback_service, '_store_feedback', side_effect=Exception("Storage failed")):
            with pytest.raises(Exception, match="Failed to submit feedback"):
                await feedback_service.submit_feedback(sample_feedback_request)


class TestGetFeedbackSummary:
    """Test cases for feedback summary retrieval."""
    
    @pytest.mark.asyncio
    async def test_get_feedback_summary_empty(self, feedback_service):
        """Test feedback summary for scan with no feedback."""
        summary = await feedback_service.get_feedback_summary("scan_empty")
        
        assert summary.scan_id == "scan_empty"
        assert summary.total_feedback_count == 0
        assert summary.helpful_count == 0
        assert summary.not_helpful_count == 0
        assert summary.feedback_types == {}
        assert summary.average_rating is None
    
    @pytest.mark.asyncio
    async def test_get_feedback_summary_with_feedback(self, feedback_service):
        """Test feedback summary with existing feedback."""
        # Add some feedback
        await self._add_test_feedback(feedback_service, "scan_123", 5, 3)
        
        summary = await feedback_service.get_feedback_summary("scan_123")
        
        assert summary.scan_id == "scan_123"
        assert summary.total_feedback_count == 8
        assert summary.helpful_count == 5
        assert summary.not_helpful_count == 3
        assert len(summary.feedback_types) > 0
    
    @pytest.mark.asyncio
    async def test_get_feedback_summary_with_ratings(self, feedback_service):
        """Test feedback summary calculation with ratings."""
        # Add feedback with ratings
        requests = [
            FeedbackRequest(
                scan_id="scan_ratings",
                feedback_type=FeedbackType.FINDING,
                is_helpful=True,
                rating=FeedbackRating.VERY_HELPFUL,
                comment="Excellent"
            ),
            FeedbackRequest(
                scan_id="scan_ratings",
                feedback_type=FeedbackType.FINDING,
                is_helpful=True,
                rating=FeedbackRating.HELPFUL,
                comment="Good"
            ),
            FeedbackRequest(
                scan_id="scan_ratings",
                feedback_type=FeedbackType.FINDING,
                is_helpful=False,
                rating=FeedbackRating.NOT_HELPFUL,
                comment="Poor"
            )
        ]
        
        for request in requests:
            await feedback_service.submit_feedback(request)
        
        summary = await feedback_service.get_feedback_summary("scan_ratings")
        
        # Rating values: VERY_HELPFUL=5, HELPFUL=4, NOT_HELPFUL=2
        # Average: (5 + 4 + 2) / 3 = 3.67
        assert summary.average_rating == 3.67
    
    @pytest.mark.asyncio
    async def test_get_feedback_summary_error_handling(self, feedback_service):
        """Test feedback summary error handling."""
        with patch.object(feedback_service, '_get_feedback_by_scan', side_effect=Exception("Database error")):
            with pytest.raises(Exception, match="Failed to get feedback summary"):
                await feedback_service.get_feedback_summary("scan_error")
    
    async def _add_test_feedback(self, service, scan_id, helpful_count, not_helpful_count):
        """Helper method to add test feedback."""
        # Add helpful feedback
        for i in range(helpful_count):
            request = FeedbackRequest(
                scan_id=scan_id,
                feedback_type=FeedbackType.FINDING,
                is_helpful=True,
                comment=f"Helpful feedback {i}"
            )
            await service.submit_feedback(request)
        
        # Add not helpful feedback
        for i in range(not_helpful_count):
            request = FeedbackRequest(
                scan_id=scan_id,
                feedback_type=FeedbackType.LLM_SUGGESTION,
                is_helpful=False,
                comment=f"Not helpful feedback {i}"
            )
            await service.submit_feedback(request)


class TestQueryFeedback:
    """Test cases for feedback querying."""
    
    @pytest.mark.asyncio
    async def test_query_feedback_no_filters(self, feedback_service):
        """Test feedback query without filters."""
        # Add some test feedback
        await self._add_sample_feedback(feedback_service)
        
        query = FeedbackQuery()
        results = await feedback_service.query_feedback(query)
        
        assert len(results) > 0
        assert all(isinstance(feedback, FeedbackDetail) for feedback in results)
    
    @pytest.mark.asyncio
    async def test_query_feedback_with_scan_id_filter(self, feedback_service):
        """Test feedback query with scan_id filter."""
        # Add feedback for different scans
        await self._add_sample_feedback(feedback_service)
        
        query = FeedbackQuery(scan_id="scan_123")
        results = await feedback_service.query_feedback(query)
        
        assert all(feedback.scan_id == "scan_123" for feedback in results)
    
    @pytest.mark.asyncio
    async def test_query_feedback_with_helpfulness_filter(self, feedback_service):
        """Test feedback query with helpfulness filter."""
        await self._add_sample_feedback(feedback_service)
        
        query = FeedbackQuery(is_helpful=True)
        results = await feedback_service.query_feedback(query)
        
        assert all(feedback.is_helpful is True for feedback in results)
    
    @pytest.mark.asyncio
    async def test_query_feedback_with_pagination(self, feedback_service):
        """Test feedback query with pagination."""
        await self._add_sample_feedback(feedback_service)
        
        # Test first page
        query = FeedbackQuery(limit=2, offset=0)
        results_page1 = await feedback_service.query_feedback(query)
        assert len(results_page1) <= 2
        
        # Test second page
        query = FeedbackQuery(limit=2, offset=2)
        results_page2 = await feedback_service.query_feedback(query)
        
        # Results should be different
        if len(results_page1) == 2 and len(results_page2) > 0:
            assert results_page1[0].feedback_id != results_page2[0].feedback_id
    
    @pytest.mark.asyncio
    async def test_query_feedback_sorting(self, feedback_service):
        """Test that feedback query returns results sorted by timestamp."""
        # Add feedback with different timestamps
        base_time = datetime.utcnow()
        
        for i in range(3):
            request = FeedbackRequest(
                scan_id="scan_sort",
                feedback_type=FeedbackType.FINDING,
                is_helpful=True,
                comment=f"Feedback {i}"
            )
            response = await feedback_service.submit_feedback(request)
            
            # Manually adjust timestamp for testing
            feedback = feedback_service._feedback_storage[response.feedback_id]
            feedback.timestamp = base_time + timedelta(seconds=i)
        
        query = FeedbackQuery(scan_id="scan_sort")
        results = await feedback_service.query_feedback(query)
        
        # Should be sorted by timestamp descending (newest first)
        for i in range(len(results) - 1):
            assert results[i].timestamp >= results[i + 1].timestamp
    
    async def _add_sample_feedback(self, service):
        """Helper method to add sample feedback for testing."""
        requests = [
            FeedbackRequest(
                scan_id="scan_123",
                feedback_type=FeedbackType.FINDING,
                is_helpful=True,
                comment="Good finding"
            ),
            FeedbackRequest(
                scan_id="scan_123",
                feedback_type=FeedbackType.LLM_SUGGESTION,
                is_helpful=False,
                comment="Poor suggestion"
            ),
            FeedbackRequest(
                scan_id="scan_456",
                feedback_type=FeedbackType.FINDING,
                is_helpful=True,
                comment="Another good finding"
            )
        ]
        
        for request in requests:
            await service.submit_feedback(request)


class TestFeedbackAnalytics:
    """Test cases for feedback analytics."""
    
    @pytest.mark.asyncio
    async def test_get_feedback_analytics_empty(self, feedback_service):
        """Test analytics with no feedback."""
        analytics = await feedback_service.get_feedback_analytics(30)
        
        assert analytics.total_feedback == 0
        assert analytics.helpfulness_ratio == 0.0
        assert analytics.feedback_by_type == {}
        assert analytics.rule_performance == {}
        assert analytics.common_complaints == []
        assert analytics.improvement_suggestions == ["Continue monitoring feedback for improvement opportunities"]
    
    @pytest.mark.asyncio
    async def test_get_feedback_analytics_with_data(self, feedback_service):
        """Test analytics with feedback data."""
        # Add test feedback
        await self._add_analytics_test_data(feedback_service)
        
        analytics = await feedback_service.get_feedback_analytics(30)
        
        assert analytics.total_feedback > 0
        assert 0 <= analytics.helpfulness_ratio <= 1
        assert len(analytics.feedback_by_type) > 0
        assert isinstance(analytics.time_period, dict)
        assert "start" in analytics.time_period
        assert "end" in analytics.time_period
    
    @pytest.mark.asyncio
    async def test_analyze_rule_performance(self, feedback_service):
        """Test rule performance analysis."""
        # Add feedback for specific rules
        rule_feedback = [
            FeedbackRequest(
                scan_id="scan_rules",
                feedback_type=FeedbackType.FINDING,
                is_helpful=True,
                rule_id="print_statements",
                comment="Good rule"
            ),
            FeedbackRequest(
                scan_id="scan_rules",
                feedback_type=FeedbackType.FINDING,
                is_helpful=False,
                rule_id="print_statements",
                comment="Too many false positives"
            ),
            FeedbackRequest(
                scan_id="scan_rules",
                feedback_type=FeedbackType.FINDING,
                is_helpful=True,
                rule_id="unused_imports",
                comment="Very helpful"
            )
        ]
        
        for request in rule_feedback:
            await feedback_service.submit_feedback(request)
        
        analytics = await feedback_service.get_feedback_analytics(30)
        
        assert "print_statements" in analytics.rule_performance
        assert "unused_imports" in analytics.rule_performance
        
        print_rule = analytics.rule_performance["print_statements"]
        assert print_rule["total_feedback"] == 2
        assert print_rule["helpful_feedback"] == 1
        assert print_rule["helpfulness_ratio"] == 0.5
    
    @pytest.mark.asyncio
    async def test_extract_common_complaints(self, feedback_service):
        """Test extraction of common complaint themes."""
        complaints = [
            "This is a false positive",
            "The finding is incorrect and not relevant",
            "Too many false positives in this report",
            "The suggestion is confusing and unclear"
        ]
        
        for i, comment in enumerate(complaints):
            request = FeedbackRequest(
                scan_id="scan_complaints",
                feedback_type=FeedbackType.FINDING,
                is_helpful=False,
                comment=comment
            )
            await feedback_service.submit_feedback(request)
        
        analytics = await feedback_service.get_feedback_analytics(30)
        
        # Should detect "false positive" mentioned multiple times
        false_positive_complaints = [c for c in analytics.common_complaints if "false positive" in c]
        assert len(false_positive_complaints) > 0
    
    async def _add_analytics_test_data(self, service):
        """Helper method to add test data for analytics."""
        test_data = [
            (FeedbackType.FINDING, True, "print_statements"),
            (FeedbackType.FINDING, False, "print_statements"),
            (FeedbackType.LLM_SUGGESTION, True, None),
            (FeedbackType.LLM_INSIGHT, False, None),
            (FeedbackType.FINDING, True, "unused_imports")
        ]
        
        for feedback_type, is_helpful, rule_id in test_data:
            request = FeedbackRequest(
                scan_id="scan_analytics",
                feedback_type=feedback_type,
                is_helpful=is_helpful,
                rule_id=rule_id,
                comment="Test feedback for analytics"
            )
            await service.submit_feedback(request)


class TestFeedbackServiceHelperMethods:
    """Test cases for helper methods."""
    
    @pytest.mark.asyncio
    async def test_store_feedback(self, feedback_service, sample_feedback_detail):
        """Test feedback storage."""
        await feedback_service._store_feedback(sample_feedback_detail)
        
        assert sample_feedback_detail.feedback_id in feedback_service._feedback_storage
        assert sample_feedback_detail.scan_id in feedback_service._scan_feedback_index
        assert sample_feedback_detail.feedback_id in feedback_service._scan_feedback_index[sample_feedback_detail.scan_id]
    
    @pytest.mark.asyncio
    async def test_get_feedback_by_scan(self, feedback_service, sample_feedback_detail):
        """Test retrieving feedback by scan ID."""
        await feedback_service._store_feedback(sample_feedback_detail)
        
        feedback_list = await feedback_service._get_feedback_by_scan(sample_feedback_detail.scan_id)
        
        assert len(feedback_list) == 1
        assert feedback_list[0].feedback_id == sample_feedback_detail.feedback_id
    
    def test_analyze_feedback_by_type(self, feedback_service):
        """Test feedback analysis by type."""
        feedback_list = [
            FeedbackDetail(
                feedback_id="f1",
                scan_id="scan_123",
                feedback_type=FeedbackType.FINDING,
                is_helpful=True,
                comment="test",
                timestamp=datetime.utcnow()
            ),
            FeedbackDetail(
                feedback_id="f2",
                scan_id="scan_123",
                feedback_type=FeedbackType.FINDING,
                is_helpful=False,
                comment="test",
                timestamp=datetime.utcnow()
            )
        ]
        
        analysis = feedback_service._analyze_feedback_by_type(feedback_list)
        
        assert FeedbackType.FINDING in analysis
        finding_analysis = analysis[FeedbackType.FINDING]
        assert finding_analysis["total"] == 2
        assert finding_analysis["helpful"] == 1
        assert finding_analysis["not_helpful"] == 1
        assert finding_analysis["helpfulness_ratio"] == 0.5 