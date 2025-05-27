"""
DashboardService for AI Code Review System.

Provides aggregated analytics and dashboard data for web application,
including scan metrics, findings trends, and system health indicators.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter

from ..models.dashboard_models import (
    DashboardSummary, DashboardQuery, TimeRange, TrendDataPoint,
    ScanMetrics, FindingsMetrics, RepositoryMetrics, XAIMetrics,
    FindingsTrend, SystemHealth
)
from ..models.scan_models import ScanType, ScanStatus, SeverityLevel

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Service for dashboard analytics and aggregated data.
    
    Provides comprehensive metrics, trends, and insights for the
    AI Code Review system dashboard interface.
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize DashboardService.
        
        Args:
            db_connection: Database connection (PostgreSQL)
                         If None, uses mock data for development
        """
        self.db_connection = db_connection
        self.start_time = datetime.now()
        
        # Mock data storage for development - will be generated on first use
        self._mock_scans = None
        self._mock_findings = None
        
        logger.info("DashboardService initialized")
    
    async def get_dashboard_summary(self, query: DashboardQuery) -> DashboardSummary:
        """
        Get comprehensive dashboard summary data.
        
        Args:
            query: Dashboard query parameters
            
        Returns:
            DashboardSummary with aggregated metrics and trends
        """
        try:
            logger.info(f"Generating dashboard summary for {query.time_range}")
            
            # Calculate date range
            end_date = datetime.now()
            start_date = self._get_start_date(query.time_range, end_date)
            
            # Filter data by time range and query parameters
            filtered_scans = self._filter_scans(start_date, end_date, query)
            filtered_findings = self._filter_findings(filtered_scans, query)
            
            # Generate metrics
            scan_metrics = self._calculate_scan_metrics(filtered_scans)
            findings_metrics = self._calculate_findings_metrics(filtered_findings)
            repository_metrics = self._calculate_repository_metrics(filtered_scans)
            xai_metrics = self._calculate_xai_metrics(filtered_findings)
            
            # Generate trends
            findings_trend = self._calculate_findings_trend(start_date, end_date, filtered_findings)
            
            # Get recent activity
            recent_scans = self._get_recent_scans(filtered_scans)
            recent_findings = self._get_recent_findings(filtered_findings)
            
            # System health
            system_health = self._calculate_system_health()
            
            return DashboardSummary(
                time_range=query.time_range,
                generated_at=datetime.now(),
                scan_metrics=scan_metrics,
                findings_metrics=findings_metrics,
                repository_metrics=repository_metrics,
                xai_metrics=xai_metrics,
                findings_trend=findings_trend,
                recent_scans=recent_scans,
                recent_findings=recent_findings,
                system_health=system_health
            )
            
        except Exception as e:
            logger.error(f"Error generating dashboard summary: {e}")
            raise Exception(f"Failed to generate dashboard summary: {str(e)}")
    
    async def get_health_check(self) -> SystemHealth:
        """Get system health check status."""
        if self._mock_scans is None:
            self._mock_scans = self._generate_mock_scans()
        if self._mock_findings is None:
            self._mock_findings = self._generate_mock_findings()
            
        uptime = datetime.now() - self.start_time
        uptime_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"
        
        return SystemHealth(
            status="healthy",
            timestamp=datetime.now(),
            version="1.0.0",
            uptime=uptime_str,
            metrics={
                "total_scans": len(self._mock_scans),
                "total_findings": len(self._mock_findings),
                "avg_response_time": "150ms"
            }
        )
    
    def _get_start_date(self, time_range: TimeRange, end_date: datetime) -> datetime:
        """Calculate start date based on time range."""
        if time_range == TimeRange.LAST_7_DAYS:
            return end_date - timedelta(days=7)
        elif time_range == TimeRange.LAST_30_DAYS:
            return end_date - timedelta(days=30)
        elif time_range == TimeRange.LAST_90_DAYS:
            return end_date - timedelta(days=90)
        elif time_range == TimeRange.LAST_YEAR:
            return end_date - timedelta(days=365)
        else:
            return end_date - timedelta(days=30)  # Default
    
    def _filter_scans(self, start_date: datetime, end_date: datetime, query: DashboardQuery) -> List[Dict]:
        """Filter scans based on query parameters."""
        if self._mock_scans is None:
            self._mock_scans = self._generate_mock_scans()
            
        filtered = []
        
        for scan in self._mock_scans:
            scan_date = datetime.fromisoformat(scan["timestamp"])
            
            # Time range filter
            if not (start_date <= scan_date <= end_date):
                continue
            
            # Repository filter
            if query.repository_filter and scan["repository"] != query.repository_filter:
                continue
            
            # Scan type filter
            if query.scan_type_filter and scan["scan_type"] != query.scan_type_filter:
                continue
            
            filtered.append(scan)
        
        return filtered
    
    def _filter_findings(self, scans: List[Dict], query: DashboardQuery) -> List[Dict]:
        """Filter findings based on associated scans."""
        if self._mock_findings is None:
            self._mock_findings = self._generate_mock_findings()
            
        scan_ids = {scan["scan_id"] for scan in scans}
        return [f for f in self._mock_findings if f["scan_id"] in scan_ids]
    
    def _calculate_scan_metrics(self, scans: List[Dict]) -> ScanMetrics:
        """Calculate aggregated scan metrics."""
        total_scans = len(scans)
        
        status_counts = Counter(scan["status"] for scan in scans)
        type_counts = Counter(scan["scan_type"] for scan in scans)
        
        # Calculate average duration
        durations = [scan.get("duration", 300) for scan in scans if scan.get("duration")]
        avg_duration = sum(durations) / len(durations) / 60 if durations else 0  # Convert to minutes
        
        return ScanMetrics(
            total_scans=total_scans,
            active_scans=status_counts.get("running", 0),
            completed_scans=status_counts.get("completed", 0),
            failed_scans=status_counts.get("failed", 0),
            avg_scan_duration=round(avg_duration, 1),
            scans_by_type=dict(type_counts),
            scans_by_status=dict(status_counts)
        )
    
    def _calculate_findings_metrics(self, findings: List[Dict]) -> FindingsMetrics:
        """Calculate aggregated findings metrics."""
        total_findings = len(findings)
        
        severity_counts = Counter(finding["severity"] for finding in findings)
        category_counts = Counter(finding["category"] for finding in findings)
        rule_counts = Counter(finding["rule_id"] for finding in findings)
        
        # Calculate average findings per scan
        scan_ids = set(finding["scan_id"] for finding in findings)
        avg_per_scan = total_findings / len(scan_ids) if scan_ids else 0
        
        # Top rules
        top_rules = [
            {"rule_id": rule, "count": count, "percentage": round(count/total_findings*100, 1)}
            for rule, count in rule_counts.most_common(5)
        ]
        
        return FindingsMetrics(
            total_findings=total_findings,
            avg_findings_per_scan=round(avg_per_scan, 1),
            findings_by_severity=dict(severity_counts),
            findings_by_category=dict(category_counts),
            top_rules=top_rules
        )
    
    def _calculate_repository_metrics(self, scans: List[Dict]) -> RepositoryMetrics:
        """Calculate repository-specific metrics."""
        repo_counts = Counter(scan["repository"] for scan in scans)
        lang_counts = Counter(scan.get("primary_language", "unknown") for scan in scans)
        
        most_scanned = [
            {"repository": repo, "scan_count": count}
            for repo, count in repo_counts.most_common(5)
        ]
        
        # Calculate average health (mock calculation)
        health_scores = [scan.get("health_score", 0.75) for scan in scans]
        avg_health = sum(health_scores) / len(health_scores) if health_scores else 0
        
        return RepositoryMetrics(
            total_repositories=len(repo_counts),
            most_scanned_repos=most_scanned,
            languages_analyzed=dict(lang_counts),
            avg_repository_health=round(avg_health, 2)
        )
    
    def _calculate_xai_metrics(self, findings: List[Dict]) -> XAIMetrics:
        """Calculate XAI-specific metrics."""
        xai_findings = [f for f in findings if f.get("xai_confidence")]
        
        if not xai_findings:
            return XAIMetrics()
        
        confidence_scores = [f["xai_confidence"] for f in xai_findings]
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Confidence distribution
        confidence_dist = {
            "high": sum(1 for c in confidence_scores if c >= 0.8),
            "medium": sum(1 for c in confidence_scores if 0.6 <= c < 0.8),
            "low": sum(1 for c in confidence_scores if c < 0.6)
        }
        
        # Reasoning quality (mock calculation based on reasoning length)
        reasoning_lengths = [len(f.get("xai_reasoning", "")) for f in xai_findings]
        avg_reasoning_length = sum(reasoning_lengths) / len(reasoning_lengths) if reasoning_lengths else 0
        reasoning_quality = min(1.0, avg_reasoning_length / 100)  # Normalize to 0-1
        
        return XAIMetrics(
            total_xai_analyses=len(xai_findings),
            avg_confidence_score=round(avg_confidence, 2),
            confidence_distribution=confidence_dist,
            reasoning_quality_score=round(reasoning_quality, 2)
        )
    
    def _calculate_findings_trend(self, start_date: datetime, end_date: datetime, findings: List[Dict]) -> FindingsTrend:
        """Calculate findings trends over time."""
        # Group findings by date
        daily_counts = defaultdict(int)
        daily_severity = defaultdict(lambda: defaultdict(int))
        daily_category = defaultdict(lambda: defaultdict(int))
        
        for finding in findings:
            finding_date = datetime.fromisoformat(finding["timestamp"]).date().isoformat()
            daily_counts[finding_date] += 1
            daily_severity[finding_date][finding["severity"]] += 1
            daily_category[finding_date][finding["category"]] += 1
        
        # Generate data points for all days in range
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        total_trend = []
        severity_trends = defaultdict(list)
        category_trends = defaultdict(list)
        
        while current_date <= end_date_only:
            date_str = current_date.isoformat()
            count = daily_counts.get(date_str, 0)
            
            total_trend.append(TrendDataPoint(date=date_str, value=count, count=count))
            
            # Severity trends
            for severity in ["error", "warning", "info"]:
                severity_count = daily_severity[date_str].get(severity, 0)
                severity_trends[severity].append(TrendDataPoint(date=date_str, value=severity_count, count=severity_count))
            
            # Category trends (top 3)
            for category in ["debugging", "logging", "complexity"]:
                category_count = daily_category[date_str].get(category, 0)
                category_trends[category].append(TrendDataPoint(date=date_str, value=category_count, count=category_count))
            
            current_date += timedelta(days=1)
        
        return FindingsTrend(
            total_findings=total_trend,
            severity_trends=dict(severity_trends),
            category_trends=dict(category_trends)
        )
    
    def _get_recent_scans(self, scans: List[Dict]) -> List[Dict]:
        """Get most recent scans."""
        sorted_scans = sorted(scans, key=lambda x: x["timestamp"], reverse=True)
        return [
            {
                "scan_id": scan["scan_id"],
                "repository": scan["repository"],
                "status": scan["status"],
                "timestamp": scan["timestamp"],
                "findings_count": scan.get("findings_count", 0)
            }
            for scan in sorted_scans[:5]
        ]
    
    def _get_recent_findings(self, findings: List[Dict]) -> List[Dict]:
        """Get most recent high-severity findings."""
        high_severity = [f for f in findings if f["severity"] in ["error", "warning"]]
        sorted_findings = sorted(high_severity, key=lambda x: x["timestamp"], reverse=True)
        return [
            {
                "rule_id": finding["rule_id"],
                "severity": finding["severity"],
                "message": finding["message"],
                "timestamp": finding["timestamp"],
                "scan_id": finding["scan_id"]
            }
            for finding in sorted_findings[:5]
        ]
    
    def _calculate_system_health(self) -> SystemHealth:
        """Calculate overall system health indicators."""
        if self._mock_scans is None:
            self._mock_scans = self._generate_mock_scans()
        if self._mock_findings is None:
            self._mock_findings = self._generate_mock_findings()
            
        uptime = datetime.now() - self.start_time
        uptime_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"
        
        return SystemHealth(
            status="healthy",
            timestamp=datetime.now(),
            version="1.0.0",
            uptime=uptime_str,
            metrics={
                "scan_success_rate": 0.95,
                "avg_response_time": "150ms",
                "error_rate": 0.02,
                "total_scans": len(self._mock_scans),
                "total_findings": len(self._mock_findings)
            }
        )
    
    def _generate_mock_scans(self) -> List[Dict]:
        """Generate mock scan data for development."""
        mock_scans = []
        base_time = datetime.now()
        
        repositories = [
            "https://github.com/example/webapp",
            "https://github.com/example/api",
            "https://github.com/example/mobile-app",
            "https://github.com/example/data-pipeline"
        ]
        
        for i in range(50):
            scan_time = base_time - timedelta(days=i//2, hours=i%24)
            mock_scans.append({
                "scan_id": f"scan_{i:03d}",
                "repository": repositories[i % len(repositories)],
                "scan_type": "pr" if i % 3 == 0 else "project",
                "status": "completed" if i % 10 != 9 else "failed",
                "timestamp": scan_time.isoformat(),
                "duration": 300 + (i % 5) * 120,  # 5-15 minutes
                "findings_count": max(0, 15 - (i % 8)),
                "primary_language": ["python", "javascript", "java"][i % 3],
                "health_score": 0.6 + (i % 4) * 0.1
            })
        
        return mock_scans
    
    def _generate_mock_findings(self) -> List[Dict]:
        """Generate mock findings data for development."""
        mock_findings = []
        base_time = datetime.now()
        
        rules = [
            {"rule_id": "print_statements", "category": "logging", "severity": "warning"},
            {"rule_id": "pdb_trace", "category": "debugging", "severity": "error"},
            {"rule_id": "function_too_long", "category": "complexity", "severity": "warning"},
            {"rule_id": "unused_imports", "category": "imports", "severity": "info"},
            {"rule_id": "hardcoded_strings", "category": "security", "severity": "warning"}
        ]
        
        for i in range(200):
            finding_time = base_time - timedelta(days=i//10, hours=i%24)
            rule = rules[i % len(rules)]
            
            mock_findings.append({
                "finding_id": f"finding_{i:03d}",
                "scan_id": f"scan_{i//4:03d}",
                "rule_id": rule["rule_id"],
                "category": rule["category"],
                "severity": rule["severity"],
                "message": f"Found {rule['rule_id']} issue in code",
                "timestamp": finding_time.isoformat(),
                "xai_confidence": 0.5 + (i % 5) * 0.1,
                "xai_reasoning": f"Reasoning for {rule['rule_id']} detection"
            })
        
        return mock_findings 