/**
 * Unit tests cho LoginForm component.
 * 
 * Test suite bao gồm form validation, user interactions, và error handling.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from '../LoginForm';
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
    validateLoginForm: vi.fn().mockReturnValue({ isValid: true, errors: {} }),
  }),
}));

const renderLoginForm = (props = {}) => {
  return render(
    <AuthProvider>
      <LoginForm {...props} />
    </AuthProvider>
  );
};

describe('LoginForm', () => {
  beforeEach(() => {
    setupLocalStorageMock();
    resetAllAuthMocks();
  });

  describe('Rendering', () => {
    it('should render login form with all required fields', () => {
      renderLoginForm();

      expect(screen.getByText('Chào mừng trở lại')).toBeInTheDocument();
      expect(screen.getByText('Đăng nhập để tiếp tục sử dụng AI Code Reviewer')).toBeInTheDocument();
      expect(screen.getByLabelText(/tên đăng nhập/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/mật khẩu/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /đăng nhập/i })).toBeInTheDocument();
    });

    it('should render social login buttons', () => {
      renderLoginForm();

      expect(screen.getByText('Google')).toBeInTheDocument();
      expect(screen.getByText('GitHub')).toBeInTheDocument();
    });

    it('should render switch to register link', () => {
      renderLoginForm();

      expect(screen.getByText('Đăng ký ngay')).toBeInTheDocument();
    });

    it('should render remember me checkbox', () => {
      renderLoginForm();

      expect(screen.getByLabelText(/ghi nhớ đăng nhập/i)).toBeInTheDocument();
    });
  });

  describe('Form Interactions', () => {
    it('should update input values when user types', async () => {
      const user = userEvent.setup();
      renderLoginForm();

      const usernameInput = screen.getByLabelText(/tên đăng nhập/i);
      const passwordInput = screen.getByLabelText(/mật khẩu/i);

      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'password123');

      expect(usernameInput).toHaveValue('testuser');
      expect(passwordInput).toHaveValue('password123');
    });

    it('should toggle password visibility when eye icon is clicked', async () => {
      const user = userEvent.setup();
      renderLoginForm();

      const passwordInput = screen.getByLabelText(/mật khẩu/i);
      const toggleButton = screen.getByRole('button', { name: '' }); // Eye icon button

      expect(passwordInput).toHaveAttribute('type', 'password');

      await user.click(toggleButton);
      expect(passwordInput).toHaveAttribute('type', 'text');

      await user.click(toggleButton);
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    it('should toggle remember me checkbox', async () => {
      const user = userEvent.setup();
      renderLoginForm();

      const rememberCheckbox = screen.getByLabelText(/ghi nhớ đăng nhập/i);

      expect(rememberCheckbox).not.toBeChecked();

      await user.click(rememberCheckbox);
      expect(rememberCheckbox).toBeChecked();

      await user.click(rememberCheckbox);
      expect(rememberCheckbox).not.toBeChecked();
    });
  });

  describe('Form Submission', () => {
    it('should call login function with correct credentials on form submit', async () => {
      const user = userEvent.setup();
      renderLoginForm();

      const usernameInput = screen.getByLabelText(/tên đăng nhập/i);
      const passwordInput = screen.getByLabelText(/mật khẩu/i);
      const submitButton = screen.getByRole('button', { name: /đăng nhập/i });

      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockAuthContext.login).toHaveBeenCalledWith({
          username: 'testuser',
          password: 'password123',
        });
      });
    });

    it('should call onSuccess callback after successful login', async () => {
      const onSuccess = vi.fn();
      const user = userEvent.setup();
      renderLoginForm({ onSuccess });

      const usernameInput = screen.getByLabelText(/tên đăng nhập/i);
      const passwordInput = screen.getByLabelText(/mật khẩu/i);
      const submitButton = screen.getByRole('button', { name: /đăng nhập/i });

      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalled();
      });
    });

    it('should not submit form with empty fields', async () => {
      const user = userEvent.setup();
      
      // Mock validation to return errors for empty fields
      const mockValidation = vi.fn().mockReturnValue({
        isValid: false,
        errors: {
          username: 'Tên đăng nhập là bắt buộc',
          password: 'Mật khẩu là bắt buộc',
        },
      });

      vi.mocked(vi.importMock('../../../hooks/useAuth')).useAuthValidation = () => ({
        validateLoginForm: mockValidation,
      });

      renderLoginForm();

      const submitButton = screen.getByRole('button', { name: /đăng nhập/i });
      await user.click(submitButton);

      expect(mockAuthContext.login).not.toHaveBeenCalled();
    });
  });

  describe('Loading State', () => {
    it('should show loading state when login is in progress', () => {
      // Mock loading state
      const loadingAuthContext = { ...mockAuthContext, loading: true };
      vi.mocked(vi.importMock('../../../contexts/AuthContext')).useAuth = () => loadingAuthContext;

      renderLoginForm();

      expect(screen.getByText('Đang đăng nhập...')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /đang đăng nhập/i })).toBeDisabled();
    });

    it('should disable form inputs during loading', () => {
      const loadingAuthContext = { ...mockAuthContext, loading: true };
      vi.mocked(vi.importMock('../../../contexts/AuthContext')).useAuth = () => loadingAuthContext;

      renderLoginForm();

      expect(screen.getByLabelText(/tên đăng nhập/i)).toBeDisabled();
      expect(screen.getByLabelText(/mật khẩu/i)).toBeDisabled();
      expect(screen.getByLabelText(/ghi nhớ đăng nhập/i)).toBeDisabled();
    });
  });

  describe('Remember Me Functionality', () => {
    it('should save username to localStorage when remember me is checked', async () => {
      const user = userEvent.setup();
      renderLoginForm();

      const usernameInput = screen.getByLabelText(/tên đăng nhập/i);
      const rememberCheckbox = screen.getByLabelText(/ghi nhớ đăng nhập/i);

      await user.type(usernameInput, 'testuser');
      await user.click(rememberCheckbox);

      expect(mockApiService.setAuthToken).toHaveBeenCalled();
    });

    it('should load remembered username on component mount', () => {
      mockApiService.getAuthToken.mockReturnValue('remembered-user');
      
      renderLoginForm();

      // Component should attempt to load remembered username
      expect(mockApiService.getAuthToken).toHaveBeenCalled();
    });
  });

  describe('Switch to Register', () => {
    it('should call onSwitchToRegister when register link is clicked', async () => {
      const onSwitchToRegister = vi.fn();
      const user = userEvent.setup();
      renderLoginForm({ onSwitchToRegister });

      const registerLink = screen.getByText('Đăng ký ngay');
      await user.click(registerLink);

      expect(onSwitchToRegister).toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should display validation errors', async () => {
      const mockValidation = vi.fn().mockReturnValue({
        isValid: false,
        errors: {
          username: 'Tên đăng nhập không hợp lệ',
          password: 'Mật khẩu quá ngắn',
        },
      });

      vi.mocked(vi.importMock('../../../hooks/useAuth')).useAuthValidation = () => ({
        validateLoginForm: mockValidation,
      });

      const user = userEvent.setup();
      renderLoginForm();

      const submitButton = screen.getByRole('button', { name: /đăng nhập/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Tên đăng nhập không hợp lệ')).toBeInTheDocument();
        expect(screen.getByText('Mật khẩu quá ngắn')).toBeInTheDocument();
      });
    });

    it('should clear errors when user starts typing', async () => {
      const user = userEvent.setup();
      renderLoginForm();

      // First, trigger an error
      const mockValidation = vi.fn().mockReturnValue({
        isValid: false,
        errors: { username: 'Error message' },
      });

      vi.mocked(vi.importMock('../../../hooks/useAuth')).useAuthValidation = () => ({
        validateLoginForm: mockValidation,
      });

      const submitButton = screen.getByRole('button', { name: /đăng nhập/i });
      await user.click(submitButton);

      // Then type in the field to clear error
      const usernameInput = screen.getByLabelText(/tên đăng nhập/i);
      await user.type(usernameInput, 'a');

      // Error should be cleared by the component's logic
      await waitFor(() => {
        expect(screen.queryByText('Error message')).not.toBeInTheDocument();
      });
    });
  });
}); 