import React from 'react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Dashboard from '../Dashboard';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock dashboard data
const mockDashboardData = {
  time_range: 'LAST_30_DAYS',
  generated_at: '2025-01-30T10:00:00Z',
  scan_metrics: {
    total_scans: 50,
    active_scans: 2,
    completed_scans: 45,
    failed_scans: 3,
    avg_scan_duration: 8.5,
    scans_by_type: { pr: 20, project: 30 },
    scans_by_status: { completed: 45, failed: 3, running: 2 }
  },
  findings_metrics: {
    total_findings: 200,
    avg_findings_per_scan: 4.0,
    findings_by_severity: { error: 25, warning: 100, info: 75 },
    findings_by_category: { debugging: 50, logging: 75, complexity: 75 },
    top_rules: [
      { rule_id: 'print_statements', count: 75, percentage: 37.5 },
      { rule_id: 'pdb_trace', count: 25, percentage: 12.5 },
      { rule_id: 'function_too_long', count: 50, percentage: 25.0 }
    ]
  },
  repository_metrics: {
    total_repositories: 4,
    most_scanned_repos: [
      { repository: 'https://github.com/example/webapp', scan_count: 15 },
      { repository: 'https://github.com/example/api', scan_count: 12 }
    ],
    languages_analyzed: { python: 30, javascript: 15, java: 5 },
    avg_repository_health: 0.75
  },
  xai_metrics: {
    total_xai_analyses: 180,
    avg_confidence_score: 0.82,
    confidence_distribution: { high: 120, medium: 45, low: 15 },
    reasoning_quality_score: 0.88
  },
  findings_trend: {
    total_findings: [
      { date: '2025-01-29', value: 10, count: 10 },
      { date: '2025-01-30', value: 15, count: 15 }
    ],
    severity_trends: {
      error: [
        { date: '2025-01-29', value: 2, count: 2 },
        { date: '2025-01-30', value: 3, count: 3 }
      ]
    },
    category_trends: {
      debugging: [
        { date: '2025-01-29', value: 5, count: 5 },
        { date: '2025-01-30', value: 7, count: 7 }
      ]
    }
  },
  recent_scans: [
    {
      scan_id: 'scan_001',
      repository: 'https://github.com/example/webapp',
      status: 'completed',
      timestamp: '2025-01-30T09:00:00Z',
      findings_count: 5
    }
  ],
  recent_findings: [
    {
      rule_id: 'print_statements',
      severity: 'warning',
      message: 'Found print statement that should use logging',
      timestamp: '2025-01-30T09:30:00Z',
      scan_id: 'scan_001'
    }
  ],
  system_health: {
    status: 'healthy',
    scan_success_rate: 0.95,
    avg_response_time: '150ms',
    error_rate: 0.02,
    uptime: '99.9%',
    last_updated: '2025-01-30T10:00:00Z'
  }
};

const mockHealthData = {
  status: 'healthy',
  timestamp: '2025-01-30T10:00:00Z',
  version: '1.0.0',
  uptime: '2d 5h 30m',
  metrics: {
    total_scans: 50,
    total_findings: 200,
    avg_response_time: '150ms'
  }
};

describe('Dashboard Component', () => {
  beforeEach(() => {
    // Reset mocks before each test
    mockFetch.mockReset();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Loading State', () => {
    it('shows loading spinner initially', () => {
      // Mock fetch to return pending promise
      mockFetch.mockReturnValue(new Promise(() => {}));

      render(<Dashboard />);

      expect(screen.getByText('Đang tải dashboard...')).toBeInTheDocument();
      expect(screen.getByRole('progressbar', { hidden: true })).toBeInTheDocument();
    });
  });

  describe('Successful Data Loading', () => {
    beforeEach(() => {
      // Mock successful API responses
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockDashboardData
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockHealthData
        });
    });

    it('renders dashboard header with correct title', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('📊 AI Code Review Analytics')).toBeInTheDocument();
        expect(screen.getByText('Tổng quan tình trạng và xu hướng quality code')).toBeInTheDocument();
      });
    });

    it('displays time range selector with correct options', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        const selector = screen.getByDisplayValue('30 ngày qua');
        expect(selector).toBeInTheDocument();
        
        // Check all options are present
        expect(screen.getByText('7 ngày qua')).toBeInTheDocument();
        expect(screen.getByText('30 ngày qua')).toBeInTheDocument();
        expect(screen.getByText('90 ngày qua')).toBeInTheDocument();
        expect(screen.getByText('1 năm qua')).toBeInTheDocument();
      });
    });

    it('shows refresh button', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('Làm mới')).toBeInTheDocument();
      });
    });

    it('displays system health information', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('System Health: HEALTHY')).toBeInTheDocument();
        expect(screen.getByText('Uptime: 2d 5h 30m')).toBeInTheDocument();
        expect(screen.getByText('Version: 1.0.0')).toBeInTheDocument();
      });
    });

    it('displays all metric cards with correct values', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        // Check metric cards
        expect(screen.getByText('Tổng số Scans')).toBeInTheDocument();
        expect(screen.getByText('50')).toBeInTheDocument();
        expect(screen.getByText('45 hoàn thành')).toBeInTheDocument();

        expect(screen.getByText('Tổng Issues')).toBeInTheDocument();
        expect(screen.getByText('200')).toBeInTheDocument();
        expect(screen.getByText('4 trung bình/scan')).toBeInTheDocument();

        expect(screen.getByText('Repositories')).toBeInTheDocument();
        expect(screen.getByText('4')).toBeInTheDocument();
        expect(screen.getByText('Health: 75.0%')).toBeInTheDocument();

        expect(screen.getByText('XAI Confidence')).toBeInTheDocument();
        expect(screen.getByText('82.0%')).toBeInTheDocument();
        expect(screen.getByText('180 analyses')).toBeInTheDocument();
      });
    });

    it('displays severity breakdown chart', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('Issues theo Severity')).toBeInTheDocument();
        expect(screen.getByText('🔴 error')).toBeInTheDocument();
        expect(screen.getByText('🟡 warning')).toBeInTheDocument();
        expect(screen.getByText('🔵 info')).toBeInTheDocument();
        expect(screen.getByText('25')).toBeInTheDocument(); // error count
        expect(screen.getByText('100')).toBeInTheDocument(); // warning count
        expect(screen.getByText('75')).toBeInTheDocument(); // info count
      });
    });

    it('displays top rules list', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('Top Rules')).toBeInTheDocument();
        expect(screen.getByText('#1')).toBeInTheDocument();
        expect(screen.getByText('print_statements')).toBeInTheDocument();
        expect(screen.getByText('(37.5%)')).toBeInTheDocument();
      });
    });

    it('displays XAI confidence distribution', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('XAI Confidence Distribution')).toBeInTheDocument();
        expect(screen.getByText('🟢 Cao')).toBeInTheDocument();
        expect(screen.getByText('🟡 Trung bình')).toBeInTheDocument();
        expect(screen.getByText('🔴 Thấp')).toBeInTheDocument();
        expect(screen.getByText('120')).toBeInTheDocument(); // high confidence count
      });
    });

    it('displays recent scans activity', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('🔍 Recent Scans')).toBeInTheDocument();
        expect(screen.getByText('webapp')).toBeInTheDocument(); // repository name
        expect(screen.getByText('5 issues')).toBeInTheDocument();
      });
    });

    it('displays recent findings activity', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('🐛 Recent High-Priority Issues')).toBeInTheDocument();
        expect(screen.getByText('🟡 print_statements')).toBeInTheDocument();
        expect(screen.getByText('Found print statement that should use logging')).toBeInTheDocument();
      });
    });

    it('displays trend chart', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('Xu hướng Issues theo thời gian')).toBeInTheDocument();
        // SVG should be rendered for the trend chart
        expect(document.querySelector('svg')).toBeInTheDocument();
      });
    });

    it('displays footer with last updated information', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Cập nhật lần cuối:/)).toBeInTheDocument();
        expect(screen.getByText(/30 ngày qua/)).toBeInTheDocument();
      });
    });
  });

  describe('User Interactions', () => {
    beforeEach(() => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockDashboardData
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockHealthData
        });
    });

    it('allows changing time range', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        const selector = screen.getByDisplayValue('30 ngày qua');
        fireEvent.change(selector, { target: { value: 'LAST_7_DAYS' } });
      });

      // Should trigger new API call
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('time_range=LAST_7_DAYS')
        );
      });
    });

    it('allows refreshing data', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        const refreshButton = screen.getByText('Làm mới');
        fireEvent.click(refreshButton);
      });

      // Should trigger new API calls
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledTimes(4); // Initial 2 + refresh 2
      });
    });

    it('shows refreshing state when refresh button is clicked', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        const refreshButton = screen.getByText('Làm mới');
        fireEvent.click(refreshButton);
        expect(screen.getByText('Đang cập nhật...')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error message when API fails', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('❌ Lỗi tải Dashboard')).toBeInTheDocument();
        expect(screen.getByText('Network error')).toBeInTheDocument();
        expect(screen.getByText('🔄 Thử lại')).toBeInTheDocument();
      });
    });

    it('displays error message when API returns non-ok status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });

      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('❌ Lỗi tải Dashboard')).toBeInTheDocument();
        expect(screen.getByText('HTTP 500: Internal Server Error')).toBeInTheDocument();
      });
    });

    it('allows retry after error', async () => {
      // First call fails
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('🔄 Thử lại')).toBeInTheDocument();
      });

      // Second call succeeds
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockDashboardData
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockHealthData
        });

      const retryButton = screen.getByText('🔄 Thử lại');
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getByText('📊 AI Code Review Analytics')).toBeInTheDocument();
      });
    });

    it('handles missing health data gracefully', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockDashboardData
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 503
        });

      render(<Dashboard />);

      await waitFor(() => {
        // Should still render dashboard data even without health data
        expect(screen.getByText('📊 AI Code Review Analytics')).toBeInTheDocument();
        expect(screen.queryByText('System Health:')).not.toBeInTheDocument();
      });
    });
  });

  describe('Utility Functions', () => {
    beforeEach(() => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockDashboardData
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockHealthData
        });
    });

    it('formats large numbers correctly', async () => {
      const largeNumberData = {
        ...mockDashboardData,
        findings_metrics: {
          ...mockDashboardData.findings_metrics,
          total_findings: 1500
        }
      };

      mockFetch.mockReset();
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => largeNumberData
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockHealthData
        });

      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('1.5K')).toBeInTheDocument();
      });
    });

    it('formats percentages correctly', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('75.0%')).toBeInTheDocument(); // Repository health
        expect(screen.getByText('82.0%')).toBeInTheDocument(); // XAI confidence
      });
    });

    it('displays severity icons correctly', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('🔴 error')).toBeInTheDocument();
        expect(screen.getByText('🟡 warning')).toBeInTheDocument();
        expect(screen.getByText('🔵 info')).toBeInTheDocument();
      });
    });
  });

  describe('Responsive Behavior', () => {
    beforeEach(() => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockDashboardData
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockHealthData
        });
    });

    it('renders without breaking on different screen sizes', async () => {
      // Mock window.matchMedia for responsive testing
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockImplementation(query => ({
          matches: false,
          media: query,
          onchange: null,
          addListener: vi.fn(),
          removeListener: vi.fn(),
          addEventListener: vi.fn(),
          removeEventListener: vi.fn(),
          dispatchEvent: vi.fn(),
        })),
      });

      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('📊 AI Code Review Analytics')).toBeInTheDocument();
      });
    });
  });
}); 