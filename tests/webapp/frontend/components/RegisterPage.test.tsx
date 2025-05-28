/**
 * Unit tests for RegisterPage component
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { RegisterPage } from '../../../../src/webapp/frontend/src/pages/RegisterPage';
import { AuthContext } from '../../../../src/webapp/frontend/src/contexts/AuthContext';
import { AuthContextValue } from '../../../../src/webapp/frontend/src/types';

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock AuthContext values
const createMockAuthContext = (overrides: Partial<AuthContextValue> = {}): AuthContextValue => ({
  user: null,
  loading: false,
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
  refreshToken: vi.fn(),
  updateProfile: vi.fn(),
  changePassword: vi.fn(),
  isAuthenticated: false,
  ...overrides,
});

// Helper to render component with providers
const renderWithProviders = (authValue: AuthContextValue) => {
  return render(
    <MemoryRouter>
      <AuthContext.Provider value={authValue}>
        <RegisterPage />
      </AuthContext.Provider>
    </MemoryRouter>
  );
};

describe('RegisterPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders register form with all fields', () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      expect(screen.getByText('Đăng ký')).toBeInTheDocument();
      expect(screen.getByText('Tạo tài khoản mới để sử dụng AI Code Reviewer')).toBeInTheDocument();
      
      expect(screen.getByLabelText('Họ và tên')).toBeInTheDocument();
      expect(screen.getByLabelText('Email')).toBeInTheDocument();
      expect(screen.getByLabelText('Mật khẩu')).toBeInTheDocument();
      expect(screen.getByLabelText('Xác nhận mật khẩu')).toBeInTheDocument();
      
      expect(screen.getByRole('button', { name: 'Tạo tài khoản' })).toBeInTheDocument();
      expect(screen.getByText('Đăng nhập ngay')).toBeInTheDocument();
    });

    it('redirects to dashboard if already authenticated', () => {
      const authValue = createMockAuthContext({ isAuthenticated: true });
      renderWithProviders(authValue);

      expect(mockNavigate).toHaveBeenCalledWith('/dashboard', { replace: true });
    });

    it('shows loading state when submitting', () => {
      const authValue = createMockAuthContext({ loading: true });
      renderWithProviders(authValue);

      expect(screen.getByText('Đang đăng ký...')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /đang đăng ký/i })).toBeDisabled();
    });
  });

  describe('Form Validation', () => {
    it('shows error for empty full name', async () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Vui lòng nhập họ và tên')).toBeInTheDocument();
      });
    });

    it('shows error for short full name', async () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      const fullNameInput = screen.getByLabelText('Họ và tên');
      fireEvent.change(fullNameInput, { target: { value: 'A' } });

      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Họ và tên phải có ít nhất 2 ký tự')).toBeInTheDocument();
      });
    });

    it('shows error for invalid email', async () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      const emailInput = screen.getByLabelText('Email');
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });

      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Email không hợp lệ')).toBeInTheDocument();
      });
    });

    it('shows error for weak password', async () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      const passwordInput = screen.getByLabelText('Mật khẩu');
      fireEvent.change(passwordInput, { target: { value: '123' } });

      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Mật khẩu phải có ít nhất 8 ký tự')).toBeInTheDocument();
      });
    });

    it('shows error for password without complexity requirements', async () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      const passwordInput = screen.getByLabelText('Mật khẩu');
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Mật khẩu phải chứa ít nhất 1 chữ hoa, 1 chữ thường, 1 số và 1 ký tự đặc biệt')).toBeInTheDocument();
      });
    });

    it('shows error for mismatched passwords', async () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      const passwordInput = screen.getByLabelText('Mật khẩu');
      const confirmPasswordInput = screen.getByLabelText('Xác nhận mật khẩu');
      
      fireEvent.change(passwordInput, { target: { value: 'Password123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'Different123!' } });

      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Mật khẩu xác nhận không khớp')).toBeInTheDocument();
      });
    });

    it('clears errors when user starts typing', async () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      // Trigger validation errors
      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Vui lòng nhập họ và tên')).toBeInTheDocument();
      });

      // Start typing in full name field
      const fullNameInput = screen.getByLabelText('Họ và tên');
      fireEvent.change(fullNameInput, { target: { value: 'John' } });

      await waitFor(() => {
        expect(screen.queryByText('Vui lòng nhập họ và tên')).not.toBeInTheDocument();
      });
    });
  });

  describe('Password Strength Indicator', () => {
    it('shows weak password strength', () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      const passwordInput = screen.getByLabelText('Mật khẩu');
      fireEvent.change(passwordInput, { target: { value: 'password' } });

      expect(screen.getByText('Yếu')).toBeInTheDocument();
    });

    it('shows medium password strength', () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      const passwordInput = screen.getByLabelText('Mật khẩu');
      fireEvent.change(passwordInput, { target: { value: 'Password123' } });

      expect(screen.getByText('Trung bình')).toBeInTheDocument();
    });

    it('shows strong password strength', () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      const passwordInput = screen.getByLabelText('Mật khẩu');
      fireEvent.change(passwordInput, { target: { value: 'Password123!' } });

      expect(screen.getByText('Mạnh')).toBeInTheDocument();
    });
  });

  describe('Password Visibility Toggle', () => {
    it('toggles password visibility', () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      const passwordInput = screen.getByLabelText('Mật khẩu') as HTMLInputElement;
      const toggleButton = screen.getAllByLabelText('Hiện mật khẩu')[0];

      expect(passwordInput.type).toBe('password');

      fireEvent.click(toggleButton);
      expect(passwordInput.type).toBe('text');

      fireEvent.click(toggleButton);
      expect(passwordInput.type).toBe('password');
    });

    it('toggles confirm password visibility', () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      const confirmPasswordInput = screen.getByLabelText('Xác nhận mật khẩu') as HTMLInputElement;
      const toggleButton = screen.getAllByLabelText('Hiện mật khẩu')[1];

      expect(confirmPasswordInput.type).toBe('password');

      fireEvent.click(toggleButton);
      expect(confirmPasswordInput.type).toBe('text');

      fireEvent.click(toggleButton);
      expect(confirmPasswordInput.type).toBe('password');
    });
  });

  describe('Form Submission', () => {
    it('submits form with valid data', async () => {
      const mockRegister = vi.fn().mockResolvedValue(undefined);
      const authValue = createMockAuthContext({ register: mockRegister });
      renderWithProviders(authValue);

      // Fill form with valid data
      fireEvent.change(screen.getByLabelText('Họ và tên'), { 
        target: { value: 'John Doe' } 
      });
      fireEvent.change(screen.getByLabelText('Email'), { 
        target: { value: 'john@example.com' } 
      });
      fireEvent.change(screen.getByLabelText('Mật khẩu'), { 
        target: { value: 'Password123!' } 
      });
      fireEvent.change(screen.getByLabelText('Xác nhận mật khẩu'), { 
        target: { value: 'Password123!' } 
      });

      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
          username: 'john@example.com',
          password: 'Password123!',
          full_name: 'John Doe',
        });
      });
    });

    it('handles registration error', async () => {
      const mockRegister = vi.fn().mockRejectedValue(new Error('Registration failed'));
      const authValue = createMockAuthContext({ register: mockRegister });
      renderWithProviders(authValue);

      // Fill form with valid data
      fireEvent.change(screen.getByLabelText('Họ và tên'), { 
        target: { value: 'John Doe' } 
      });
      fireEvent.change(screen.getByLabelText('Email'), { 
        target: { value: 'john@example.com' } 
      });
      fireEvent.change(screen.getByLabelText('Mật khẩu'), { 
        target: { value: 'Password123!' } 
      });
      fireEvent.change(screen.getByLabelText('Xác nhận mật khẩu'), { 
        target: { value: 'Password123!' } 
      });

      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Đăng ký thất bại. Email có thể đã được sử dụng.')).toBeInTheDocument();
      });
    });

    it('does not submit form with invalid data', async () => {
      const mockRegister = vi.fn();
      const authValue = createMockAuthContext({ register: mockRegister });
      renderWithProviders(authValue);

      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockRegister).not.toHaveBeenCalled();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper form labels and ARIA attributes', () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      const fullNameInput = screen.getByLabelText('Họ và tên');
      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Mật khẩu');
      const confirmPasswordInput = screen.getByLabelText('Xác nhận mật khẩu');

      expect(fullNameInput).toHaveAttribute('required');
      expect(emailInput).toHaveAttribute('required');
      expect(passwordInput).toHaveAttribute('required');
      expect(confirmPasswordInput).toHaveAttribute('required');

      expect(fullNameInput).toHaveAttribute('autoComplete', 'name');
      expect(emailInput).toHaveAttribute('autoComplete', 'email');
      expect(passwordInput).toHaveAttribute('autoComplete', 'new-password');
      expect(confirmPasswordInput).toHaveAttribute('autoComplete', 'new-password');
    });

    it('has proper error message associations', async () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        const fullNameInput = screen.getByLabelText('Họ và tên');
        const errorMessage = screen.getByText('Vui lòng nhập họ và tên');
        
        expect(fullNameInput).toHaveAttribute('aria-describedby', 'full-name-error');
        expect(errorMessage).toHaveAttribute('role', 'alert');
      });
    });
  });

  describe('Links and Navigation', () => {
    it('has link to login page', () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      const loginLink = screen.getByText('Đăng nhập ngay');
      expect(loginLink).toHaveAttribute('href', '/login');
    });

    it('has terms and privacy policy links', () => {
      const authValue = createMockAuthContext();
      renderWithProviders(authValue);

      expect(screen.getByText('Điều khoản dịch vụ')).toBeInTheDocument();
      expect(screen.getByText('Chính sách bảo mật')).toBeInTheDocument();
    });
  });
}); 