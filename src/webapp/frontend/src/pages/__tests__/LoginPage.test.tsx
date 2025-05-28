/**
 * Unit tests cho LoginPage component với thiết kế minimalist 2025.
 * 
 * Test coverage:
 * - Rendering và layout
 * - Form validation
 * - User interactions
 * - Accessibility
 * - Error handling
 * - Loading states
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import React from 'react';

// Mock AuthContext
const mockLogin = vi.fn();
const mockRegister = vi.fn();
const mockLogout = vi.fn();
const mockUpdateProfile = vi.fn();
const mockChangePassword = vi.fn();

const mockAuthValue = {
  login: mockLogin,
  register: mockRegister,
  logout: mockLogout,
  updateProfile: mockUpdateProfile,
  changePassword: mockChangePassword,
  isAuthenticated: false,
  user: null,
  loading: false,
  isInitialized: true,
  error: null,
};

// Mock useAuth hook
vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => mockAuthValue,
}));

// Mock react-router-dom
const mockNavigate = vi.fn();
const mockLocation = { state: null };

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => mockLocation,
  };
});

// Mock framer-motion for testing
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    form: ({ children, ...props }: any) => <form {...props}>{children}</form>,
    p: ({ children, ...props }: any) => <p {...props}>{children}</p>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

import { LoginPage } from '../LoginPage';

// Helper to render component with router
const renderLoginPage = (authOverrides = {}) => {
  // Update mock auth value
  Object.assign(mockAuthValue, authOverrides);
  
  return render(
    <BrowserRouter>
      <LoginPage />
    </BrowserRouter>
  );
};

describe('LoginPage - Minimalist Design 2025', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    
    // Reset mock auth value
    Object.assign(mockAuthValue, {
      login: mockLogin,
      register: mockRegister,
      logout: mockLogout,
      updateProfile: mockUpdateProfile,
      changePassword: mockChangePassword,
      isAuthenticated: false,
      user: null,
      loading: false,
      isInitialized: true,
      error: null,
    });
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('Rendering và Layout', () => {
    it('should render main elements correctly', () => {
      renderLoginPage();
      
      expect(screen.getByRole('heading', { name: /đăng nhập/i })).toBeInTheDocument();
      expect(screen.getByText(/chào mừng bạn quay lại với ai code reviewer/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/mật khẩu/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /đăng nhập/i })).toBeInTheDocument();
    });

    it('should have modern card layout with soft UI classes', () => {
      renderLoginPage();
      
      const cardElements = document.querySelectorAll('.card-soft, .card-soft-body');
      expect(cardElements.length).toBeGreaterThan(0);
    });

    it('should have proper form structure', () => {
      renderLoginPage();
      
      const form = screen.getByRole('form', { hidden: true });
      expect(form).toHaveAttribute('noValidate');
      
      const emailInput = screen.getByLabelText(/email/i);
      expect(emailInput).toHaveAttribute('type', 'email');
      expect(emailInput).toHaveAttribute('autoComplete', 'email');
      expect(emailInput).toHaveAttribute('required');
      
      const passwordInput = screen.getByLabelText(/mật khẩu/i);
      expect(passwordInput).toHaveAttribute('type', 'password');
      expect(passwordInput).toHaveAttribute('autoComplete', 'current-password');
      expect(passwordInput).toHaveAttribute('required');
    });

    it('should show register link in footer', () => {
      renderLoginPage();
      
      expect(screen.getByText(/chưa có tài khoản\?/i)).toBeInTheDocument();
      const registerLink = screen.getByRole('link', { name: /đăng ký ngay/i });
      expect(registerLink).toHaveAttribute('href', '/register');
    });
  });

  describe('Form Validation', () => {
    it('should validate empty email', async () => {
      const user = userEvent.setup();
      renderLoginPage();
      
      const submitButton = screen.getByRole('button', { name: /đăng nhập/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/vui lòng nhập email/i)).toBeInTheDocument();
      });
    });

    it('should validate invalid email format', async () => {
      const user = userEvent.setup();
      renderLoginPage();
      
      const emailInput = screen.getByLabelText(/email/i);
      await user.type(emailInput, 'invalid-email');
      
      const submitButton = screen.getByRole('button', { name: /đăng nhập/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/email không hợp lệ/i)).toBeInTheDocument();
      });
    });

    it('should validate empty password', async () => {
      const user = userEvent.setup();
      renderLoginPage();
      
      const emailInput = screen.getByLabelText(/email/i);
      await user.type(emailInput, 'test@example.com');
      
      const submitButton = screen.getByRole('button', { name: /đăng nhập/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/vui lòng nhập mật khẩu/i)).toBeInTheDocument();
      });
    });

    it('should validate short password', async () => {
      const user = userEvent.setup();
      renderLoginPage();
      
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/mật khẩu/i);
      
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, '123');
      
      const submitButton = screen.getByRole('button', { name: /đăng nhập/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/mật khẩu phải có ít nhất 6 ký tự/i)).toBeInTheDocument();
      });
    });

    it('should clear errors when user starts typing', async () => {
      const user = userEvent.setup();
      renderLoginPage();
      
      // Trigger validation error first
      const submitButton = screen.getByRole('button', { name: /đăng nhập/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/vui lòng nhập email/i)).toBeInTheDocument();
      });
      
      // Start typing to clear error
      const emailInput = screen.getByLabelText(/email/i);
      await user.type(emailInput, 'a');
      
      await waitFor(() => {
        expect(screen.queryByText(/vui lòng nhập email/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('User Interactions', () => {
    it('should toggle password visibility', async () => {
      const user = userEvent.setup();
      renderLoginPage();
      
      const passwordInput = screen.getByLabelText(/mật khẩu/i);
      const toggleButton = screen.getByLabelText(/hiện mật khẩu/i);
      
      expect(passwordInput).toHaveAttribute('type', 'password');
      
      await user.click(toggleButton);
      expect(passwordInput).toHaveAttribute('type', 'text');
      
      await user.click(toggleButton);
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    it('should handle remember me checkbox', async () => {
      const user = userEvent.setup();
      renderLoginPage();
      
      const rememberCheckbox = screen.getByRole('checkbox', { name: /ghi nhớ đăng nhập/i });
      expect(rememberCheckbox).not.toBeChecked();
      
      await user.click(rememberCheckbox);
      expect(rememberCheckbox).toBeChecked();
    });

    it('should submit form with valid data', async () => {
      const user = userEvent.setup();
      renderLoginPage();
      
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/mật khẩu/i);
      const submitButton = screen.getByRole('button', { name: /đăng nhập/i });
      
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith({
          username: 'test@example.com',
          password: 'password123',
        });
      });
    });

    it('should handle login failure', async () => {
      const user = userEvent.setup();
      mockLogin.mockRejectedValueOnce(new Error('Login failed'));
      renderLoginPage();
      
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/mật khẩu/i);
      const submitButton = screen.getByRole('button', { name: /đăng nhập/i });
      
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'wrongpassword');
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/email hoặc mật khẩu không đúng/i)).toBeInTheDocument();
      });
    });
  });

  describe('Loading States', () => {
    it('should show loading state during submission', async () => {
      renderLoginPage({ loading: true });
      
      const submitButton = screen.getByRole('button', { name: /đang đăng nhập\.\.\./i });
      expect(submitButton).toBeDisabled();
      expect(screen.getByText(/đang đăng nhập\.\.\./i)).toBeInTheDocument();
      
      // Check for loading spinner
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('should disable form inputs during loading', () => {
      renderLoginPage({ loading: true });
      
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/mật khẩu/i);
      const rememberCheckbox = screen.getByRole('checkbox', { name: /ghi nhớ đăng nhập/i });
      
      expect(emailInput).toBeDisabled();
      expect(passwordInput).toBeDisabled();
      expect(rememberCheckbox).toBeDisabled();
    });
  });

  describe('Remember Me Functionality', () => {
    it('should load remembered username from localStorage', () => {
      localStorage.setItem('remembered_username', 'saved@example.com');
      renderLoginPage();
      
      const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
      expect(emailInput.value).toBe('saved@example.com');
      
      const rememberCheckbox = screen.getByRole('checkbox', { name: /ghi nhớ đăng nhập/i });
      expect(rememberCheckbox).toBeChecked();
    });

    it('should save username to localStorage when remember me is checked', async () => {
      const user = userEvent.setup();
      renderLoginPage();
      
      const emailInput = screen.getByLabelText(/email/i);
      const rememberCheckbox = screen.getByRole('checkbox', { name: /ghi nhớ đăng nhập/i });
      
      await user.type(emailInput, 'new@example.com');
      await user.click(rememberCheckbox);
      
      expect(localStorage.getItem('remembered_username')).toBe('new@example.com');
    });

    it('should remove username from localStorage when remember me is unchecked', async () => {
      const user = userEvent.setup();
      localStorage.setItem('remembered_username', 'saved@example.com');
      renderLoginPage();
      
      const rememberCheckbox = screen.getByRole('checkbox', { name: /ghi nhớ đăng nhập/i });
      await user.click(rememberCheckbox); // Uncheck
      
      expect(localStorage.getItem('remembered_username')).toBeNull();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels and descriptions', () => {
      renderLoginPage();
      
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/mật khẩu/i);
      const toggleButton = screen.getByLabelText(/hiện mật khẩu/i);
      
      expect(emailInput).toHaveAttribute('aria-describedby');
      expect(passwordInput).toHaveAttribute('aria-describedby');
      expect(toggleButton).toHaveAttribute('aria-label');
    });

    it('should show error messages with proper ARIA roles', async () => {
      const user = userEvent.setup();
      renderLoginPage();
      
      const submitButton = screen.getByRole('button', { name: /đăng nhập/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        const errorMessage = screen.getByText(/vui lòng nhập email/i);
        expect(errorMessage).toHaveAttribute('role', 'alert');
        expect(errorMessage).toHaveAttribute('id', 'username-error');
      });
    });

    it('should have proper form accessibility attributes', () => {
      renderLoginPage();
      
      const form = screen.getByRole('form', { hidden: true });
      expect(form).toHaveAttribute('noValidate');
      
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/mật khẩu/i);
      
      expect(emailInput).toHaveAttribute('required');
      expect(passwordInput).toHaveAttribute('required');
    });
  });

  describe('Navigation và Redirects', () => {
    it('should redirect to dashboard when authenticated', () => {
      renderLoginPage({ isAuthenticated: true });
      
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard', { replace: true });
    });

    it('should redirect to intended location from state', () => {
      mockLocation.state = { from: { pathname: '/scans' } };
      renderLoginPage({ isAuthenticated: true });
      
      expect(mockNavigate).toHaveBeenCalledWith('/scans', { replace: true });
    });
  });
}); 