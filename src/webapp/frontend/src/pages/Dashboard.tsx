import React, { useState, useEffect } from 'react';
import '../styles/Dashboard.css';

// Types for Dashboard API
interface DashboardSummary {
  time_range: string;
  generated_at: string;
  scan_metrics: {
    total_scans: number;
    active_scans: number;
    completed_scans: number;
    failed_scans: number;
    avg_scan_duration: number;
    scans_by_type: Record<string, number>;
    scans_by_status: Record<string, number>;
  };
  findings_metrics: {
    total_findings: number;
    avg_findings_per_scan: number;
    findings_by_severity: Record<string, number>;
    findings_by_category: Record<string, number>;
    top_rules: Array<{
      rule_id: string;
      count: number;
      percentage: number;
    }>;
  };
  repository_metrics: {
    total_repositories: number;
    most_scanned_repos: Array<{
      repository: string;
      scan_count: number;
    }>;
    languages_analyzed: Record<string, number>;
    avg_repository_health: number;
  };
  xai_metrics: {
    total_xai_analyses: number;
    avg_confidence_score: number;
    confidence_distribution: Record<string, number>;
    reasoning_quality_score: number;
  };
  findings_trend: {
    total_findings: Array<{
      date: string;
      value: number;
      count: number;
    }>;
    severity_trends: Record<string, Array<{
      date: string;
      value: number;
      count: number;
    }>>;
    category_trends: Record<string, Array<{
      date: string;
      value: number;
      count: number;
    }>>;
  };
  recent_scans: Array<{
    scan_id: string;
    repository: string;
    status: string;
    timestamp: string;
    findings_count: number;
  }>;
  recent_findings: Array<{
    rule_id: string;
    severity: string;
    message: string;
    timestamp: string;
    scan_id: string;
  }>;
  system_health: {
    status: string;
    scan_success_rate: number;
    avg_response_time: string;
    error_rate: number;
    uptime: string;
    last_updated: string;
  };
}

interface HealthCheckResponse {
  status: string;
  timestamp: string;
  version: string;
  uptime: string;
  metrics: {
    total_scans: number;
    total_findings: number;
    avg_response_time: string;
  };
}

const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardSummary | null>(null);
  const [healthData, setHealthData] = useState<HealthCheckResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('LAST_30_DAYS');
  const [refreshing, setRefreshing] = useState(false);

  const timeRangeOptions = [
    { value: 'LAST_7_DAYS', label: '7 ngày qua' },
    { value: 'LAST_30_DAYS', label: '30 ngày qua' },
    { value: 'LAST_90_DAYS', label: '90 ngày qua' },
    { value: 'LAST_YEAR', label: '1 năm qua' }
  ];

  const fetchDashboardData = async (timeRange: string) => {
    try {
      setRefreshing(true);
      
      // Fetch dashboard summary
      const summaryResponse = await fetch(
        `/api/dashboard/summary?time_range=${timeRange}&include_trends=true&include_xai=true`
      );
      
      if (!summaryResponse.ok) {
        throw new Error(`HTTP ${summaryResponse.status}: ${summaryResponse.statusText}`);
      }
      
      const summaryData = await summaryResponse.json();
      setDashboardData(summaryData);
      
      // Fetch health check
      const healthResponse = await fetch('/api/dashboard/health');
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        setHealthData(healthData);
      }
      
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err instanceof Error ? err.message : 'Không thể tải dữ liệu dashboard');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData(selectedTimeRange);
  }, [selectedTimeRange]);

  const handleTimeRangeChange = (newTimeRange: string) => {
    setSelectedTimeRange(newTimeRange);
  };

  const handleRefresh = () => {
    fetchDashboardData(selectedTimeRange);
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const formatPercentage = (num: number): string => {
    return `${(num * 100).toFixed(1)}%`;
  };

  const getSeverityIcon = (severity: string): string => {
    switch (severity.toLowerCase()) {
      case 'error': return '🔴';
      case 'warning': return '🟡';
      case 'info': return '🔵';
      default: return '⚫';
    }
  };

  const getHealthStatusColor = (status: string): string => {
    switch (status) {
      case 'healthy': return '#22c55e';
      case 'warning': return '#f59e0b';
      case 'error': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const renderMetricCard = (title: string, value: string | number, subtitle?: string, icon?: string) => (
    <div className="metric-card">
      <div className="metric-header">
        {icon && <span className="metric-icon">{icon}</span>}
        <h3>{title}</h3>
      </div>
      <div className="metric-value">{typeof value === 'number' ? formatNumber(value) : value}</div>
      {subtitle && <div className="metric-subtitle">{subtitle}</div>}
    </div>
  );

  const renderTrendChart = (data: Array<{ date: string; value: number }>, title: string) => {
    if (!data || data.length === 0) return null;
    
    const maxValue = Math.max(...data.map(d => d.value));
    const minValue = Math.min(...data.map(d => d.value));
    const range = maxValue - minValue || 1;
    
    return (
      <div className="trend-chart">
        <h4>{title}</h4>
        <div className="chart-container">
          <svg width="100%" height="200" viewBox="0 0 400 200">
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
              </linearGradient>
            </defs>
            
            {/* Grid lines */}
            {[0, 1, 2, 3, 4].map(i => (
              <line
                key={i}
                x1="0"
                y1={40 * i}
                x2="400"
                y2={40 * i}
                stroke="#e5e7eb"
                strokeWidth="1"
              />
            ))}
            
            {/* Data line */}
            <polyline
              fill="url(#gradient)"
              stroke="#3b82f6"
              strokeWidth="2"
              points={data.map((d, i) => {
                const x = (i / (data.length - 1)) * 400;
                const y = 200 - ((d.value - minValue) / range) * 160 - 20;
                return `${x},${y}`;
              }).join(' ')}
            />
            
            {/* Data points */}
            {data.map((d, i) => {
              const x = (i / (data.length - 1)) * 400;
              const y = 200 - ((d.value - minValue) / range) * 160 - 20;
              return (
                <circle
                  key={i}
                  cx={x}
                  cy={y}
                  r="4"
                  fill="#3b82f6"
                />
              );
            })}
          </svg>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Đang tải dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="error-state">
          <div className="error-content">
            <h2>❌ Lỗi tải Dashboard</h2>
            <p>{error}</p>
            <button onClick={handleRefresh} className="retry-button">
              🔄 Thử lại
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return null;
  }

  return (
    <div className="dashboard-container">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-content">
          <h1>📊 AI Code Review Analytics</h1>
          <p>Tổng quan tình trạng và xu hướng quality code</p>
        </div>
        
        <div className="header-controls">
          <select
            value={selectedTimeRange}
            onChange={(e) => handleTimeRangeChange(e.target.value)}
            className="time-range-select"
          >
            {timeRangeOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          
          <button
            onClick={handleRefresh}
            className={`refresh-button ${refreshing ? 'refreshing' : ''}`}
            disabled={refreshing}
          >
            🔄 {refreshing ? 'Đang cập nhật...' : 'Làm mới'}
          </button>
        </div>
      </div>

      {/* System Health */}
      {healthData && (
        <div className="health-section">
          <div className="health-card">
            <div className="health-status">
              <span 
                className="health-indicator"
                style={{ backgroundColor: getHealthStatusColor(healthData.status) }}
              ></span>
              <h3>System Health: {healthData.status.toUpperCase()}</h3>
            </div>
            <div className="health-metrics">
              <div>Uptime: {healthData.uptime}</div>
              <div>Version: {healthData.version}</div>
              <div>Avg Response: {healthData.metrics.avg_response_time}</div>
            </div>
          </div>
        </div>
      )}

      {/* Overview Metrics */}
      <div className="metrics-grid">
        {renderMetricCard(
          'Tổng số Scans',
          dashboardData.scan_metrics.total_scans,
          `${dashboardData.scan_metrics.completed_scans} hoàn thành`,
          '🔍'
        )}
        
        {renderMetricCard(
          'Tổng Issues',
          dashboardData.findings_metrics.total_findings,
          `${dashboardData.findings_metrics.avg_findings_per_scan} trung bình/scan`,
          '🐛'
        )}
        
        {renderMetricCard(
          'Repositories',
          dashboardData.repository_metrics.total_repositories,
          `Health: ${formatPercentage(dashboardData.repository_metrics.avg_repository_health)}`,
          '📁'
        )}
        
        {renderMetricCard(
          'XAI Confidence',
          formatPercentage(dashboardData.xai_metrics.avg_confidence_score),
          `${dashboardData.xai_metrics.total_xai_analyses} analyses`,
          '🤖'
        )}
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        <div className="chart-row">
          <div className="chart-card">
            {renderTrendChart(
              dashboardData.findings_trend.total_findings,
              'Xu hướng Issues theo thời gian'
            )}
          </div>
          
          <div className="chart-card">
            <h4>Issues theo Severity</h4>
            <div className="severity-breakdown">
              {Object.entries(dashboardData.findings_metrics.findings_by_severity).map(([severity, count]) => (
                <div key={severity} className="severity-item">
                  <span className="severity-label">
                    {getSeverityIcon(severity)} {severity}
                  </span>
                  <span className="severity-count">{count}</span>
                  <div className="severity-bar">
                    <div
                      className={`severity-fill severity-${severity.toLowerCase()}`}
                      style={{
                        width: `${(count / dashboardData.findings_metrics.total_findings) * 100}%`
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="chart-row">
          <div className="chart-card">
            <h4>Top Rules</h4>
            <div className="top-rules-list">
              {dashboardData.findings_metrics.top_rules.map((rule, index) => (
                <div key={rule.rule_id} className="rule-item">
                  <div className="rule-info">
                    <span className="rule-rank">#{index + 1}</span>
                    <span className="rule-id">{rule.rule_id}</span>
                  </div>
                  <div className="rule-stats">
                    <span className="rule-count">{rule.count}</span>
                    <span className="rule-percentage">({rule.percentage}%)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="chart-card">
            <h4>XAI Confidence Distribution</h4>
            <div className="confidence-distribution">
              {Object.entries(dashboardData.xai_metrics.confidence_distribution).map(([level, count]) => {
                const percentage = (count / dashboardData.xai_metrics.total_xai_analyses) * 100;
                return (
                  <div key={level} className="confidence-item">
                    <span className="confidence-label">
                      {level === 'high' ? '🟢 Cao' : level === 'medium' ? '🟡 Trung bình' : '🔴 Thấp'}
                    </span>
                    <span className="confidence-count">{count}</span>
                    <div className="confidence-bar">
                      <div
                        className={`confidence-fill confidence-${level}`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="activity-section">
        <div className="activity-row">
          <div className="activity-card">
            <h4>🔍 Recent Scans</h4>
            <div className="activity-list">
              {dashboardData.recent_scans.map(scan => (
                <div key={scan.scan_id} className="activity-item">
                  <div className="activity-info">
                    <span className="activity-title">{scan.repository.split('/').pop()}</span>
                    <span className="activity-time">
                      {new Date(scan.timestamp).toLocaleString('vi-VN')}
                    </span>
                  </div>
                  <div className="activity-meta">
                    <span className={`status-badge status-${scan.status}`}>
                      {scan.status}
                    </span>
                    <span className="findings-badge">
                      {scan.findings_count} issues
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="activity-card">
            <h4>🐛 Recent High-Priority Issues</h4>
            <div className="activity-list">
              {dashboardData.recent_findings.map((finding, index) => (
                <div key={index} className="activity-item">
                  <div className="activity-info">
                    <span className="activity-title">
                      {getSeverityIcon(finding.severity)} {finding.rule_id}
                    </span>
                    <span className="activity-description">{finding.message}</span>
                    <span className="activity-time">
                      {new Date(finding.timestamp).toLocaleString('vi-VN')}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="dashboard-footer">
        <p>
          Cập nhật lần cuối: {new Date(dashboardData.generated_at).toLocaleString('vi-VN')} | 
          Dữ liệu từ {timeRangeOptions.find(opt => opt.value === selectedTimeRange)?.label}
        </p>
      </div>
    </div>
  );
};

export default Dashboard; 