/**
 * Unit tests cho ProtectedRoute component.
 * 
 * Test suite bao gồm authentication checks, loading states, và protected routing logic.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ProtectedRoute, withAuth } from '../ProtectedRoute';
import { AuthProvider } from '../../../contexts/AuthContext';
import { mockAuthContext, resetAllAuthMocks } from '../../../test/mocks/authMocks';

// Mock the AuthContext
const mockUseAuth = vi.fn(() => mockAuthContext);
vi.mock('../../../contexts/AuthContext', async () => {
  const actual = await vi.importActual('../../../contexts/AuthContext');
  return {
    ...actual,
    useAuth: () => mockUseAuth(),
  };
});

// Mock AuthModal
vi.mock('../AuthModal', () => ({
  AuthModal: ({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) => (
    isOpen ? (
      <div data-testid="auth-modal">
        <h2>Auth Modal</h2>
        <button onClick={onClose}>Close Modal</button>
      </div>
    ) : null
  ),
}));

// Mock window.location
const mockLocationHref = vi.fn();
Object.defineProperty(window, 'location', {
  value: { href: mockLocationHref },
  writable: true,
});

describe('ProtectedRoute', () => {
  beforeEach(() => {
    resetAllAuthMocks();
    mockLocationHref.mockClear();
    mockUseAuth.mockReturnValue(mockAuthContext);
  });

  describe('Authentication States', () => {
    it('should render children when user is authenticated', () => {
      const authenticatedContext = { ...mockAuthContext, isAuthenticated: true, loading: false };
      mockUseAuth.mockReturnValue(authenticatedContext);

      render(
        <ProtectedRoute>
          <div data-testid="protected-content">Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByTestId('protected-content')).toBeInTheDocument();
      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });

    it('should show loading spinner when authentication is being checked', () => {
      const loadingContext = { ...mockAuthContext, isAuthenticated: false, loading: true };
      mockUseAuth.mockReturnValue(loadingContext);

      render(
        <ProtectedRoute>
          <div data-testid="protected-content">Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText('Đang kiểm tra đăng nhập...')).toBeInTheDocument();
      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    });

    it('should show authentication required message when user is not authenticated', () => {
      const unauthenticatedContext = { ...mockAuthContext, isAuthenticated: false, loading: false };
      mockUseAuth.mockReturnValue(unauthenticatedContext);

      render(
        <ProtectedRoute>
          <div data-testid="protected-content">Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText('Cần đăng nhập')).toBeInTheDocument();
      expect(screen.getByText('Bạn cần đăng nhập để truy cập trang này')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /đăng nhập ngay/i })).toBeInTheDocument();
      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    });
  });

  describe('Fallback Content', () => {
    it('should render custom fallback when provided and user is not authenticated', () => {
      const unauthenticatedContext = { ...mockAuthContext, isAuthenticated: false, loading: false };
      mockUseAuth.mockReturnValue(unauthenticatedContext);

      const customFallback = <div data-testid="custom-fallback">Custom Fallback</div>;

      render(
        <ProtectedRoute fallback={customFallback}>
          <div data-testid="protected-content">Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByTestId('custom-fallback')).toBeInTheDocument();
      expect(screen.getByText('Custom Fallback')).toBeInTheDocument();
      expect(screen.queryByText('Cần đăng nhập')).not.toBeInTheDocument();
      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    });
  });

  describe('Authentication Modal', () => {
    it('should show auth modal when login button is clicked', async () => {
      const unauthenticatedContext = { ...mockAuthContext, isAuthenticated: false, loading: false };
      mockUseAuth.mockReturnValue(unauthenticatedContext);

      const user = userEvent.setup();

      render(
        <ProtectedRoute>
          <div data-testid="protected-content">Protected Content</div>
        </ProtectedRoute>
      );

      const loginButton = screen.getByRole('button', { name: /đăng nhập ngay/i });
      await user.click(loginButton);

      expect(screen.getByTestId('auth-modal')).toBeInTheDocument();
      expect(screen.getByText('Auth Modal')).toBeInTheDocument();
    });

    it('should close auth modal when close button is clicked', async () => {
      const unauthenticatedContext = { ...mockAuthContext, isAuthenticated: false, loading: false };
      mockUseAuth.mockReturnValue(unauthenticatedContext);

      const user = userEvent.setup();

      render(
        <ProtectedRoute>
          <div data-testid="protected-content">Protected Content</div>
        </ProtectedRoute>
      );

      // Open modal
      const loginButton = screen.getByRole('button', { name: /đăng nhập ngay/i });
      await user.click(loginButton);
      expect(screen.getByTestId('auth-modal')).toBeInTheDocument();

      // Close modal
      const closeButton = screen.getByText('Close Modal');
      await user.click(closeButton);
      
      await waitFor(() => {
        expect(screen.queryByTestId('auth-modal')).not.toBeInTheDocument();
      });
    });

    it('should not show modal when showModal is false', () => {
      const unauthenticatedContext = { ...mockAuthContext, isAuthenticated: false, loading: false };
      mockUseAuth.mockReturnValue(unauthenticatedContext);

      render(
        <ProtectedRoute showModal={false}>
          <div data-testid="protected-content">Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.queryByText('Cần đăng nhập')).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /đăng nhập ngay/i })).not.toBeInTheDocument();
    });
  });

  describe('Redirection', () => {
    it('should redirect to custom path when showModal is false and redirectPath is provided', () => {
      const unauthenticatedContext = { ...mockAuthContext, isAuthenticated: false, loading: false };
      mockUseAuth.mockReturnValue(unauthenticatedContext);

      render(
        <ProtectedRoute showModal={false} redirectPath="/custom-login">
          <div data-testid="protected-content">Protected Content</div>
        </ProtectedRoute>
      );

      expect(mockLocationHref).toHaveBeenCalledWith('/custom-login');
    });

    it('should redirect to default login path when showModal is false and no redirectPath is provided', () => {
      const unauthenticatedContext = { ...mockAuthContext, isAuthenticated: false, loading: false };
      mockUseAuth.mockReturnValue(unauthenticatedContext);

      render(
        <ProtectedRoute showModal={false}>
          <div data-testid="protected-content">Protected Content</div>
        </ProtectedRoute>
      );

      expect(mockLocationHref).toHaveBeenCalledWith('/login');
    });
  });

  describe('Loading State UI', () => {
    it('should show loading spinner with proper styling during authentication check', () => {
      const loadingContext = { ...mockAuthContext, isAuthenticated: false, loading: true };
      mockUseAuth.mockReturnValue(loadingContext);

      render(
        <ProtectedRoute>
          <div data-testid="protected-content">Protected Content</div>
        </ProtectedRoute>
      );

      const loadingContainer = screen.getByText('Đang kiểm tra đăng nhập...').closest('div');
      expect(loadingContainer).toHaveClass('min-h-screen');
      expect(loadingContainer).toHaveClass('flex');
      expect(loadingContainer).toHaveClass('items-center');
      expect(loadingContainer).toHaveClass('justify-center');
    });
  });

  describe('Unauthorized UI', () => {
    it('should show lock icon and proper styling when user is not authenticated', () => {
      const unauthenticatedContext = { ...mockAuthContext, isAuthenticated: false, loading: false };
      mockUseAuth.mockReturnValue(unauthenticatedContext);

      render(
        <ProtectedRoute>
          <div data-testid="protected-content">Protected Content</div>
        </ProtectedRoute>
      );

      // Check for lock icon (FontAwesome)
      const lockIcon = document.querySelector('.fa-lock');
      expect(lockIcon).toBeInTheDocument();

      // Check for proper container styling
      const container = screen.getByText('Cần đăng nhập').closest('div');
      expect(container).toHaveClass('bg-white');
      expect(container).toHaveClass('rounded-3xl');
      expect(container).toHaveClass('shadow-soft-xl');
    });
  });
});

describe('withAuth HOC', () => {
  beforeEach(() => {
    resetAllAuthMocks();
    mockUseAuth.mockReturnValue(mockAuthContext);
  });

  it('should wrap component with ProtectedRoute', () => {
    const TestComponent = () => <div data-testid="test-component">Test Component</div>;
    const WrappedComponent = withAuth(TestComponent);

    const authenticatedContext = { ...mockAuthContext, isAuthenticated: true, loading: false };
    mockUseAuth.mockReturnValue(authenticatedContext);

    render(<WrappedComponent />);

    expect(screen.getByTestId('test-component')).toBeInTheDocument();
    expect(screen.getByText('Test Component')).toBeInTheDocument();
  });

  it('should pass through props to wrapped component', () => {
    interface TestProps {
      testProp: string;
    }

    const TestComponent = ({ testProp }: TestProps) => (
      <div data-testid="test-component">Test Component: {testProp}</div>
    );
    const WrappedComponent = withAuth(TestComponent);

    const authenticatedContext = { ...mockAuthContext, isAuthenticated: true, loading: false };
    mockUseAuth.mockReturnValue(authenticatedContext);

    render(<WrappedComponent testProp="test value" />);

    expect(screen.getByText('Test Component: test value')).toBeInTheDocument();
  });

  it('should use custom ProtectedRoute options', () => {
    const TestComponent = () => <div data-testid="test-component">Test Component</div>;
    const customFallback = <div data-testid="custom-fallback">Custom Fallback</div>;
    const WrappedComponent = withAuth(TestComponent, { fallback: customFallback });

    const unauthenticatedContext = { ...mockAuthContext, isAuthenticated: false, loading: false };
    mockUseAuth.mockReturnValue(unauthenticatedContext);

    render(<WrappedComponent />);

    expect(screen.getByTestId('custom-fallback')).toBeInTheDocument();
    expect(screen.queryByTestId('test-component')).not.toBeInTheDocument();
    expect(screen.queryByText('Cần đăng nhập')).not.toBeInTheDocument();
  });

  it('should show loading state when authentication is being checked', () => {
    const TestComponent = () => <div data-testid="test-component">Test Component</div>;
    const WrappedComponent = withAuth(TestComponent);

    const loadingContext = { ...mockAuthContext, isAuthenticated: false, loading: true };
    mockUseAuth.mockReturnValue(loadingContext);

    render(<WrappedComponent />);

    expect(screen.getByText('Đang kiểm tra đăng nhập...')).toBeInTheDocument();
    expect(screen.queryByTestId('test-component')).not.toBeInTheDocument();
  });
}); 