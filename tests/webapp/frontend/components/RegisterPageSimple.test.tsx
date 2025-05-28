/**
 * Unit tests for RegisterPageSimple component
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { RegisterPageSimple } from '../../../../src/webapp/frontend/src/pages/RegisterPageSimple';

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Test component wrapper
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <MemoryRouter>
    {children}
  </MemoryRouter>
);

describe('RegisterPageSimple', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Component Rendering', () => {
    it('should render all form fields correctly', () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      // Check title and description
      expect(screen.getByText('📝 Đăng ký')).toBeInTheDocument();
      expect(screen.getByText('Tạo tài khoản mới để sử dụng AI Code Reviewer')).toBeInTheDocument();

      // Check form fields
      expect(screen.getByLabelText('Họ và tên:')).toBeInTheDocument();
      expect(screen.getByLabelText('Email:')).toBeInTheDocument();
      expect(screen.getByLabelText('Mật khẩu:')).toBeInTheDocument();
      expect(screen.getByLabelText('Xác nhận mật khẩu:')).toBeInTheDocument();

      // Check submit button
      expect(screen.getByRole('button', { name: 'Tạo tài khoản' })).toBeInTheDocument();

      // Check login link
      expect(screen.getByText('Đăng nhập ngay')).toBeInTheDocument();
    });

    it('should render password visibility toggle buttons', () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      // Password field should have visibility toggle
      const passwordToggles = screen.getAllByText('👁️');
      expect(passwordToggles).toHaveLength(2); // Password and confirm password
    });

    it('should render terms and privacy links', () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      expect(screen.getByText('Điều khoản dịch vụ')).toBeInTheDocument();
      expect(screen.getByText('Chính sách bảo mật')).toBeInTheDocument();
    });

    it('should render development mode notice', () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      expect(screen.getByText('🔧 DEV MODE: Mật khẩu chỉ cần ít nhất 1 ký tự')).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('should show validation errors for empty required fields', async () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Vui lòng nhập họ và tên')).toBeInTheDocument();
        expect(screen.getByText('Vui lòng nhập email')).toBeInTheDocument();
        expect(screen.getByText('Vui lòng nhập mật khẩu')).toBeInTheDocument();
        expect(screen.getByText('Vui lòng xác nhận mật khẩu')).toBeInTheDocument();
      });
    });

    it('should validate email format', async () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText('Email:');
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });

      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Email không hợp lệ')).toBeInTheDocument();
      });
    });

    it('should validate password strength requirements', async () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      // Test empty password
      const passwordInput = screen.getByLabelText('Mật khẩu:');
      fireEvent.change(passwordInput, { target: { value: '' } });

      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Vui lòng nhập mật khẩu')).toBeInTheDocument();
      });
      
      // Test that any non-empty password is accepted (dev mode)
      fireEvent.change(passwordInput, { target: { value: 'a' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.queryByText('Mật khẩu phải có ít nhất 1 ký tự (dev mode)')).not.toBeInTheDocument();
      });
    });

    it('should validate password confirmation match', async () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      const passwordInput = screen.getByLabelText('Mật khẩu:');
      const confirmPasswordInput = screen.getByLabelText('Xác nhận mật khẩu:');
      
      fireEvent.change(passwordInput, { target: { value: 'pass1' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'pass2' } });

      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Mật khẩu xác nhận không khớp')).toBeInTheDocument();
      });
    });

    it('should clear errors when user starts typing', async () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      // Trigger validation error
      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Vui lòng nhập họ và tên')).toBeInTheDocument();
      });

      // Start typing to clear error
      const fullNameInput = screen.getByLabelText('Họ và tên:');
      fireEvent.change(fullNameInput, { target: { value: 'John' } });

      await waitFor(() => {
        expect(screen.queryByText('Vui lòng nhập họ và tên')).not.toBeInTheDocument();
      });
    });
  });

  describe('Password Strength Indicator', () => {
    it('should show weak password strength for single character passwords', () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      const passwordInput = screen.getByLabelText('Mật khẩu:');
      fireEvent.change(passwordInput, { target: { value: 'a' } });

      expect(screen.getByText('Yếu')).toBeInTheDocument();
    });

    it('should show medium password strength for moderately complex passwords', () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      const passwordInput = screen.getByLabelText('Mật khẩu:');
      fireEvent.change(passwordInput, { target: { value: 'Password' } });

      expect(screen.getByText('Trung bình')).toBeInTheDocument();
    });

    it('should show strong password strength for complex passwords', () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      const passwordInput = screen.getByLabelText('Mật khẩu:');
      fireEvent.change(passwordInput, { target: { value: 'StrongPass123!' } });

      expect(screen.getByText('Mạnh')).toBeInTheDocument();
    });
  });

  describe('Password Visibility Toggle', () => {
    it('should toggle password visibility', () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      const passwordInput = screen.getByLabelText('Mật khẩu:') as HTMLInputElement;
      const toggleButtons = screen.getAllByText('👁️');
      const passwordToggle = toggleButtons[0];

      // Initially password should be hidden
      expect(passwordInput.type).toBe('password');

      // Click toggle to show password
      fireEvent.click(passwordToggle);
      expect(passwordInput.type).toBe('text');

      // Click again to hide password
      fireEvent.click(passwordToggle);
      expect(passwordInput.type).toBe('password');
    });

    it('should toggle confirm password visibility independently', () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      const confirmPasswordInput = screen.getByLabelText('Xác nhận mật khẩu:') as HTMLInputElement;
      const toggleButtons = screen.getAllByText('👁️');
      const confirmToggle = toggleButtons[1];

      // Initially confirm password should be hidden
      expect(confirmPasswordInput.type).toBe('password');

      // Click toggle to show confirm password
      fireEvent.click(confirmToggle);
      expect(confirmPasswordInput.type).toBe('text');
    });
  });

  describe('Form Submission', () => {
    it('should navigate to dashboard on successful form submission', async () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      // Fill out valid form with simple password (dev mode)
      fireEvent.change(screen.getByLabelText('Họ và tên:'), { 
        target: { value: 'John Doe' } 
      });
      fireEvent.change(screen.getByLabelText('Email:'), { 
        target: { value: 'john@example.com' } 
      });
      fireEvent.change(screen.getByLabelText('Mật khẩu:'), { 
        target: { value: 'simple' } 
      });
      fireEvent.change(screen.getByLabelText('Xác nhận mật khẩu:'), { 
        target: { value: 'simple' } 
      });

      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
      });
    });

    it('should not submit form with validation errors', async () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      // Fill out invalid form
      fireEvent.change(screen.getByLabelText('Email:'), { 
        target: { value: 'invalid-email' } 
      });

      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockNavigate).not.toHaveBeenCalled();
      });
    });
  });

  describe('UI Styling', () => {
    it('should apply consistent styling with LoginPageSimple', () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      // Check background color consistency
      const container = screen.getByText('📝 Đăng ký').closest('div');
      expect(container).toBeInTheDocument();

      // Check button color (emerald green for register vs blue for login)
      const submitButton = screen.getByRole('button', { name: 'Tạo tài khoản' });
      expect(submitButton).toHaveStyle({ backgroundColor: '#10b981' });
    });

    it('should show debug info section', () => {
      render(
        <TestWrapper>
          <RegisterPageSimple />
        </TestWrapper>
      );

      expect(screen.getByText('Debug Info:')).toBeInTheDocument();
      expect(screen.getByText(/Họ và tên:/)).toBeInTheDocument();
      expect(screen.getByText(/Email:/)).toBeInTheDocument();
      expect(screen.getByText(/Password:/)).toBeInTheDocument();
      expect(screen.getByText(/Confirm:/)).toBeInTheDocument();
    });
  });
}); 