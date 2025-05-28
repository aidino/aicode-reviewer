/**
 * Unit tests cho authentication hooks.
 * 
 * Test suite bao gồm validation logic, API operations, và error handling.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useUserSessions, useAuthOperations, useAuthValidation } from '../useAuth';
import { mockApiService, mockUserSessions, mockLoginResponse, resetAllAuthMocks } from '../../test/mocks/authMocks';

// Mock the API service
vi.mock('../../services/api', () => ({
  apiService: mockApiService,
}));

describe('useUserSessions', () => {
  beforeEach(() => {
    resetAllAuthMocks();
  });

  it('should fetch user sessions successfully', async () => {
    const { result } = renderHook(() => useUserSessions());

    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();

    await act(async () => {
      await result.current.fetchSessions();
    });

    expect(mockApiService.getUserSessions).toHaveBeenCalled();
    expect(result.current.data).toEqual(mockUserSessions);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should handle fetch sessions error', async () => {
    const error = { detail: 'Failed to fetch sessions', status_code: 500 };
    mockApiService.getUserSessions.mockResolvedValueOnce({ error });

    const { result } = renderHook(() => useUserSessions());

    await act(async () => {
      await result.current.fetchSessions();
    });

    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toEqual(error);
  });

  it('should revoke a specific session successfully', async () => {
    const { result } = renderHook(() => useUserSessions());

    // First fetch sessions
    await act(async () => {
      await result.current.fetchSessions();
    });

    // Then revoke a session
    let revokeResult: boolean;
    await act(async () => {
      revokeResult = await result.current.revokeSession('session-1');
    });

    expect(revokeResult!).toBe(true);
    expect(mockApiService.revokeSession).toHaveBeenCalledWith('session-1');
    // Should fetch sessions again after revoke
    expect(mockApiService.getUserSessions).toHaveBeenCalledTimes(2);
  });

  it('should handle revoke session error', async () => {
    const error = { detail: 'Failed to revoke session', status_code: 500 };
    mockApiService.revokeSession.mockResolvedValueOnce({ error });

    const { result } = renderHook(() => useUserSessions());

    let revokeResult: boolean;
    await act(async () => {
      revokeResult = await result.current.revokeSession('session-1');
    });

    expect(revokeResult!).toBe(false);
    expect(result.current.error).toEqual(error);
  });

  it('should revoke all sessions successfully', async () => {
    const { result } = renderHook(() => useUserSessions());

    let revokeResult: boolean;
    await act(async () => {
      revokeResult = await result.current.revokeAllSessions();
    });

    expect(revokeResult!).toBe(true);
    expect(mockApiService.revokeAllSessions).toHaveBeenCalled();
    expect(mockApiService.getUserSessions).toHaveBeenCalledTimes(1); // Auto-fetch after revoke
  });

  it('should handle revoke all sessions error', async () => {
    const error = { detail: 'Failed to revoke all sessions', status_code: 500 };
    mockApiService.revokeAllSessions.mockResolvedValueOnce({ error });

    const { result } = renderHook(() => useUserSessions());

    let revokeResult: boolean;
    await act(async () => {
      revokeResult = await result.current.revokeAllSessions();
    });

    expect(revokeResult!).toBe(false);
    expect(result.current.error).toEqual(error);
  });

  it('should show loading state during fetch', async () => {
    const { result } = renderHook(() => useUserSessions());

    act(() => {
      result.current.fetchSessions();
    });

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
  });
});

describe('useAuthOperations', () => {
  beforeEach(() => {
    resetAllAuthMocks();
  });

  describe('login', () => {
    it('should login successfully', async () => {
      const { result } = renderHook(() => useAuthOperations());

      const credentials = { username: 'testuser', password: 'password123' };
      let loginResult: any;

      await act(async () => {
        loginResult = await result.current.login(credentials);
      });

      expect(mockApiService.login).toHaveBeenCalledWith(credentials);
      expect(loginResult).toEqual(mockLoginResponse);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should handle login error', async () => {
      const error = { detail: 'Invalid credentials', status_code: 401 };
      mockApiService.login.mockResolvedValueOnce({ error });

      const { result } = renderHook(() => useAuthOperations());

      const credentials = { username: 'testuser', password: 'wrongpassword' };
      let loginResult: any;

      await act(async () => {
        loginResult = await result.current.login(credentials);
      });

      expect(loginResult).toBeNull();
      expect(result.current.error).toEqual(error);
      expect(result.current.loading).toBe(false);
    });

    it('should handle login exception', async () => {
      mockApiService.login.mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useAuthOperations());

      const credentials = { username: 'testuser', password: 'password123' };
      let loginResult: any;

      await act(async () => {
        loginResult = await result.current.login(credentials);
      });

      expect(loginResult).toBeNull();
      expect(result.current.error).toEqual({
        detail: 'Network error',
        status_code: 0,
      });
    });
  });

  describe('register', () => {
    it('should register successfully', async () => {
      const { result } = renderHook(() => useAuthOperations());

      const userData = {
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123',
        full_name: 'Test User',
      };
      let registerResult: any;

      await act(async () => {
        registerResult = await result.current.register(userData);
      });

      expect(mockApiService.register).toHaveBeenCalledWith(userData);
      expect(registerResult).toEqual(mockLoginResponse);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should handle register error', async () => {
      const error = { detail: 'Username already exists', status_code: 409 };
      mockApiService.register.mockResolvedValueOnce({ error });

      const { result } = renderHook(() => useAuthOperations());

      const userData = {
        username: 'existinguser',
        email: 'test@example.com',
        password: 'password123',
      };
      let registerResult: any;

      await act(async () => {
        registerResult = await result.current.register(userData);
      });

      expect(registerResult).toBeNull();
      expect(result.current.error).toEqual(error);
    });
  });

  describe('changePassword', () => {
    it('should change password successfully', async () => {
      const { result } = renderHook(() => useAuthOperations());

      const passwords = {
        current_password: 'oldpassword',
        new_password: 'newpassword123',
      };
      let changeResult: boolean;

      await act(async () => {
        changeResult = await result.current.changePassword(passwords);
      });

      expect(mockApiService.changePassword).toHaveBeenCalledWith(passwords);
      expect(changeResult!).toBe(true);
      expect(result.current.error).toBeNull();
    });

    it('should handle change password error', async () => {
      const error = { detail: 'Current password is incorrect', status_code: 400 };
      mockApiService.changePassword.mockResolvedValueOnce({ error });

      const { result } = renderHook(() => useAuthOperations());

      const passwords = {
        current_password: 'wrongpassword',
        new_password: 'newpassword123',
      };
      let changeResult: boolean;

      await act(async () => {
        changeResult = await result.current.changePassword(passwords);
      });

      expect(changeResult!).toBe(false);
      expect(result.current.error).toEqual(error);
    });
  });

  describe('updateProfile', () => {
    it('should update profile successfully', async () => {
      const { result } = renderHook(() => useAuthOperations());

      const updates = {
        full_name: 'Updated Name',
        timezone: 'UTC',
      };
      let updateResult: any;

      await act(async () => {
        updateResult = await result.current.updateProfile(updates);
      });

      expect(mockApiService.updateProfile).toHaveBeenCalledWith(updates);
      expect(updateResult).toBeDefined();
      expect(result.current.error).toBeNull();
    });

    it('should handle update profile error', async () => {
      const error = { detail: 'Invalid profile data', status_code: 400 };
      mockApiService.updateProfile.mockResolvedValueOnce({ error });

      const { result } = renderHook(() => useAuthOperations());

      const updates = { full_name: '' };
      let updateResult: any;

      await act(async () => {
        updateResult = await result.current.updateProfile(updates);
      });

      expect(updateResult).toBeNull();
      expect(result.current.error).toEqual(error);
    });
  });

  describe('clearError', () => {
    it('should clear error state', async () => {
      const error = { detail: 'Test error', status_code: 400 };
      mockApiService.login.mockResolvedValueOnce({ error });

      const { result } = renderHook(() => useAuthOperations());

      // Trigger an error
      await act(async () => {
        await result.current.login({ username: 'test', password: 'test' });
      });

      expect(result.current.error).toEqual(error);

      // Clear the error
      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });
});

describe('useAuthValidation', () => {
  it('should validate email correctly', () => {
    const { result } = renderHook(() => useAuthValidation());

    expect(result.current.validateEmail('')).toBe('Email là bắt buộc');
    expect(result.current.validateEmail('invalid-email')).toBe('Email không hợp lệ');
    expect(result.current.validateEmail('test@example.com')).toBeNull();
  });

  it('should validate username correctly', () => {
    const { result } = renderHook(() => useAuthValidation());

    expect(result.current.validateUsername('')).toBe('Tên đăng nhập là bắt buộc');
    expect(result.current.validateUsername('ab')).toBe('Tên đăng nhập phải có ít nhất 3 ký tự');
    expect(result.current.validateUsername('a'.repeat(51))).toBe('Tên đăng nhập không được quá 50 ký tự');
    expect(result.current.validateUsername('user@name')).toBe('Tên đăng nhập chỉ được chứa chữ cái, số, dấu gạch dưới và gạch ngang');
    expect(result.current.validateUsername('valid_user-123')).toBeNull();
  });

  it('should validate password correctly', () => {
    const { result } = renderHook(() => useAuthValidation());

    expect(result.current.validatePassword('')).toBe('Mật khẩu là bắt buộc');
    expect(result.current.validatePassword('short')).toBe('Mật khẩu phải có ít nhất 8 ký tự');
    expect(result.current.validatePassword('a'.repeat(129))).toBe('Mật khẩu không được quá 128 ký tự');
    expect(result.current.validatePassword('onlyletters')).toBe('Mật khẩu phải chứa ít nhất một chữ cái và một số');
    expect(result.current.validatePassword('12345678')).toBe('Mật khẩu phải chứa ít nhất một chữ cái và một số');
    expect(result.current.validatePassword('password123')).toBeNull();
  });

  it('should validate password confirmation correctly', () => {
    const { result } = renderHook(() => useAuthValidation());

    expect(result.current.validatePasswordConfirm('password123', '')).toBe('Xác nhận mật khẩu là bắt buộc');
    expect(result.current.validatePasswordConfirm('password123', 'different')).toBe('Mật khẩu xác nhận không khớp');
    expect(result.current.validatePasswordConfirm('password123', 'password123')).toBeNull();
  });

  it('should validate full name correctly', () => {
    const { result } = renderHook(() => useAuthValidation());

    expect(result.current.validateFullName('')).toBeNull(); // Optional field
    expect(result.current.validateFullName('a'.repeat(101))).toBe('Họ tên không được quá 100 ký tự');
    expect(result.current.validateFullName('Valid Name')).toBeNull();
  });

  it('should validate login form correctly', () => {
    const { result } = renderHook(() => useAuthValidation());

    const invalidCredentials = { username: '', password: '' };
    const validation = result.current.validateLoginForm(invalidCredentials);

    expect(validation.isValid).toBe(false);
    expect(validation.errors.username).toBe('Tên đăng nhập là bắt buộc');
    expect(validation.errors.password).toBe('Mật khẩu là bắt buộc');

    const validCredentials = { username: 'testuser', password: 'password123' };
    const validValidation = result.current.validateLoginForm(validCredentials);

    expect(validValidation.isValid).toBe(true);
    expect(Object.keys(validValidation.errors)).toHaveLength(0);
  });

  it('should validate register form correctly', () => {
    const { result } = renderHook(() => useAuthValidation());

    const invalidData = {
      username: '',
      email: 'invalid-email',
      password: 'short',
      full_name: 'a'.repeat(101),
    };
    const validation = result.current.validateRegisterForm(invalidData);

    expect(validation.isValid).toBe(false);
    expect(validation.errors.username).toBe('Tên đăng nhập là bắt buộc');
    expect(validation.errors.email).toBe('Email không hợp lệ');
    expect(validation.errors.password).toBe('Mật khẩu phải có ít nhất 8 ký tự');
    expect(validation.errors.full_name).toBe('Họ tên không được quá 100 ký tự');

    const validData = {
      username: 'testuser',
      email: 'test@example.com',
      password: 'password123',
      full_name: 'Test User',
    };
    const validValidation = result.current.validateRegisterForm(validData);

    expect(validValidation.isValid).toBe(true);
    expect(Object.keys(validValidation.errors)).toHaveLength(0);
  });

  it('should handle optional full name in register form', () => {
    const { result } = renderHook(() => useAuthValidation());

    const dataWithoutFullName = {
      username: 'testuser',
      email: 'test@example.com',
      password: 'password123',
    };
    const validation = result.current.validateRegisterForm(dataWithoutFullName);

    expect(validation.isValid).toBe(true);
    expect(validation.errors.full_name).toBeUndefined();
  });
}); 