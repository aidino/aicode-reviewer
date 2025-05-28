/**
 * Authentication Context cho AI Code Reviewer.
 * 
 * Context này quản lý trạng thái authentication toàn cục,
 * bao gồm user login, logout, token refresh, và profile management.
 */

import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';
import {
  User,
  AuthContextValue,
  LoginRequest,
  RegisterRequest,
  ChangePasswordRequest,
  UpdateProfileRequest,
  ApiError
} from '../types';

// Auth state interface
interface AuthState {
  user: User | null;
  loading: boolean;
  error: ApiError | null;
  isAuthenticated: boolean;
}

// Auth actions
type AuthAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_ERROR'; payload: ApiError | null }
  | { type: 'LOGOUT' };

// Initial state
const initialState: AuthState = {
  user: null,
  loading: true,
  error: null,
  isAuthenticated: false,
};

// Auth reducer
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
      };
    case 'SET_USER':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: !!action.payload,
        loading: false,
        error: null,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        loading: false,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        loading: false,
        error: null,
      };
    default:
      return state;
  }
};

// Create context
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// Token management utilities
const TOKEN_STORAGE_KEY = 'refresh_token';
const TOKEN_REFRESH_INTERVAL = 14 * 60 * 1000; // 14 minutes (tokens expire in 15)

/**
 * AuthProvider component.
 * 
 * Cung cấp authentication context cho toàn bộ ứng dụng.
 */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  /**
   * Set error helper.
   */
  const setError = useCallback((error: ApiError | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  }, []);

  /**
   * Check if user is authenticated by verifying token and fetching user data.
   */
  const checkAuth = useCallback(async () => {
    const accessToken = apiService.getAuthToken();
    
    if (!accessToken) {
      dispatch({ type: 'SET_LOADING', payload: false });
      return;
    }

    try {
      const response = await apiService.getCurrentUser();
      
      if (response.error) {
        // Token might be expired, try to refresh
        await handleTokenRefresh();
      } else {
        dispatch({ type: 'SET_USER', payload: response.data! });
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      handleLogout();
    }
  }, []);

  /**
   * Handle token refresh.
   */
  const handleTokenRefresh = useCallback(async () => {
    const refreshToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    
    if (!refreshToken) {
      handleLogout();
      return;
    }

    try {
      const response = await apiService.refreshToken({ refresh_token: refreshToken });
      
      if (response.error) {
        handleLogout();
        return;
      }

      const tokens = response.data!;
      apiService.setAuthToken(tokens.access_token);
      localStorage.setItem(TOKEN_STORAGE_KEY, tokens.refresh_token);

      // Fetch user data after successful refresh
      const userResponse = await apiService.getCurrentUser();
      if (userResponse.data) {
        dispatch({ type: 'SET_USER', payload: userResponse.data });
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      handleLogout();
    }
  }, []);

  /**
   * Handle logout cleanup.
   */
  const handleLogout = useCallback(() => {
    apiService.setAuthToken(null);
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    dispatch({ type: 'LOGOUT' });
  }, []);

  /**
   * User login.
   */
  const login = useCallback(async (credentials: LoginRequest) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    setError(null);

    try {
      const response = await apiService.login(credentials);
      
      if (response.error) {
        setError(response.error);
        return;
      }

      const loginData = response.data!;
      
      // Store tokens
      apiService.setAuthToken(loginData.access_token);
      localStorage.setItem(TOKEN_STORAGE_KEY, loginData.refresh_token);
      
      dispatch({ type: 'SET_USER', payload: loginData.user });
    } catch (error) {
      setError({
        detail: error instanceof Error ? error.message : 'Login failed',
        status_code: 0,
      });
    }
  }, [setError]);

  /**
   * User registration.
   */
  const register = useCallback(async (userData: RegisterRequest) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    setError(null);

    try {
      const response = await apiService.register(userData);
      
      if (response.error) {
        setError(response.error);
        return;
      }

      const registerData = response.data!;
      
      // Store tokens
      apiService.setAuthToken(registerData.access_token);
      localStorage.setItem(TOKEN_STORAGE_KEY, registerData.refresh_token);
      
      dispatch({ type: 'SET_USER', payload: registerData.user });
    } catch (error) {
      setError({
        detail: error instanceof Error ? error.message : 'Registration failed',
        status_code: 0,
      });
    }
  }, [setError]);

  /**
   * User logout.
   */
  const logout = useCallback(async () => {
    try {
      // Call backend logout to invalidate token
      await apiService.logout();
    } catch (error) {
      console.error('Backend logout failed:', error);
    } finally {
      handleLogout();
    }
  }, [handleLogout]);

  /**
   * Refresh token manually.
   */
  const refreshToken = useCallback(async () => {
    await handleTokenRefresh();
  }, [handleTokenRefresh]);

  /**
   * Update user profile.
   */
  const updateProfile = useCallback(async (updates: UpdateProfileRequest) => {
    setError(null);

    try {
      const response = await apiService.updateProfile(updates);
      
      if (response.error) {
        setError(response.error);
        return;
      }

      dispatch({ type: 'SET_USER', payload: response.data! });
    } catch (error) {
      setError({
        detail: error instanceof Error ? error.message : 'Profile update failed',
        status_code: 0,
      });
    }
  }, [setError]);

  /**
   * Change user password.
   */
  const changePassword = useCallback(async (passwords: ChangePasswordRequest) => {
    setError(null);

    try {
      const response = await apiService.changePassword(passwords);
      
      if (response.error) {
        setError(response.error);
        return;
      }

      // Password changed successfully, no need to update user state
    } catch (error) {
      setError({
        detail: error instanceof Error ? error.message : 'Password change failed',
        status_code: 0,
      });
    }
  }, [setError]);

  // Setup token refresh interval
  useEffect(() => {
    let refreshInterval: NodeJS.Timeout;

    if (state.isAuthenticated) {
      refreshInterval = setInterval(() => {
        handleTokenRefresh();
      }, TOKEN_REFRESH_INTERVAL);
    }

    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [state.isAuthenticated, handleTokenRefresh]);

  // Initial auth check
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const contextValue: AuthContextValue = {
    user: state.user,
    loading: state.loading,
    login,
    register,
    logout,
    refreshToken,
    updateProfile,
    changePassword,
    isAuthenticated: state.isAuthenticated,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Hook để sử dụng Auth context.
 * 
 * Returns:
 *   AuthContextValue: Authentication context value
 * 
 * Throws:
 *   Error nếu được sử dụng ngoài AuthProvider
 */
export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}; 