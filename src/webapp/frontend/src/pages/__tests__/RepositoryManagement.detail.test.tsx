import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, test, beforeEach, expect } from 'vitest';
import RepositoryManagement from '../RepositoryManagement';
import { AuthProvider } from '../../contexts/AuthContext';
import { SidebarProvider } from '../../contexts/SidebarContext';

// Mock modules
vi.mock('../../services/api', () => ({
  apiService: {
    getRepositoryDetail: vi.fn(),
    updateRepositoryLatest: vi.fn(),
  }
}));

// Mock react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ id: '1', action: undefined }),
    useNavigate: () => mockNavigate,
  };
});

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>
  },
  AnimatePresence: ({ children }: any) => children
}));

// Mock Layout component
vi.mock('../../components/Layout', () => {
  return {
    default: function MockLayout({ children }: { children: React.ReactNode }) {
      return <div data-testid="layout">{children}</div>;
    }
  };
});

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>
      <SidebarProvider>
        {children}
      </SidebarProvider>
    </AuthProvider>
  </BrowserRouter>
);

// Mock repository data
const mockRepositoryData = {
  id: 1,
  name: 'test-repo',
  url: 'https://github.com/user/test-repo',
  description: 'Test repository for unit tests',
  language: 'TypeScript',
  stars: 123,
  forks: 45,
  default_branch: 'main',
  is_private: false,
  owner_id: 1,
  created_at: '2025-01-15T10:00:00Z',
  updated_at: '2025-01-29T15:30:00Z',
  last_synced_at: '2025-01-29T15:30:00Z',
  cached_path: '/cache/test-repo',
  last_commit_hash: 'abc123def456',
  cache_expires_at: '2025-01-30T15:30:00Z',
  cache_size_mb: 25.5,
  auto_sync_enabled: true,
};

describe('RepositoryManagement - Repository Detail View', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('should fetch and display repository detail on load', async () => {
    const { apiService } = await import('../../services/api');
    (apiService.getRepositoryDetail as any).mockResolvedValue({
      data: mockRepositoryData
    });

    render(
      <TestWrapper>
        <RepositoryManagement />
      </TestWrapper>
    );

    // Wait for API call and data load
    await waitFor(() => {
      expect(apiService.getRepositoryDetail).toHaveBeenCalledWith('1');
    });

    // Check if repository data is displayed
    expect(screen.getByText('test-repo')).toBeInTheDocument();
    expect(screen.getByText('Test repository for unit tests')).toBeInTheDocument();
    expect(screen.getByText('TypeScript')).toBeInTheDocument();
    expect(screen.getByText('⭐ 123')).toBeInTheDocument();
    expect(screen.getByText('🍴 45')).toBeInTheDocument();
  });

  test('should display Update Latest button in view mode', async () => {
    const { apiService } = await import('../../services/api');
    (apiService.getRepositoryDetail as any).mockResolvedValue({
      data: mockRepositoryData
    });

    render(
      <TestWrapper>
        <RepositoryManagement />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Update Latest')).toBeInTheDocument();
    });

    const updateButton = screen.getByText('Update Latest');
    expect(updateButton).toBeInTheDocument();
    expect(updateButton.closest('button')).not.toBeDisabled();
  });

  test('should call updateRepositoryLatest API when Update Latest button is clicked', async () => {
    const { apiService } = await import('../../services/api');
    const user = userEvent.setup();
    
    (apiService.getRepositoryDetail as any).mockResolvedValue({
      data: mockRepositoryData
    });
    (apiService.updateRepositoryLatest as any).mockResolvedValue({
      data: { ...mockRepositoryData, updated_at: '2025-01-29T16:00:00Z' }
    });

    render(
      <TestWrapper>
        <RepositoryManagement />
      </TestWrapper>
    );

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Update Latest')).toBeInTheDocument();
    });

    // Click Update Latest button
    const updateButton = screen.getByText('Update Latest');
    await user.click(updateButton);

    // Check if loading state is shown
    expect(screen.getByText('Đang cập nhật...')).toBeInTheDocument();

    // Wait for API call completion
    await waitFor(() => {
      expect(apiService.updateRepositoryLatest).toHaveBeenCalledWith('1');
    });

    // Should refetch repository data after update
    await waitFor(() => {
      expect(apiService.getRepositoryDetail).toHaveBeenCalledTimes(2);
    });
  });

  test('should display smart cache information when available', async () => {
    const { apiService } = await import('../../services/api');
    (apiService.getRepositoryDetail as any).mockResolvedValue({
      data: mockRepositoryData
    });

    render(
      <TestWrapper>
        <RepositoryManagement />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('📁 Smart Cache Information')).toBeInTheDocument();
    });

    // Check cache details
    expect(screen.getByText('Cache Size: 25.5MB')).toBeInTheDocument();
    expect(screen.getByText('Last Commit: abc123d')).toBeInTheDocument();
  });

  test('should display repository visibility and sync status', async () => {
    const { apiService } = await import('../../services/api');
    (apiService.getRepositoryDetail as any).mockResolvedValue({
      data: mockRepositoryData
    });

    render(
      <TestWrapper>
        <RepositoryManagement />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('🌍 Public')).toBeInTheDocument();
      expect(screen.getByText('✅ Enabled')).toBeInTheDocument();
    });
  });

  test('should handle API error gracefully', async () => {
    const { apiService } = await import('../../services/api');
    (apiService.getRepositoryDetail as any).mockResolvedValue({
      error: { detail: 'Repository not found', status_code: 404 }
    });

    render(
      <TestWrapper>
        <RepositoryManagement />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Lỗi tải Repository')).toBeInTheDocument();
      expect(screen.getByText('Repository not found')).toBeInTheDocument();
    });

    // Check if retry button is available
    expect(screen.getByText('Thử lại')).toBeInTheDocument();
  });

  test('should handle update error gracefully', async () => {
    const { apiService } = await import('../../services/api');
    const user = userEvent.setup();
    
    (apiService.getRepositoryDetail as any).mockResolvedValue({
      data: mockRepositoryData
    });
    (apiService.updateRepositoryLatest as any).mockResolvedValue({
      error: { detail: 'Update failed', status_code: 500 }
    });

    render(
      <TestWrapper>
        <RepositoryManagement />
      </TestWrapper>
    );

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Update Latest')).toBeInTheDocument();
    });

    // Click Update Latest button
    const updateButton = screen.getByText('Update Latest');
    await user.click(updateButton);

    // Wait for error to appear
    await waitFor(() => {
      expect(screen.getByText('⚠️')).toBeInTheDocument();
      expect(screen.getByText('Update failed')).toBeInTheDocument();
    });
  });

  test('should display formatted timestamps in Vietnamese locale', async () => {
    const { apiService } = await import('../../services/api');
    (apiService.getRepositoryDetail as any).mockResolvedValue({
      data: mockRepositoryData
    });

    render(
      <TestWrapper>
        <RepositoryManagement />
      </TestWrapper>
    );

    await waitFor(() => {
      // Check if Vietnamese formatted dates are present
      expect(screen.getByText(/Tạo lúc/)).toBeInTheDocument();
      expect(screen.getByText(/Cập nhật lần cuối/)).toBeInTheDocument();
    });
  });
}); 