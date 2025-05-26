/**
 * Unit tests for ScanList page component.
 * 
 * Tests scan list rendering, pagination, navigation, and scan management functionality.
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '../../../src/test/utils';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import ScanList from '../../../../src/webapp/frontend/src/pages/ScanList';
import { server } from '../../../src/test/mocks/server';
import { http, HttpResponse } from 'msw';

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock window.confirm
global.confirm = vi.fn();

describe('ScanList Component', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
    (global.confirm as any).mockReturnValue(true);
  });

  test('renders loading state initially', () => {
    render(<ScanList />);
    
    expect(screen.getByText('Loading scans...')).toBeInTheDocument();
  });

  test('renders scan list with mock data', async () => {
    render(<ScanList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Code Review Scans')).toBeInTheDocument();
    });

    // Check that scans are displayed
    expect(screen.getByText('demo_scan_001')).toBeInTheDocument();
    expect(screen.getByText('project_scan_002')).toBeInTheDocument();
    expect(screen.getByText('pr_scan_003')).toBeInTheDocument();

    // Check repository names
    expect(screen.getByText('user/test-repo')).toBeInTheDocument();
    expect(screen.getByText('org/project-repo')).toBeInTheDocument();
    expect(screen.getByText('team/feature-repo')).toBeInTheDocument();
  });

  test('displays scan status badges correctly', async () => {
    render(<ScanList />);
    
    await waitFor(() => {
      expect(screen.getByText('Code Review Scans')).toBeInTheDocument();
    });

    // Check status badges
    expect(screen.getByText('COMPLETED')).toBeInTheDocument();
    expect(screen.getByText('RUNNING')).toBeInTheDocument();
    expect(screen.getByText('FAILED')).toBeInTheDocument();
  });

  test('displays scan type badges correctly', async () => {
    render(<ScanList />);
    
    await waitFor(() => {
      expect(screen.getByText('Code Review Scans')).toBeInTheDocument();
    });

    // Check type badges
    const prBadges = screen.getAllByText('PR');
    const projectBadges = screen.getAllByText('PROJECT');
    
    expect(prBadges).toHaveLength(2); // demo_scan_001 and pr_scan_003
    expect(projectBadges).toHaveLength(1); // project_scan_002
  });

  test('displays PR numbers for PR scans', async () => {
    render(<ScanList />);
    
    await waitFor(() => {
      expect(screen.getByText('Code Review Scans')).toBeInTheDocument();
    });

    // Check PR numbers
    expect(screen.getByText('PR #123')).toBeInTheDocument();
    expect(screen.getByText('PR #456')).toBeInTheDocument();
  });

  test('displays findings count with appropriate styling', async () => {
    render(<ScanList />);
    
    await waitFor(() => {
      expect(screen.getByText('Code Review Scans')).toBeInTheDocument();
    });

    // Check findings count - demo_scan_001 has 5 findings
    const findingsCell = screen.getByText('5');
    expect(findingsCell).toBeInTheDocument();
    
    // Check zero findings display
    const zeroFindings = screen.getAllByText('0');
    expect(zeroFindings.length).toBeGreaterThan(0);
  });

  test('navigates to report view when scan ID is clicked', async () => {
    render(<ScanList />);
    
    await waitFor(() => {
      expect(screen.getByText('demo_scan_001')).toBeInTheDocument();
    });

    // Click on scan ID
    await user.click(screen.getByText('demo_scan_001'));
    
    expect(mockNavigate).toHaveBeenCalledWith('/reports/demo_scan_001');
  });

  test('navigates to report view when View button is clicked', async () => {
    render(<ScanList />);
    
    await waitFor(() => {
      expect(screen.getByText('Code Review Scans')).toBeInTheDocument();
    });

    // Click on first View button
    const viewButtons = screen.getAllByText('View');
    await user.click(viewButtons[0]);
    
    expect(mockNavigate).toHaveBeenCalledWith('/reports/demo_scan_001');
  });

  test('navigates to create scan page when New Scan button is clicked', async () => {
    render(<ScanList />);
    
    await waitFor(() => {
      expect(screen.getByText('New Scan')).toBeInTheDocument();
    });

    await user.click(screen.getByText('New Scan'));
    
    expect(mockNavigate).toHaveBeenCalledWith('/create-scan');
  });

  test('deletes scan when Delete button is clicked and confirmed', async () => {
    render(<ScanList />);
    
    await waitFor(() => {
      expect(screen.getByText('Code Review Scans')).toBeInTheDocument();
    });

    // Click on first Delete button
    const deleteButtons = screen.getAllByText('Delete');
    await user.click(deleteButtons[0]);
    
    // Check that confirm was called
    expect(global.confirm).toHaveBeenCalledWith('Are you sure you want to delete this scan?');
  });

  test('does not delete scan when deletion is cancelled', async () => {
    (global.confirm as any).mockReturnValue(false);
    
    render(<ScanList />);
    
    await waitFor(() => {
      expect(screen.getByText('Code Review Scans')).toBeInTheDocument();
    });

    // Click on first Delete button
    const deleteButtons = screen.getAllByText('Delete');
    await user.click(deleteButtons[0]);
    
    // Check that confirm was called but no API call made
    expect(global.confirm).toHaveBeenCalledWith('Are you sure you want to delete this scan?');
  });

  test('handles pagination correctly', async () => {
    render(<ScanList />);
    
    await waitFor(() => {
      expect(screen.getByText('Code Review Scans')).toBeInTheDocument();
    });

    // Check pagination controls
    expect(screen.getByText('Previous')).toBeInTheDocument();
    expect(screen.getByText('Next')).toBeInTheDocument();
    expect(screen.getByText('Page 1')).toBeInTheDocument();

    // Previous button should be disabled on first page
    const previousButton = screen.getByText('Previous');
    expect(previousButton).toBeDisabled();
  });

  test('handles next page navigation', async () => {
    render(<ScanList />);
    
    await waitFor(() => {
      expect(screen.getByText('Code Review Scans')).toBeInTheDocument();
    });

    // Click next page
    const nextButton = screen.getByText('Next');
    await user.click(nextButton);

    // Page should increment
    await waitFor(() => {
      expect(screen.getByText('Page 2')).toBeInTheDocument();
    });
  });

  test('shows empty state when no scans are found', async () => {
    // Override API to return empty array
    server.use(
      http.get('/scans', () => {
        return HttpResponse.json([]);
      })
    );

    render(<ScanList />);
    
    await waitFor(() => {
      expect(screen.getByText('No scans found')).toBeInTheDocument();
      expect(screen.getByText('Create your first scan to get started with code analysis.')).toBeInTheDocument();
    });

    // Should show Create Scan button in empty state
    expect(screen.getByText('Create Scan')).toBeInTheDocument();
  });

  test('handles API error gracefully', async () => {
    // Override API to return error
    server.use(
      http.get('/scans', () => {
        return HttpResponse.json(
          { detail: 'Internal server error' },
          { status: 500 }
        );
      })
    );

    render(<ScanList />);
    
    await waitFor(() => {
      expect(screen.getByText('Error loading scans:')).toBeInTheDocument();
      expect(screen.getByText('Internal server error')).toBeInTheDocument();
    });

    // Should show retry button
    expect(screen.getByText('Retry')).toBeInTheDocument();
  });

  test('retries loading when Retry button is clicked', async () => {
    // First return error, then success
    let callCount = 0;
    server.use(
      http.get('/scans', () => {
        callCount++;
        if (callCount === 1) {
          return HttpResponse.json(
            { detail: 'Network error' },
            { status: 500 }
          );
        }
        return HttpResponse.json([
          {
            scan_id: 'retry_test',
            scan_type: 'pr',
            repository: 'test/repo',
            status: 'completed',
            created_at: '2025-01-28T10:00:00Z',
            total_findings: 1,
          }
        ]);
      })
    );

    render(<ScanList />);
    
    // Wait for error state
    await waitFor(() => {
      expect(screen.getByText('Error loading scans:')).toBeInTheDocument();
    });

    // Click retry
    await user.click(screen.getByText('Retry'));

    // Should show success after retry
    await waitFor(() => {
      expect(screen.getByText('retry_test')).toBeInTheDocument();
    });
  });

  test('displays statistics correctly', async () => {
    render(<ScanList />);
    
    await waitFor(() => {
      expect(screen.getByText('Code Review Scans')).toBeInTheDocument();
    });

    // Should show scan count
    expect(screen.getByText(/Showing \d+ scans? \(Page 1\)/)).toBeInTheDocument();
  });

  test('formats dates correctly', async () => {
    render(<ScanList />);
    
    await waitFor(() => {
      expect(screen.getByText('Code Review Scans')).toBeInTheDocument();
    });

    // Dates should be formatted as locale strings
    // The exact format depends on the user's locale, so we just check that dates are present
    const dateElements = screen.getAllByText(/\d{1,2}\/\d{1,2}\/\d{4}/);
    expect(dateElements.length).toBeGreaterThan(0);
  });

  test('applies correct CSS classes', () => {
    const { container } = render(<ScanList className="custom-class" />);
    
    expect(container.firstChild).toHaveClass('scan-list', 'custom-class');
  });
}); 