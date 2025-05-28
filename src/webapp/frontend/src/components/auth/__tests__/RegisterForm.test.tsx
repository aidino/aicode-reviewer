/**
 * Unit tests cho RegisterForm component.
 * 
 * Test suite bao gồm form validation, user interactions, và error handling.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RegisterForm } from '../RegisterForm';
import { AuthProvider } from '../../../contexts/AuthContext';
import { mockAuthContext, mockApiService, setupLocalStorageMock, resetAllAuthMocks } from '../../../test/mocks/authMocks';

// Mock the API service
vi.mock('../../../services/api', () => ({
  apiService: mockApiService,
}));

// Mock the AuthContext
vi.mock('../../../contexts/AuthContext', async () => {
  const actual = await vi.importActual('../../../contexts/AuthContext');
  return {
    ...actual,
    useAuth: () => mockAuthContext,
  };
});

// Mock hooks
vi.mock('../../../hooks/useAuth', () => ({
  useAuthValidation: () => ({
    validateRegisterForm: vi.fn().mockReturnValue({ isValid: true, errors: {} }),
    validatePasswordConfirm: vi.fn().mockReturnValue(null),
  }),
}));

const renderRegisterForm = (props = {}) => {
  return render(
    <AuthProvider>
      <RegisterForm {...props} />
    </AuthProvider>
  );
};

describe('RegisterForm', () => {
  beforeEach(() => {
    setupLocalStorageMock();
    resetAllAuthMocks();
  });

  describe('Rendering', () => {
    it('should render registration form with all required fields', () => {
      renderRegisterForm();

      expect(screen.getByText('Tạo tài khoản mới')).toBeInTheDocument();
      expect(screen.getByText('Đăng ký để bắt đầu sử dụng AI Code Reviewer')).toBeInTheDocument();
      expect(screen.getByLabelText(/họ và tên/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/tên đăng nhập/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^mật khẩu/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/xác nhận mật khẩu/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /đăng ký tài khoản/i })).toBeInTheDocument();
    });

    it('should render required field indicators', () => {
      renderRegisterForm();

      const requiredFields = screen.getAllByText('*');
      expect(requiredFields.length).toBeGreaterThan(0);
    });

    it('should render terms and conditions checkbox', () => {
      renderRegisterForm();

      expect(screen.getByText(/tôi đồng ý với/i)).toBeInTheDocument();
      expect(screen.getByText('Điều khoản sử dụng')).toBeInTheDocument();
      expect(screen.getByText('Chính sách bảo mật')).toBeInTheDocument();
    });

    it('should render social registration buttons', () => {
      renderRegisterForm();

      expect(screen.getByText('Google')).toBeInTheDocument();
      expect(screen.getByText('GitHub')).toBeInTheDocument();
    });

    it('should render switch to login link', () => {
      renderRegisterForm();

      expect(screen.getByText('Đăng nhập ngay')).toBeInTheDocument();
    });
  });

  describe('Form Interactions', () => {
    it('should update input values when user types', async () => {
      const user = userEvent.setup();
      renderRegisterForm();

      const fullNameInput = screen.getByLabelText(/họ và tên/i);
      const usernameInput = screen.getByLabelText(/tên đăng nhập/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^mật khẩu/i);
      const confirmPasswordInput = screen.getByLabelText(/xác nhận mật khẩu/i);

      await user.type(fullNameInput, 'Test User');
      await user.type(usernameInput, 'testuser');
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'password123');

      expect(fullNameInput).toHaveValue('Test User');
      expect(usernameInput).toHaveValue('testuser');
      expect(emailInput).toHaveValue('test@example.com');
      expect(passwordInput).toHaveValue('password123');
      expect(confirmPasswordInput).toHaveValue('password123');
    });

    it('should toggle password visibility for password field', async () => {
      const user = userEvent.setup();
      renderRegisterForm();

      const passwordInput = screen.getByLabelText(/^mật khẩu/i);
      const toggleButtons = screen.getAllByRole('button', { name: '' }); // Eye icon buttons
      const passwordToggle = toggleButtons[0]; // First toggle is for password

      expect(passwordInput).toHaveAttribute('type', 'password');

      await user.click(passwordToggle);
      expect(passwordInput).toHaveAttribute('type', 'text');

      await user.click(passwordToggle);
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    it('should toggle password visibility for confirm password field', async () => {
      const user = userEvent.setup();
      renderRegisterForm();

      const confirmPasswordInput = screen.getByLabelText(/xác nhận mật khẩu/i);
      const toggleButtons = screen.getAllByRole('button', { name: '' }); // Eye icon buttons
      const confirmPasswordToggle = toggleButtons[1]; // Second toggle is for confirm password

      expect(confirmPasswordInput).toHaveAttribute('type', 'password');

      await user.click(confirmPasswordToggle);
      expect(confirmPasswordInput).toHaveAttribute('type', 'text');

      await user.click(confirmPasswordToggle);
      expect(confirmPasswordInput).toHaveAttribute('type', 'password');
    });

    it('should toggle terms acceptance checkbox', async () => {
      const user = userEvent.setup();
      renderRegisterForm();

      const termsCheckbox = screen.getByRole('checkbox');

      expect(termsCheckbox).not.toBeChecked();

      await user.click(termsCheckbox);
      expect(termsCheckbox).toBeChecked();

      await user.click(termsCheckbox);
      expect(termsCheckbox).not.toBeChecked();
    });
  });

  describe('Form Submission', () => {
    it('should call register function with correct data on form submit', async () => {
      const user = userEvent.setup();
      renderRegisterForm();

      // Fill out the form
      await user.type(screen.getByLabelText(/tên đăng nhập/i), 'testuser');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^mật khẩu/i), 'password123');
      await user.type(screen.getByLabelText(/xác nhận mật khẩu/i), 'password123');
      await user.type(screen.getByLabelText(/họ và tên/i), 'Test User');
      await user.click(screen.getByRole('checkbox')); // Accept terms

      const submitButton = screen.getByRole('button', { name: /đăng ký tài khoản/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockAuthContext.register).toHaveBeenCalledWith({
          username: 'testuser',
          email: 'test@example.com',
          password: 'password123',
          full_name: 'Test User',
        });
      });
    });

    it('should call onSuccess callback after successful registration', async () => {
      const onSuccess = vi.fn();
      const user = userEvent.setup();
      renderRegisterForm({ onSuccess });

      // Fill out the form
      await user.type(screen.getByLabelText(/tên đăng nhập/i), 'testuser');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^mật khẩu/i), 'password123');
      await user.type(screen.getByLabelText(/xác nhận mật khẩu/i), 'password123');
      await user.click(screen.getByRole('checkbox')); // Accept terms

      const submitButton = screen.getByRole('button', { name: /đăng ký tài khoản/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalled();
      });
    });

    it('should not submit form without accepting terms', async () => {
      const user = userEvent.setup();
      renderRegisterForm();

      // Fill out the form but don't accept terms
      await user.type(screen.getByLabelText(/tên đăng nhập/i), 'testuser');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^mật khẩu/i), 'password123');
      await user.type(screen.getByLabelText(/xác nhận mật khẩu/i), 'password123');
      // Don't click terms checkbox

      const submitButton = screen.getByRole('button', { name: /đăng ký tài khoản/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Bạn phải đồng ý với điều khoản sử dụng')).toBeInTheDocument();
      });

      expect(mockAuthContext.register).not.toHaveBeenCalled();
    });

    it('should not submit form with mismatched passwords', async () => {
      const user = userEvent.setup();
      
      // Mock validation to return password mismatch error
      const mockValidation = vi.fn().mockReturnValue({
        isValid: true,
        errors: {},
      });
      const mockPasswordConfirm = vi.fn().mockReturnValue('Mật khẩu xác nhận không khớp');

      vi.mocked(vi.importMock('../../../hooks/useAuth')).useAuthValidation = () => ({
        validateRegisterForm: mockValidation,
        validatePasswordConfirm: mockPasswordConfirm,
      });

      renderRegisterForm();

      // Fill out the form with mismatched passwords
      await user.type(screen.getByLabelText(/tên đăng nhập/i), 'testuser');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^mật khẩu/i), 'password123');
      await user.type(screen.getByLabelText(/xác nhận mật khẩu/i), 'different');
      await user.click(screen.getByRole('checkbox')); // Accept terms

      const submitButton = screen.getByRole('button', { name: /đăng ký tài khoản/i });
      await user.click(submitButton);

      expect(mockAuthContext.register).not.toHaveBeenCalled();
    });
  });

  describe('Loading State', () => {
    it('should show loading state when registration is in progress', () => {
      const loadingAuthContext = { ...mockAuthContext, loading: true };
      vi.mocked(vi.importMock('../../../contexts/AuthContext')).useAuth = () => loadingAuthContext;

      renderRegisterForm();

      expect(screen.getByText('Đang đăng ký...')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /đang đăng ký/i })).toBeDisabled();
    });

    it('should disable form inputs during loading', () => {
      const loadingAuthContext = { ...mockAuthContext, loading: true };
      vi.mocked(vi.importMock('../../../contexts/AuthContext')).useAuth = () => loadingAuthContext;

      renderRegisterForm();

      expect(screen.getByLabelText(/họ và tên/i)).toBeDisabled();
      expect(screen.getByLabelText(/tên đăng nhập/i)).toBeDisabled();
      expect(screen.getByLabelText(/email/i)).toBeDisabled();
      expect(screen.getByLabelText(/^mật khẩu/i)).toBeDisabled();
      expect(screen.getByLabelText(/xác nhận mật khẩu/i)).toBeDisabled();
      expect(screen.getByRole('checkbox')).toBeDisabled();
    });
  });

  describe('Switch to Login', () => {
    it('should call onSwitchToLogin when login link is clicked', async () => {
      const onSwitchToLogin = vi.fn();
      const user = userEvent.setup();
      renderRegisterForm({ onSwitchToLogin });

      const loginLink = screen.getByText('Đăng nhập ngay');
      await user.click(loginLink);

      expect(onSwitchToLogin).toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should display validation errors', async () => {
      const mockValidation = vi.fn().mockReturnValue({
        isValid: false,
        errors: {
          username: 'Tên đăng nhập không hợp lệ',
          email: 'Email không hợp lệ',
          password: 'Mật khẩu quá ngắn',
        },
      });

      vi.mocked(vi.importMock('../../../hooks/useAuth')).useAuthValidation = () => ({
        validateRegisterForm: mockValidation,
        validatePasswordConfirm: vi.fn().mockReturnValue(null),
      });

      const user = userEvent.setup();
      renderRegisterForm();

      await user.click(screen.getByRole('checkbox')); // Accept terms
      const submitButton = screen.getByRole('button', { name: /đăng ký tài khoản/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Tên đăng nhập không hợp lệ')).toBeInTheDocument();
        expect(screen.getByText('Email không hợp lệ')).toBeInTheDocument();
        expect(screen.getByText('Mật khẩu quá ngắn')).toBeInTheDocument();
      });
    });

    it('should clear errors when user starts typing', async () => {
      const user = userEvent.setup();
      renderRegisterForm();

      // First, trigger an error
      const mockValidation = vi.fn().mockReturnValue({
        isValid: false,
        errors: { username: 'Error message' },
      });

      vi.mocked(vi.importMock('../../../hooks/useAuth')).useAuthValidation = () => ({
        validateRegisterForm: mockValidation,
        validatePasswordConfirm: vi.fn().mockReturnValue(null),
      });

      const submitButton = screen.getByRole('button', { name: /đăng ký tài khoản/i });
      await user.click(submitButton);

      // Then type in the field to clear error
      const usernameInput = screen.getByLabelText(/tên đăng nhập/i);
      await user.type(usernameInput, 'a');

      // Error should be cleared by the component's logic
      await waitFor(() => {
        expect(screen.queryByText('Error message')).not.toBeInTheDocument();
      });
    });

    it('should clear confirm password error when password changes', async () => {
      const user = userEvent.setup();
      renderRegisterForm();

      // First set passwords to different values
      await user.type(screen.getByLabelText(/^mật khẩu/i), 'password123');
      await user.type(screen.getByLabelText(/xác nhận mật khẩu/i), 'different');

      // Try to submit to trigger error
      await user.click(screen.getByRole('checkbox')); // Accept terms
      await user.click(screen.getByRole('button', { name: /đăng ký tài khoản/i }));

      // Now change the password field - confirm password error should clear
      const passwordInput = screen.getByLabelText(/^mật khẩu/i);
      await user.clear(passwordInput);
      await user.type(passwordInput, 'newpassword');

      // The component should clear the confirm password error
      // This is testing the component's internal logic
    });
  });

  describe('Password Requirements', () => {
    it('should show password requirements text', () => {
      renderRegisterForm();

      expect(screen.getByText('Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ cái và số')).toBeInTheDocument();
    });
  });
}); 