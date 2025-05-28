/**
 * Authentication hooks cho AI Code Reviewer.
 * 
 * Các hooks này cung cấp functionality riêng biệt cho
 * authentication operations.
 */

import { useState, useCallback } from 'react';
import { apiService } from '../services/api';
import {
  LoginRequest,
  RegisterRequest,
  ChangePasswordRequest,
  UpdateProfileRequest,
  UserSession,
  ApiError
} from '../types';

// Generic API hook state
interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
}

/**
 * Hook for user sessions management.
 * 
 * Returns:
 *   Object containing sessions data, loading state, error, và management functions
 */
export const useUserSessions = () => {
  const [state, setState] = useState<ApiState<UserSession[]>>({
    data: null,
    loading: false,
    error: null,
  });

  const fetchSessions = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    const response = await apiService.getUserSessions();
    
    if (response.error) {
      setState({
        data: null,
        loading: false,
        error: response.error,
      });
    } else {
      setState({
        data: response.data || [],
        loading: false,
        error: null,
      });
    }
  }, []);

  const revokeSession = useCallback(async (sessionId: string): Promise<boolean> => {
    const response = await apiService.revokeSession(sessionId);
    
    if (response.error) {
      setState(prev => ({ ...prev, error: response.error }));
      return false;
    }
    
    // Refresh sessions list after successful revoke
    await fetchSessions();
    return true;
  }, [fetchSessions]);

  const revokeAllSessions = useCallback(async (): Promise<boolean> => {
    const response = await apiService.revokeAllSessions();
    
    if (response.error) {
      setState(prev => ({ ...prev, error: response.error }));
      return false;
    }
    
    // Refresh sessions list after successful revoke
    await fetchSessions();
    return true;
  }, [fetchSessions]);

  return {
    ...state,
    fetchSessions,
    revokeSession,
    revokeAllSessions,
  };
};

/**
 * Hook for standalone authentication operations.
 * 
 * Sử dụng khi cần thực hiện auth operations mà không cập nhật global state.
 */
export const useAuthOperations = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const login = useCallback(async (credentials: LoginRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.login(credentials);
      
      if (response.error) {
        setError(response.error);
        return null;
      }

      return response.data;
    } catch (error) {
      setError({
        detail: error instanceof Error ? error.message : 'Login failed',
        status_code: 0,
      });
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (userData: RegisterRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.register(userData);
      
      if (response.error) {
        setError(response.error);
        return null;
      }

      return response.data;
    } catch (error) {
      setError({
        detail: error instanceof Error ? error.message : 'Registration failed',
        status_code: 0,
      });
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const changePassword = useCallback(async (passwords: ChangePasswordRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.changePassword(passwords);
      
      if (response.error) {
        setError(response.error);
        return false;
      }

      return true;
    } catch (error) {
      setError({
        detail: error instanceof Error ? error.message : 'Password change failed',
        status_code: 0,
      });
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateProfile = useCallback(async (updates: UpdateProfileRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.updateProfile(updates);
      
      if (response.error) {
        setError(response.error);
        return null;
      }

      return response.data;
    } catch (error) {
      setError({
        detail: error instanceof Error ? error.message : 'Profile update failed',
        status_code: 0,
      });
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    loading,
    error,
    login,
    register,
    changePassword,
    updateProfile,
    clearError,
  };
};

/**
 * Hook for form validation.
 * 
 * Cung cấp validation logic cho authentication forms.
 */
export const useAuthValidation = () => {
  const validateEmail = useCallback((email: string): string | null => {
    if (!email) return 'Email là bắt buộc';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) return 'Email không hợp lệ';
    return null;
  }, []);

  const validateUsername = useCallback((username: string): string | null => {
    if (!username) return 'Tên đăng nhập là bắt buộc';
    if (username.length < 3) return 'Tên đăng nhập phải có ít nhất 3 ký tự';
    if (username.length > 50) return 'Tên đăng nhập không được quá 50 ký tự';
    if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
      return 'Tên đăng nhập chỉ được chứa chữ cái, số, dấu gạch dưới và gạch ngang';
    }
    return null;
  }, []);

  const validatePassword = useCallback((password: string): string | null => {
    if (!password) return 'Mật khẩu là bắt buộc';
    if (password.length < 8) return 'Mật khẩu phải có ít nhất 8 ký tự';
    if (password.length > 128) return 'Mật khẩu không được quá 128 ký tự';
    
    // Check for at least one letter and one number
    if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(password)) {
      return 'Mật khẩu phải chứa ít nhất một chữ cái và một số';
    }
    
    return null;
  }, []);

  const validatePasswordConfirm = useCallback((password: string, confirmPassword: string): string | null => {
    if (!confirmPassword) return 'Xác nhận mật khẩu là bắt buộc';
    if (password !== confirmPassword) return 'Mật khẩu xác nhận không khớp';
    return null;
  }, []);

  const validateFullName = useCallback((fullName: string): string | null => {
    if (fullName && fullName.length > 100) return 'Họ tên không được quá 100 ký tự';
    return null;
  }, []);

  const validateLoginForm = useCallback((credentials: LoginRequest) => {
    const errors: Partial<Record<keyof LoginRequest, string>> = {};
    
    const usernameError = validateUsername(credentials.username);
    if (usernameError) errors.username = usernameError;
    
    const passwordError = validatePassword(credentials.password);
    if (passwordError) errors.password = passwordError;
    
    return {
      isValid: Object.keys(errors).length === 0,
      errors,
    };
  }, [validateUsername, validatePassword]);

  const validateRegisterForm = useCallback((userData: RegisterRequest) => {
    const errors: Partial<Record<keyof RegisterRequest, string>> = {};
    
    const usernameError = validateUsername(userData.username);
    if (usernameError) errors.username = usernameError;
    
    const emailError = validateEmail(userData.email);
    if (emailError) errors.email = emailError;
    
    const passwordError = validatePassword(userData.password);
    if (passwordError) errors.password = passwordError;
    
    if (userData.full_name) {
      const fullNameError = validateFullName(userData.full_name);
      if (fullNameError) errors.full_name = fullNameError;
    }
    
    return {
      isValid: Object.keys(errors).length === 0,
      errors,
    };
  }, [validateUsername, validateEmail, validatePassword, validateFullName]);

  return {
    validateEmail,
    validateUsername,
    validatePassword,
    validatePasswordConfirm,
    validateFullName,
    validateLoginForm,
    validateRegisterForm,
  };
}; 