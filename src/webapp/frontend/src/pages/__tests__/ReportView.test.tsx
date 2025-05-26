/**
 * Unit tests for ReportView page component.
 * 
 * Tests report viewing functionality including tabs, findings filtering,
 * LLM insights display, and diagram rendering.
 */

import React from 'react';
import { render, screen, waitFor } from '../../test/utils';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import ReportView from '../ReportView';
import { server } from '../../test/mocks/server';
import { http, HttpResponse } from 'msw';

// Mock useParams and useNavigate
const mockNavigate = vi.fn();
const mockScanId = 'demo_scan_001';

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ scanId: mockScanId }),
    useNavigate: () => mockNavigate,
  };
});

describe('ReportView Component', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  test('renders loading state initially', () => {
    render(<ReportView />);
    
    expect(screen.getByText('Loading report...')).toBeInTheDocument();
  });

  test('renders report with mock data', async () => {
    render(<ReportView />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Scan Report: demo_scan_001')).toBeInTheDocument();
    });

    // Check basic report information
    expect(screen.getByText('user/test-repo')).toBeInTheDocument();
    expect(screen.getByText('Back to Scans')).toBeInTheDocument();
  });

  test('displays tabs correctly', async () => {
    render(<ReportView />);
    
    await waitFor(() => {
      expect(screen.getByText('Scan Report: demo_scan_001')).toBeInTheDocument();
    });

    // Check all tabs are present
    expect(screen.getByText('Overview')).toBeInTheDocument();
    expect(screen.getByText('Findings (2)')).toBeInTheDocument();
    expect(screen.getByText('LLM Insights (2)')).toBeInTheDocument();
    expect(screen.getByText('Diagrams (1)')).toBeInTheDocument();
  });

  test('overview tab displays scan summary correctly', async () => {
    render(<ReportView />);
    
    await waitFor(() => {
      expect(screen.getByText('Scan Summary')).toBeInTheDocument();
    });

    // Check summary statistics
    expect(screen.getByText('5')).toBeInTheDocument(); // Total findings
    expect(screen.getByText('1')).toBeInTheDocument(); // Critical count
    expect(screen.getByText('2')).toBeInTheDocument(); // High count

    // Check scan information
    expect(screen.getByText('Scan Information')).toBeInTheDocument();
    expect(screen.getByText('demo_scan_001')).toBeInTheDocument();
    expect(screen.getByText('pr')).toBeInTheDocument();
    expect(screen.getByText('25')).toBeInTheDocument(); // Files analyzed
    expect(screen.getByText('Python, JavaScript')).toBeInTheDocument();
  });

  test('findings tab displays static analysis findings', async () => {
    render(<ReportView />);
    
    await waitFor(() => {
      expect(screen.getByText('Scan Report: demo_scan_001')).toBeInTheDocument();
    });

    // Click on findings tab
    await user.click(screen.getByText('Findings (2)'));

    // Check findings content
    expect(screen.getByText('Hardcoded API key detected')).toBeInTheDocument();
    expect(screen.getByText('Inefficient nested loop detected')).toBeInTheDocument();
    
    // Check severity badges
    expect(screen.getByText('CRITICAL')).toBeInTheDocument();
    expect(screen.getByText('HIGH')).toBeInTheDocument();
    
    // Check categories
    expect(screen.getByText('Security')).toBeInTheDocument();
    expect(screen.getByText('Performance')).toBeInTheDocument();
  });

  test('findings filtering works correctly', async () => {
    render(<ReportView />);
    
    await waitFor(() => {
      expect(screen.getByText('Scan Report: demo_scan_001')).toBeInTheDocument();
    });

    // Click on findings tab
    await user.click(screen.getByText('Findings (2)'));

    // Check filter dropdown
    const filterSelect = screen.getByDisplayValue('All (2)');
    expect(filterSelect).toBeInTheDocument();

    // Filter by critical
    await user.selectOptions(filterSelect, 'critical');
    
    // Should only show critical findings
    expect(screen.getByText('Hardcoded API key detected')).toBeInTheDocument();
    expect(screen.queryByText('Inefficient nested loop detected')).not.toBeInTheDocument();
  });

  test('findings display code snippets', async () => {
    render(<ReportView />);
    
    await waitFor(() => {
      expect(screen.getByText('Scan Report: demo_scan_001')).toBeInTheDocument();
    });

    // Click on findings tab
    await user.click(screen.getByText('Findings (2)'));

    // Check code snippet
    expect(screen.getByText('API_KEY = "sk-1234567890abcdef"')).toBeInTheDocument();
    expect(screen.getByText('src/config.py')).toBeInTheDocument();
  });

  test('findings display suggestions', async () => {
    render(<ReportView />);
    
    await waitFor(() => {
      expect(screen.getByText('Scan Report: demo_scan_001')).toBeInTheDocument();
    });

    // Click on findings tab
    await user.click(screen.getByText('Findings (2)'));

    // Check suggestions
    expect(screen.getByText('Store sensitive data in environment variables')).toBeInTheDocument();
    expect(screen.getByText('Consider using dictionary lookup or set operations')).toBeInTheDocument();
  });

  test('LLM insights tab displays analysis correctly', async () => {
    render(<ReportView />);
    
    await waitFor(() => {
      expect(screen.getByText('Scan Report: demo_scan_001')).toBeInTheDocument();
    });

    // Click on insights tab
    await user.click(screen.getByText('LLM Insights (2)'));

    // Check insights content
    expect(screen.getByText('Security Analysis')).toBeInTheDocument();
    expect(screen.getByText('Code Quality')).toBeInTheDocument();
    
    // Check confidence scores
    expect(screen.getByText('Confidence: 85%')).toBeInTheDocument();
    expect(screen.getByText('Confidence: 78%')).toBeInTheDocument();
    
    // Check model information
    expect(screen.getAllByText('Model: gpt-4')).toHaveLength(2);
  });

  test('diagrams tab renders diagrams correctly', async () => {
    render(<ReportView />);
    
    await waitFor(() => {
      expect(screen.getByText('Scan Report: demo_scan_001')).toBeInTheDocument();
    });

    // Click on diagrams tab
    await user.click(screen.getByText('Diagrams (1)'));

    // Check diagram rendering
    expect(screen.getByText('Class Diagram - plantuml')).toBeInTheDocument();
  });

  test('handles scan not found error', async () => {
    // Override mock to use nonexistent scan ID
    vi.mocked(vi.importActual('react-router-dom')).then((actual: any) => {
      vi.doMock('react-router-dom', () => ({
        ...actual,
        useParams: () => ({ scanId: 'nonexistent' }),
        useNavigate: () => mockNavigate,
      }));
    });

    server.use(
      http.get('/scans/nonexistent/report', () => {
        return HttpResponse.json(
          { detail: 'Scan not found' },
          { status: 404 }
        );
      })
    );

    render(<ReportView />);
    
    await waitFor(() => {
      expect(screen.getByText('Error loading report:')).toBeInTheDocument();
      expect(screen.getByText('Scan not found')).toBeInTheDocument();
    });

    // Should show retry and back buttons
    expect(screen.getByText('Retry')).toBeInTheDocument();
    expect(screen.getByText('Back to Scans')).toBeInTheDocument();
  });

  test('handles server error gracefully', async () => {
    server.use(
      http.get('/scans/demo_scan_001/report', () => {
        return HttpResponse.json(
          { detail: 'Internal server error' },
          { status: 500 }
        );
      })
    );

    render(<ReportView />);
    
    await waitFor(() => {
      expect(screen.getByText('Error loading report:')).toBeInTheDocument();
      expect(screen.getByText('Internal server error')).toBeInTheDocument();
    });
  });

  test('retry button works correctly', async () => {
    // First return error, then success
    let callCount = 0;
    server.use(
      http.get('/scans/demo_scan_001/report', () => {
        callCount++;
        if (callCount === 1) {
          return HttpResponse.json(
            { detail: 'Network error' },
            { status: 500 }
          );
        }
        // Return successful response on retry
        return HttpResponse.json({
          scan_info: {
            scan_id: 'demo_scan_001',
            scan_type: 'pr',
            repository: 'test/repo',
            created_at: '2025-01-28T10:00:00Z',
          },
          summary: {
            total_findings: 0,
            critical_count: 0,
            high_count: 0,
            medium_count: 0,
            low_count: 0,
            scan_status: 'completed',
            has_llm_analysis: false,
          },
          static_analysis_findings: [],
          llm_analysis: [],
          diagrams: [],
          metadata: {
            total_files_analyzed: 5,
            languages_detected: ['Python'],
            analysis_duration_seconds: 30,
            timestamp: '2025-01-28T10:00:00Z',
          },
        });
      })
    );

    render(<ReportView />);
    
    // Wait for error state
    await waitFor(() => {
      expect(screen.getByText('Error loading report:')).toBeInTheDocument();
    });

    // Click retry
    await user.click(screen.getByText('Retry'));

    // Should show success after retry
    await waitFor(() => {
      expect(screen.getByText('Scan Report: demo_scan_001')).toBeInTheDocument();
    });
  });

  test('back to scans navigation works', async () => {
    render(<ReportView />);
    
    await waitFor(() => {
      expect(screen.getByText('Back to Scans')).toBeInTheDocument();
    });

    await user.click(screen.getByText('Back to Scans'));
    
    expect(mockNavigate).toHaveBeenCalledWith('/scans');
  });

  test('tab switching works correctly', async () => {
    render(<ReportView />);
    
    await waitFor(() => {
      expect(screen.getByText('Scan Summary')).toBeInTheDocument();
    });

    // Switch to findings tab
    await user.click(screen.getByText('Findings (2)'));
    expect(screen.getByText('Filter by severity:')).toBeInTheDocument();

    // Switch to insights tab
    await user.click(screen.getByText('LLM Insights (2)'));
    expect(screen.getByText('Security Analysis')).toBeInTheDocument();

    // Switch to diagrams tab
    await user.click(screen.getByText('Diagrams (1)'));
    expect(screen.getByText('Class Diagram - plantuml')).toBeInTheDocument();

    // Switch back to overview
    await user.click(screen.getByText('Overview'));
    expect(screen.getByText('Scan Summary')).toBeInTheDocument();
  });

  test('displays empty states correctly', async () => {
    // Override to return report with no data
    server.use(
      http.get('/scans/demo_scan_001/report', () => {
        return HttpResponse.json({
          scan_info: {
            scan_id: 'demo_scan_001',
            scan_type: 'pr',
            repository: 'test/repo',
            created_at: '2025-01-28T10:00:00Z',
          },
          summary: {
            total_findings: 0,
            critical_count: 0,
            high_count: 0,
            medium_count: 0,
            low_count: 0,
            scan_status: 'completed',
            has_llm_analysis: false,
          },
          static_analysis_findings: [],
          llm_analysis: [],
          diagrams: [],
          metadata: {
            total_files_analyzed: 5,
            languages_detected: ['Python'],
            analysis_duration_seconds: 30,
            timestamp: '2025-01-28T10:00:00Z',
          },
        });
      })
    );

    render(<ReportView />);
    
    await waitFor(() => {
      expect(screen.getByText('Scan Report: demo_scan_001')).toBeInTheDocument();
    });

    // Check findings empty state
    await user.click(screen.getByText('Findings (0)'));
    expect(screen.getByText('No findings match the selected filter.')).toBeInTheDocument();

    // Check insights empty state
    await user.click(screen.getByText('LLM Insights (0)'));
    expect(screen.getByText('No LLM insights available for this scan.')).toBeInTheDocument();

    // Check diagrams empty state
    await user.click(screen.getByText('Diagrams (0)'));
    expect(screen.getByText('No diagrams available for this scan.')).toBeInTheDocument();
  });

  test('formats dates correctly', async () => {
    render(<ReportView />);
    
    await waitFor(() => {
      expect(screen.getByText('Scan Report: demo_scan_001')).toBeInTheDocument();
    });

    // Date should be formatted as locale string
    const dateElements = screen.getAllByText(/\d{1,2}\/\d{1,2}\/\d{4}/);
    expect(dateElements.length).toBeGreaterThan(0);
  });

  test('applies correct CSS classes', () => {
    const { container } = render(<ReportView className="custom-class" />);
    
    expect(container.firstChild).toHaveClass('report-view', 'custom-class');
  });

  test('handles missing scan ID gracefully', async () => {
    // Mock empty scan ID
    vi.mocked(vi.importActual('react-router-dom')).then((actual: any) => {
      vi.doMock('react-router-dom', () => ({
        ...actual,
        useParams: () => ({ scanId: undefined }),
        useNavigate: () => mockNavigate,
      }));
    });

    render(<ReportView />);
    
    await waitFor(() => {
      expect(screen.getByText('Error loading report:')).toBeInTheDocument();
      expect(screen.getByText('Scan ID is required')).toBeInTheDocument();
    });
  });
}); 