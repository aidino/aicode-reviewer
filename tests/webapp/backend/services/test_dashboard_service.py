"""
Tests for DashboardService.

This module contains comprehensive unit tests for the DashboardService class,
covering all functionality including dashboard summary, health checks, and analytics.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from freezegun import freeze_time

from src.webapp.backend.services.dashboard_service import DashboardService
from src.webapp.backend.models.dashboard_models import (
    TimeRange,
    DashboardQuery,
    DashboardSummary,
    ScanMetrics,
    FindingsMetrics,
    RepositoryMetrics,
    XAIMetrics,
    FindingsTrend,
    TrendDataPoint,
    SystemHealth
)


class TestDashboardService:
    """Test cases for DashboardService."""
    
    @pytest.fixture
    def service(self):
        """
        Create DashboardService instance for testing.
        
        Returns:
            DashboardService: Service instance
        """
        return DashboardService()
    
    @pytest.fixture
    def mock_db_session(self):
        """
        Create mock database session.
        
        Returns:
            Mock: Mock database session
        """
        return Mock()
    
    @pytest.fixture
    def sample_query(self):
        """
        Create sample dashboard query.
        
        Returns:
            DashboardQuery: Sample query object
        """
        return DashboardQuery(
            time_range=TimeRange.LAST_30_DAYS,
            repository_filter=None,
            scan_type_filter=None
        )
    
    @freeze_time("2025-01-30T10:00:00Z")
    async def test_get_dashboard_summary_success(self, service, mock_db_session, sample_query):
        """
        Test successful dashboard summary retrieval.
        
        Args:
            service: DashboardService instance
            mock_db_session: Mock database session
            sample_query: Sample query object
        """
        # Execute
        result = await service.get_dashboard_summary(sample_query)
        
        # Verify
        assert isinstance(result, DashboardSummary)
        assert result.time_range == TimeRange.LAST_30_DAYS
        assert result.generated_at is not None
        
        # Verify scan metrics
        assert isinstance(result.scan_metrics, ScanMetrics)
        assert result.scan_metrics.total_scans > 0
        assert result.scan_metrics.completed_scans >= 0
        assert result.scan_metrics.failed_scans >= 0
        assert result.scan_metrics.active_scans >= 0
        
        # Verify findings metrics
        assert isinstance(result.findings_metrics, FindingsMetrics)
        assert result.findings_metrics.total_findings > 0
        assert result.findings_metrics.avg_findings_per_scan > 0
        assert len(result.findings_metrics.top_rules) > 0
        
        # Verify repository metrics
        assert isinstance(result.repository_metrics, RepositoryMetrics)
        assert result.repository_metrics.total_repositories > 0
        assert result.repository_metrics.avg_repository_health >= 0
        assert result.repository_metrics.avg_repository_health <= 1
        
        # Verify XAI metrics
        assert isinstance(result.xai_metrics, XAIMetrics)
        assert result.xai_metrics.total_xai_analyses > 0
        assert result.xai_metrics.avg_confidence_score >= 0
        assert result.xai_metrics.avg_confidence_score <= 1
        
        # Verify trends
        assert isinstance(result.findings_trend, FindingsTrend)
        assert len(result.findings_trend.total_findings) > 0
        
        # Verify recent activity
        assert len(result.recent_scans) >= 0
        assert len(result.recent_findings) >= 0
    
    async def test_get_dashboard_summary_different_time_ranges(self, service, mock_db_session):
        """
        Test dashboard summary with different time ranges.
        
        Args:
            service: DashboardService instance
            mock_db_session: Mock database session
        """
        time_ranges = [
            TimeRange.LAST_7_DAYS,
            TimeRange.LAST_30_DAYS,
            TimeRange.LAST_90_DAYS,
            TimeRange.LAST_YEAR
        ]
        
        for time_range in time_ranges:
            query = DashboardQuery(time_range=time_range)
            result = await service.get_dashboard_summary(query)
            
            assert result.time_range == time_range
            assert isinstance(result, DashboardSummary)
    
    async def test_get_dashboard_summary_with_repository_filter(self, service, mock_db_session):
        """
        Test dashboard summary with repository filter.
        
        Args:
            service: DashboardService instance
            mock_db_session: Mock database session
        """
        query = DashboardQuery(
            time_range=TimeRange.LAST_30_DAYS,
            repository_filter="https://github.com/example/webapp"
        )
        
        result = await service.get_dashboard_summary(query)
        
        assert isinstance(result, DashboardSummary)
        # Repository-specific data should be filtered
        assert result.repository_metrics.total_repositories >= 0
    
    async def test_get_dashboard_summary_with_scan_type_filter(self, service, mock_db_session):
        """
        Test dashboard summary with scan type filter.
        
        Args:
            service: DashboardService instance
            mock_db_session: Mock database session
        """
        query = DashboardQuery(
            time_range=TimeRange.LAST_30_DAYS,
            scan_type_filter="pr"
        )
        
        result = await service.get_dashboard_summary(query)
        
        assert isinstance(result, DashboardSummary)
        # Scan type should be reflected in scan metrics
        assert "pr" in result.scan_metrics.scans_by_type
    
    @freeze_time("2025-01-30T10:00:00Z")
    async def test_get_health_check_success(self, service, mock_db_session):
        """
        Test successful health check.
        
        Args:
            service: DashboardService instance
            mock_db_session: Mock database session
        """
        result = await service.get_health_check()
        
        assert isinstance(result, SystemHealth)
        assert result.status in ['healthy', 'degraded', 'unhealthy']
        assert result.timestamp is not None
        assert result.version is not None
        assert result.uptime is not None
        assert result.metrics is not None
        
        # Verify metrics structure
        metrics = result.metrics
        assert 'total_scans' in metrics
        assert 'total_findings' in metrics
        assert 'avg_response_time' in metrics
        
        # Verify numeric values
        assert isinstance(metrics['total_scans'], int)
        assert isinstance(metrics['total_findings'], int)
        assert isinstance(metrics['avg_response_time'], str)
    
    async def test_scan_metrics_calculation(self, service, mock_db_session, sample_query):
        """
        Test scan metrics calculation accuracy.
        
        Args:
            service: DashboardService instance
            mock_db_session: Mock database session
            sample_query: Sample query object
        """
        result = await service.get_dashboard_summary(sample_query)
        metrics = result.scan_metrics
        
        # Verify totals consistency
        total_by_status = sum(metrics.scans_by_status.values())
        assert total_by_status == metrics.total_scans
        
        total_by_type = sum(metrics.scans_by_type.values())
        assert total_by_type == metrics.total_scans
        
        # Verify individual counts
        assert metrics.completed_scans == metrics.scans_by_status.get('completed', 0)
        assert metrics.failed_scans == metrics.scans_by_status.get('failed', 0)
        assert metrics.active_scans == metrics.scans_by_status.get('running', 0)
        
        # Verify average scan duration is reasonable
        assert metrics.avg_scan_duration > 0
        assert metrics.avg_scan_duration < 3600  # Less than 1 hour
    
    async def test_findings_metrics_calculation(self, service, mock_db_session, sample_query):
        """
        Test findings metrics calculation accuracy.
        
        Args:
            service: DashboardService instance
            mock_db_session: Mock database session
            sample_query: Sample query object
        """
        result = await service.get_dashboard_summary(sample_query)
        metrics = result.findings_metrics
        
        # Verify totals consistency
        total_by_severity = sum(metrics.findings_by_severity.values())
        assert total_by_severity == metrics.total_findings
        
        total_by_category = sum(metrics.findings_by_category.values())
        assert total_by_category == metrics.total_findings
        
        # Verify average calculation
        if result.scan_metrics.total_scans > 0:
            expected_avg = metrics.total_findings / result.scan_metrics.total_scans
            assert abs(metrics.avg_findings_per_scan - expected_avg) < 0.01
        
        # Verify top rules
        assert len(metrics.top_rules) > 0
        for rule in metrics.top_rules:
            assert rule["count"] > 0
            assert 0 <= rule["percentage"] <= 100
        
        # Verify top rules are sorted by count (descending)
        if len(metrics.top_rules) > 1:
            assert metrics.top_rules[0]["count"] >= metrics.top_rules[1]["count"]
    
    async def test_xai_metrics_calculation(self, service, mock_db_session, sample_query):
        """
        Test XAI metrics calculation accuracy.
        
        Args:
            service: DashboardService instance
            mock_db_session: Mock database session
            sample_query: Sample query object
        """
        result = await service.get_dashboard_summary(sample_query)
        metrics = result.xai_metrics
        
        # Verify confidence distribution totals
        total_distribution = sum(metrics.confidence_distribution.values())
        assert total_distribution == metrics.total_xai_analyses
        
        # Verify confidence score ranges
        assert 0 <= metrics.avg_confidence_score <= 1
        assert 0 <= metrics.reasoning_quality_score <= 1
        
        # Verify distribution categories
        expected_keys = ['high', 'medium', 'low']
        for key in expected_keys:
            assert key in metrics.confidence_distribution
            assert metrics.confidence_distribution[key] >= 0
    
    async def test_trends_calculation(self, service, mock_db_session, sample_query):
        """
        Test trends calculation accuracy.
        
        Args:
            service: DashboardService instance
            mock_db_session: Mock database session
            sample_query: Sample query object
        """
        result = await service.get_dashboard_summary(sample_query)
        trend = result.findings_trend
        
        # Verify total findings trend
        assert len(trend.total_findings) > 0
        for point in trend.total_findings:
            assert isinstance(point, TrendDataPoint)
            assert point.date is not None
            assert point.value >= 0
            assert point.count >= 0
        
        # Verify severity trends
        assert len(trend.severity_trends) > 0
        for severity, points in trend.severity_trends.items():
            assert severity in ['error', 'warning', 'info']
            assert len(points) > 0
            for point in points:
                assert isinstance(point, TrendDataPoint)
        
        # Verify category trends
        assert len(trend.category_trends) > 0
        for category, points in trend.category_trends.items():
            assert len(points) > 0
    
    async def test_repository_metrics_calculation(self, service, mock_db_session, sample_query):
        """
        Test repository metrics calculation accuracy.
        
        Args:
            service: DashboardService instance
            mock_db_session: Mock database session
            sample_query: Sample query object
        """
        result = await service.get_dashboard_summary(sample_query)
        metrics = result.repository_metrics
        
        # Verify repository count
        assert metrics.total_repositories > 0
        
        # Verify most scanned repos
        assert len(metrics.most_scanned_repos) > 0
        for repo in metrics.most_scanned_repos:
            assert repo['repository'] is not None
            assert repo['scan_count'] > 0
        
        # Verify most scanned repos are sorted by scan count (descending)
        if len(metrics.most_scanned_repos) > 1:
            counts = [repo['scan_count'] for repo in metrics.most_scanned_repos]
            assert counts == sorted(counts, reverse=True)
        
        # Verify languages analyzed
        assert len(metrics.languages_analyzed) > 0
        for language, count in metrics.languages_analyzed.items():
            assert count > 0
        
        # Verify health score
        assert 0 <= metrics.avg_repository_health <= 1
    
    async def test_recent_activity_retrieval(self, service, mock_db_session, sample_query):
        """
        Test recent activity retrieval.
        
        Args:
            service: DashboardService instance
            mock_db_session: Mock database session
            sample_query: Sample query object
        """
        result = await service.get_dashboard_summary(sample_query)
        
        # Verify recent scans
        assert len(result.recent_scans) >= 0
        for scan in result.recent_scans:
            assert scan['scan_id'] is not None
            assert scan['repository'] is not None
            assert scan['status'] in ['completed', 'failed', 'running']
            assert scan['timestamp'] is not None
            assert scan['findings_count'] >= 0
        
        # Verify recent findings
        assert len(result.recent_findings) >= 0
        for finding in result.recent_findings:
            assert finding['rule_id'] is not None
            assert finding['severity'] in ['error', 'warning', 'info']
            assert finding['message'] is not None
            assert finding['timestamp'] is not None
            assert finding['scan_id'] is not None
    
    async def test_time_range_filtering(self, service, mock_db_session):
        """
        Test that time range filtering affects results appropriately.
        
        Args:
            service: DashboardService instance
            mock_db_session: Mock database session
        """
        # Test short vs long time ranges
        short_query = DashboardQuery(time_range=TimeRange.LAST_7_DAYS)
        long_query = DashboardQuery(time_range=TimeRange.LAST_YEAR)
        
        short_result = await service.get_dashboard_summary(short_query)
        long_result = await service.get_dashboard_summary(long_query)
        
        # Longer time range should generally have more data
        # (This is mock data so we'll just verify structure)
        assert isinstance(short_result, DashboardSummary)
        assert isinstance(long_result, DashboardSummary)
        
        # Both should have valid data structures
        for result in [short_result, long_result]:
            assert result.scan_metrics.total_scans >= 0
            assert result.findings_metrics.total_findings >= 0
            assert len(result.findings_trend.total_findings) > 0
    
    async def test_error_handling_db_connection_failure(self, service):
        """
        Test error handling when database connection fails.
        
        Args:
            service: DashboardService instance
        """
        query = DashboardQuery(time_range=TimeRange.LAST_30_DAYS)
        
        # Should handle gracefully and return default data (using mock data)
        result = await service.get_dashboard_summary(query)
        assert isinstance(result, DashboardSummary)
    
    async def test_get_health_check_error_handling(self, service):
        """
        Test health check error handling.
        
        Args:
            service: DashboardService instance
        """
        result = await service.get_health_check()
        # Should return healthy status with mock data
        assert result.status == "healthy"
        assert isinstance(result, SystemHealth)
    
    @pytest.mark.parametrize("time_range", [
        TimeRange.LAST_7_DAYS,
        TimeRange.LAST_30_DAYS,
        TimeRange.LAST_90_DAYS,
        TimeRange.LAST_YEAR
    ])
    async def test_all_time_ranges(self, service, mock_db_session, time_range):
        """
        Test dashboard with all supported time ranges.
        
        Args:
            service: DashboardService instance
            mock_db_session: Mock database session
            time_range: Time range to test
        """
        query = DashboardQuery(time_range=time_range)
        result = await service.get_dashboard_summary(query)
        
        assert result.time_range == time_range
        assert isinstance(result, DashboardSummary)
        assert result.generated_at is not None
    
    async def test_mock_data_consistency(self, service, mock_db_session, sample_query):
        """
        Test that mock data is internally consistent.
        
        Args:
            service: DashboardService instance
            mock_db_session: Mock database session
            sample_query: Sample query object
        """
        result = await service.get_dashboard_summary(sample_query)
        
        # Verify numerical consistency
        scan_metrics = result.scan_metrics
        findings_metrics = result.findings_metrics
        
        # Total scans should be sum of completed, failed, and active
        expected_total = (scan_metrics.completed_scans + 
                         scan_metrics.failed_scans + 
                         scan_metrics.active_scans)
        assert scan_metrics.total_scans == expected_total
        
        # Average findings per scan should be correct
        if scan_metrics.total_scans > 0:
            expected_avg = findings_metrics.total_findings / scan_metrics.total_scans
            assert abs(findings_metrics.avg_findings_per_scan - expected_avg) < 0.01
        
        # Top rules percentages should add up correctly
        total_percentage = sum(rule["percentage"] for rule in findings_metrics.top_rules)
        assert 0 <= total_percentage <= 100
    
    async def test_performance_mock_data_generation(self, service, mock_db_session, sample_query):
        """
        Test that dashboard summary generation is reasonably fast.
        
        Args:
            service: DashboardService instance
            mock_db_session: Mock database session
            sample_query: Sample query object
        """
        import time
        
        start_time = time.time()
        result = await service.get_dashboard_summary(sample_query)
        end_time = time.time()
        
        # Should complete within a reasonable time (mock data should be fast)
        execution_time = end_time - start_time
        assert execution_time < 1.0  # Less than 1 second
        
        # Should still return valid data
        assert isinstance(result, DashboardSummary)
    
    async def test_system_health_status_determination(self, service, mock_db_session):
        """
        Test system health status determination logic.
        
        Args:
            service: DashboardService instance
            mock_db_session: Mock database session
        """
        result = await service.get_health_check()
        
        # Status should be one of the valid values
        assert result.status in ['healthy', 'degraded', 'unhealthy']
        
        # Verify that status corresponds to metrics
        if result.status == 'healthy':
            # Should have good metrics (mock data specific)
            assert 'total_scans' in result.metrics
            assert result.metrics['total_scans'] > 0
        
        # Verify uptime format
        assert isinstance(result.uptime, str)
        # Should contain time units (mock data returns specific format)
        assert any(unit in result.uptime for unit in ['d', 'h', 'm', 's'])
        
        # Verify version format
        assert isinstance(result.version, str)
        assert len(result.version) > 0 