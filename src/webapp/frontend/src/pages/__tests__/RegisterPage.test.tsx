/**
 * Unit tests cho RegisterPage component với thiết kế minimalist 2025.
 * 
 * Test coverage:
 * - Rendering và layout
 * - Form validation
 * - Password strength indicator
 * - User interactions
 * - Accessibility
 * - Error handling
 * - Loading states
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { RegisterPage } from '../RegisterPage';
import { AuthContext } from '../../contexts/AuthContext';

// Mock AuthContext
const mockAuthContext = {
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
  isAuthenticated: false,
  user: null,
  loading: false,
  isInitialized: true,
};

// Mock react-router-dom
const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
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

// Helper to render component with providers
const renderRegisterPage = (authOverrides = {}) => {
  const authValue = { ...mockAuthContext, ...authOverrides };
  
  return render(
    <BrowserRouter>
      <AuthContext.Provider value={authValue}>
        <RegisterPage />
      </AuthContext.Provider>
    </BrowserRouter>
  );
};

describe('RegisterPage - Minimalist Design 2025', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering và Layout', () => {
    it('should render main elements correctly', () => {
      renderRegisterPage();
      
      expect(screen.getByRole('heading', { name: /tạo tài khoản/i })).toBeInTheDocument();
      expect(screen.getByText(/bắt đầu hành trình với ai code reviewer/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/họ và tên/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^mật khẩu$/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/xác nhận mật khẩu/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /tạo tài khoản/i })).toBeInTheDocument();
    });

    it('should have modern card layout with soft UI classes', () => {
      renderRegisterPage();
      
      const cardElements = document.querySelectorAll('.card-soft, .card-soft-body');
      expect(cardElements.length).toBeGreaterThan(0);
    });

    it('should have proper form structure', () => {
      renderRegisterPage();
      
      const form = screen.getByRole('form', { hidden: true });
      expect(form).toHaveAttribute('noValidate');
      
      const fullNameInput = screen.getByLabelText(/họ và tên/i);
      expect(fullNameInput).toHaveAttribute('type', 'text');
      expect(fullNameInput).toHaveAttribute('autoComplete', 'name');
      expect(fullNameInput).toHaveAttribute('required');
      
      const emailInput = screen.getByLabelText(/email/i);
      expect(emailInput).toHaveAttribute('type', 'email');
      expect(emailInput).toHaveAttribute('autoComplete', 'email');
      expect(emailInput).toHaveAttribute('required');
    });

    it('should show login link in footer', () => {
      renderRegisterPage();
      
      expect(screen.getByText(/đã có tài khoản\?/i)).toBeInTheDocument();
      const loginLink = screen.getByRole('link', { name: /đăng nhập ngay/i });
      expect(loginLink).toHaveAttribute('href', '/login');
    });

    it('should show terms and privacy policy links', () => {
      renderRegisterPage();
      
      const termsLink = screen.getByRole('link', { name: /điều khoản sử dụng/i });
      const privacyLink = screen.getByRole('link', { name: /chính sách bảo mật/i });
      
      expect(termsLink).toHaveAttribute('href', '/terms');
      expect(privacyLink).toHaveAttribute('href', '/privacy');
    });
  });

  describe('Form Validation', () => {
    it('should validate empty full name', async () => {
      const user = userEvent.setup();
      renderRegisterPage();
      
      const submitButton = screen.getByRole('button', { name: /tạo tài khoản/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/vui lòng nhập họ và tên/i)).toBeInTheDocument();
      });
    });

    it('should validate short full name', async () => {
      const user = userEvent.setup();
      renderRegisterPage();
      
      const fullNameInput = screen.getByLabelText(/họ và tên/i);
      await user.type(fullNameInput, 'A');
      
      const submitButton = screen.getByRole('button', { name: /tạo tài khoản/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/họ và tên phải có ít nhất 2 ký tự/i)).toBeInTheDocument();
      });
    });

    it('should validate invalid email format', async () => {
      const user = userEvent.setup();
      renderRegisterPage();
      
      const emailInput = screen.getByLabelText(/email/i);
      await user.type(emailInput, 'invalid-email');
      
      const submitButton = screen.getByRole('button', { name: /tạo tài khoản/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/email không hợp lệ/i)).toBeInTheDocument();
      });
    });

    it('should validate short password', async () => {
      const user = userEvent.setup();
      renderRegisterPage();
      
      const passwordInput = screen.getByLabelText(/^mật khẩu$/i);
      await user.type(passwordInput, '123');
      
      const submitButton = screen.getByRole('button', { name: /tạo tài khoản/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/mật khẩu phải có ít nhất 8 ký tự/i)).toBeInTheDocument();
      });
    });

    it('should validate password confirmation mismatch', async () => {
      const user = userEvent.setup();
      renderRegisterPage();
      
      const passwordInput = screen.getByLabelText(/^mật khẩu$/i);
      const confirmPasswordInput = screen.getByLabelText(/xác nhận mật khẩu/i);
      
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'different123');
      
      const submitButton = screen.getByRole('button', { name: /tạo tài khoản/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/mật khẩu xác nhận không khớp/i)).toBeInTheDocument();
      });
    });

    it('should validate terms agreement', async () => {
      const user = userEvent.setup();
      renderRegisterPage();
      
      // Fill all fields except terms
      const fullNameInput = screen.getByLabelText(/họ và tên/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^mật khẩu$/i);
      const confirmPasswordInput = screen.getByLabelText(/xác nhận mật khẩu/i);
      
      await user.type(fullNameInput, 'John Doe');
      await user.type(emailInput, 'john@example.com');
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'password123');
      
      const submitButton = screen.getByRole('button', { name: /tạo tài khoản/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/bạn phải đồng ý với điều khoản sử dụng/i)).toBeInTheDocument();
      });
    });

    it('should clear errors when user starts typing', async () => {
      const user = userEvent.setup();
      renderRegisterPage();
      
      // Trigger validation error first
      const submitButton = screen.getByRole('button', { name: /tạo tài khoản/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/vui lòng nhập họ và tên/i)).toBeInTheDocument();
      });
      
      // Start typing to clear error
      const fullNameInput = screen.getByLabelText(/họ và tên/i);
      await user.type(fullNameInput, 'J');
      
      await waitFor(() => {
        expect(screen.queryByText(/vui lòng nhập họ và tên/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Password Strength Indicator', () => {
    it('should show password strength indicator when typing password', async () => {
      const user = userEvent.setup();
      renderRegisterPage();
      
      const passwordInput = screen.getByLabelText(/^mật khẩu$/i);
      await user.type(passwordInput, 'weak');
      
      await waitFor(() => {
        expect(screen.getByText(/độ mạnh mật khẩu:/i)).toBeInTheDocument();
        expect(screen.getByText(/yếu/i)).toBeInTheDocument();
      });
    });

    it('should update password strength as user types', async () => {
      const user = userEvent.setup();
      renderRegisterPage();
      
      const passwordInput = screen.getByLabelText(/^mật khẩu$/i);
      
      // Test weak password
      await user.type(passwordInput, 'weak');
      await waitFor(() => {
        expect(screen.getByText(/yếu/i)).toBeInTheDocument();
      });
      
      // Clear and test stronger password
      await user.clear(passwordInput);
      await user.type(passwordInput, 'StrongP@ss123');
      await waitFor(() => {
        expect(screen.getByText(/mạnh/i)).toBeInTheDocument();
      });
    });

    it('should not show password strength when field is empty', () => {
      renderRegisterPage();
      
      expect(screen.queryByText(/độ mạnh mật khẩu:/i)).not.toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('should toggle password visibility', async () => {
      const user = userEvent.setup();
      renderRegisterPage();
      
      const passwordInput = screen.getByLabelText(/^mật khẩu$/i);
      const toggleButtons = screen.getAllByLabelText(/hiện mật khẩu/i);
      const passwordToggle = toggleButtons[0]; // First toggle for password field
      
      expect(passwordInput).toHaveAttribute('type', 'password');
      
      await user.click(passwordToggle);
      expect(passwordInput).toHaveAttribute('type', 'text');
      
      await user.click(passwordToggle);
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    it('should toggle confirm password visibility', async () => {
      const user = userEvent.setup();
      renderRegisterPage();
      
      const confirmPasswordInput = screen.getByLabelText(/xác nhận mật khẩu/i);
      const toggleButtons = screen.getAllByLabelText(/hiện mật khẩu/i);
      const confirmPasswordToggle = toggleButtons[1]; // Second toggle for confirm password field
      
      expect(confirmPasswordInput).toHaveAttribute('type', 'password');
      
      await user.click(confirmPasswordToggle);
      expect(confirmPasswordInput).toHaveAttribute('type', 'text');
      
      await user.click(confirmPasswordToggle);
      expect(confirmPasswordInput).toHaveAttribute('type', 'password');
    });

    it('should handle terms checkbox', async () => {
      const user = userEvent.setup();
      renderRegisterPage();
      
      const termsCheckbox = screen.getByRole('checkbox');
      expect(termsCheckbox).not.toBeChecked();
      
      await user.click(termsCheckbox);
      expect(termsCheckbox).toBeChecked();
      
      await user.click(termsCheckbox);
      expect(termsCheckbox).not.toBeChecked();
    });

    it('should submit form with valid data', async () => {
      const user = userEvent.setup();
      const mockRegister = vi.fn().mockResolvedValue({});
      renderRegisterPage({ register: mockRegister });
      
      const fullNameInput = screen.getByLabelText(/họ và tên/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^mật khẩu$/i);
      const confirmPasswordInput = screen.getByLabelText(/xác nhận mật khẩu/i);
      const termsCheckbox = screen.getByRole('checkbox');
      const submitButton = screen.getByRole('button', { name: /tạo tài khoản/i });
      
      await user.type(fullNameInput, 'John Doe');
      await user.type(emailInput, 'john@example.com');
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'password123');
      await user.click(termsCheckbox);
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
          username: 'john@example.com',
          email: 'john@example.com',
          password: 'password123',
          confirmPassword: 'password123',
          fullName: 'John Doe',
        });
      });
    });

    it('should handle registration failure', async () => {
      const user = userEvent.setup();
      const mockRegister = vi.fn().mockRejectedValue(new Error('Registration failed'));
      renderRegisterPage({ register: mockRegister });
      
      const fullNameInput = screen.getByLabelText(/họ và tên/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^mật khẩu$/i);
      const confirmPasswordInput = screen.getByLabelText(/xác nhận mật khẩu/i);
      const termsCheckbox = screen.getByRole('checkbox');
      const submitButton = screen.getByRole('button', { name: /tạo tài khoản/i });
      
      await user.type(fullNameInput, 'John Doe');
      await user.type(emailInput, 'john@example.com');
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'password123');
      await user.click(termsCheckbox);
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/email đã được sử dụng hoặc có lỗi xảy ra/i)).toBeInTheDocument();
      });
    });
  });

  describe('Loading States', () => {
    it('should show loading state during submission', () => {
      renderRegisterPage({ loading: true });
      
      const submitButton = screen.getByRole('button', { name: /đang tạo tài khoản\.\.\./i });
      expect(submitButton).toBeDisabled();
      expect(screen.getByText(/đang tạo tài khoản\.\.\./i)).toBeInTheDocument();
      
      // Check for loading spinner
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('should disable form inputs during loading', () => {
      renderRegisterPage({ loading: true });
      
      const fullNameInput = screen.getByLabelText(/họ và tên/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^mật khẩu$/i);
      const confirmPasswordInput = screen.getByLabelText(/xác nhận mật khẩu/i);
      const termsCheckbox = screen.getByRole('checkbox');
      
      expect(fullNameInput).toBeDisabled();
      expect(emailInput).toBeDisabled();
      expect(passwordInput).toBeDisabled();
      expect(confirmPasswordInput).toBeDisabled();
      expect(termsCheckbox).toBeDisabled();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels and descriptions', () => {
      renderRegisterPage();
      
      const fullNameInput = screen.getByLabelText(/họ và tên/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^mật khẩu$/i);
      const confirmPasswordInput = screen.getByLabelText(/xác nhận mật khẩu/i);
      
      expect(fullNameInput).toHaveAttribute('aria-describedby');
      expect(emailInput).toHaveAttribute('aria-describedby');
      expect(passwordInput).toHaveAttribute('aria-describedby');
      expect(confirmPasswordInput).toHaveAttribute('aria-describedby');
    });

    it('should show error messages with proper ARIA roles', async () => {
      const user = userEvent.setup();
      renderRegisterPage();
      
      const submitButton = screen.getByRole('button', { name: /tạo tài khoản/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        const errorMessage = screen.getByText(/vui lòng nhập họ và tên/i);
        expect(errorMessage).toHaveAttribute('role', 'alert');
        expect(errorMessage).toHaveAttribute('id', 'fullName-error');
      });
    });

    it('should have proper form accessibility attributes', () => {
      renderRegisterPage();
      
      const form = screen.getByRole('form', { hidden: true });
      expect(form).toHaveAttribute('noValidate');
      
      const inputs = [
        screen.getByLabelText(/họ và tên/i),
        screen.getByLabelText(/email/i),
        screen.getByLabelText(/^mật khẩu$/i),
        screen.getByLabelText(/xác nhận mật khẩu/i),
      ];
      
      inputs.forEach(input => {
        expect(input).toHaveAttribute('required');
      });
    });

    it('should have proper password strength indicator accessibility', async () => {
      const user = userEvent.setup();
      renderRegisterPage();
      
      const passwordInput = screen.getByLabelText(/^mật khẩu$/i);
      await user.type(passwordInput, 'test123');
      
      await waitFor(() => {
        const strengthIndicator = screen.getByText(/độ mạnh mật khẩu:/i).closest('div');
        expect(strengthIndicator).toHaveAttribute('id', 'password-strength');
        expect(passwordInput).toHaveAttribute('aria-describedby', expect.stringContaining('password-strength'));
      });
    });
  });

  describe('Navigation và Redirects', () => {
    it('should redirect to dashboard when authenticated', () => {
      renderRegisterPage({ isAuthenticated: true });
      
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard', { replace: true });
    });
  });
}); 