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
const USER_STORAGE_KEY = 'user_data';
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
    console.log('🔐 checkAuth: Starting auth check');
    const accessToken = apiService.getAuthToken();
    const refreshToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    const savedUser = localStorage.getItem(USER_STORAGE_KEY);
    
    console.log('🎫 checkAuth: Access token found:', !!accessToken);
    console.log('🔄 checkAuth: Refresh token found:', !!refreshToken);
    console.log('👤 checkAuth: Saved user found:', !!savedUser);
    
    // If no tokens at all, definitely not authenticated
    if (!accessToken && !refreshToken) {
      console.log('❌ checkAuth: No tokens found, setting loading to false');
      dispatch({ type: 'SET_LOADING', payload: false });
      return;
    }

    // If we have saved user data and tokens, restore immediately to avoid UI flicker
    if (savedUser && (accessToken || refreshToken)) {
      try {
        const userData = JSON.parse(savedUser);
        console.log('📱 checkAuth: Restoring user from localStorage while verifying...');
        dispatch({ type: 'SET_USER', payload: userData });
      } catch (parseError) {
        console.error('🚫 checkAuth: Failed to parse saved user data, continuing with backend check');
      }
    }

    try {
      console.log('🌐 checkAuth: Checking authentication with backend...');
      
      // If we have access token, try to get current user first
      if (accessToken) {
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Auth check timeout')), 8000);
        });
        
        const apiPromise = apiService.getCurrentUser();
        const response = await Promise.race([apiPromise, timeoutPromise]);
        
        if (response.error) {
          console.log('🔄 checkAuth: Access token invalid, trying refresh...');
          await handleTokenRefresh();
        } else {
          console.log('✅ checkAuth: Auth check successful');
          console.log('👤 checkAuth: User data:', response.data);
          localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(response.data));
          dispatch({ type: 'SET_USER', payload: response.data! });
          return;
        }
      } else if (refreshToken) {
        // Only refresh token available, try to refresh
        console.log('🔄 checkAuth: Only refresh token available, attempting refresh...');
        await handleTokenRefresh();
      }
    } catch (error) {
      console.error('💥 checkAuth: Exception occurred:', error);
      if (error.message === 'Auth check timeout') {
        console.warn('⏰ checkAuth: Auth check timed out');
        // On timeout, if we have tokens and user data, keep user logged in
        if ((accessToken || refreshToken) && savedUser) {
          try {
            const userData = JSON.parse(savedUser);
            console.log('📱 checkAuth: Keeping user logged in due to timeout but tokens exist');
            dispatch({ type: 'SET_USER', payload: userData });
            return;
          } catch (parseError) {
            console.error('🚫 checkAuth: Failed to parse saved user data');
          }
        }
        
        // Even if no saved user data, keep logged in state if we have tokens
        // The user might lose some data but won't be logged out unnecessarily
        if (accessToken || refreshToken) {
          console.log('📱 checkAuth: Keeping authentication state due to existing tokens despite timeout');
          dispatch({ type: 'SET_LOADING', payload: false });
          return;
        }
      }
      
      // Only logout if we're sure tokens are invalid (not just network issues)
      if (error.message !== 'Auth check timeout' && 
          error.message !== 'Failed to fetch' && 
          !error.message.includes('network')) {
        console.error('🚪 checkAuth: Logging out due to auth error');
        handleLogout();
      } else {
        console.warn('⚠️ checkAuth: Network error, keeping user logged in');
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    }
  }, []);

  /**
   * Handle token refresh.
   */
  const handleTokenRefresh = useCallback(async () => {
    const refreshToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    
    if (!refreshToken) {
      console.log('🔄 handleTokenRefresh: No refresh token found, logging out');
      handleLogout();
      return;
    }

    try {
      console.log('🔄 handleTokenRefresh: Attempting token refresh...');
      const response = await apiService.refreshToken({ refresh_token: refreshToken });
      
      if (response.error) {
        console.log('❌ handleTokenRefresh: Refresh failed:', response.error);
        // Only logout if it's an authentication error, not network error
        if (response.error.status_code === 401 || response.error.status_code === 403) {
          console.log('🚪 handleTokenRefresh: Authentication error, logging out');
          handleLogout();
        } else {
          console.warn('⚠️ handleTokenRefresh: Network error during refresh, keeping user logged in');
          dispatch({ type: 'SET_LOADING', payload: false });
        }
        return;
      }

      const tokens = response.data!;
      apiService.setAuthToken(tokens.access_token);
      localStorage.setItem(TOKEN_STORAGE_KEY, tokens.refresh_token);
      console.log('✅ handleTokenRefresh: Token refresh successful');

      // Fetch user data after successful refresh
      try {
        const userResponse = await apiService.getCurrentUser();
        if (userResponse.data) {
          console.log('👤 handleTokenRefresh: User data fetched successfully');
          localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(userResponse.data));
          dispatch({ type: 'SET_USER', payload: userResponse.data });
        } else {
          console.warn('⚠️ handleTokenRefresh: Token refreshed but user data fetch failed, keeping user logged in');
          // Don't logout here - token is valid, just user data fetch failed temporarily
          dispatch({ type: 'SET_LOADING', payload: false });
        }
      } catch (userError) {
        console.warn('⚠️ handleTokenRefresh: Token refreshed but user data fetch threw error, keeping user logged in');
        console.warn('   User fetch error:', userError);
        // Don't logout here - token is valid, just user data fetch failed temporarily
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    } catch (error) {
      console.error('💥 handleTokenRefresh: Token refresh failed:', error);
      // Only logout if it's clearly an auth error, not network error
      if (error.message && (
          error.message.includes('401') || 
          error.message.includes('403') || 
          error.message.includes('unauthorized') ||
          error.message.includes('forbidden')
      )) {
        console.log('🚪 handleTokenRefresh: Authentication error, logging out');
        handleLogout();
      } else {
        console.warn('⚠️ handleTokenRefresh: Network error, keeping user logged in');
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    }
  }, []);

  /**
   * Handle logout cleanup.
   */
  const handleLogout = useCallback(() => {
    apiService.setAuthToken(null);
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    localStorage.removeItem(USER_STORAGE_KEY);
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
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(loginData.user));
      
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
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(registerData.user));
      
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
    console.log('🚀 AuthContext useEffect: Starting initial auth check');
    
    let timeoutId: NodeJS.Timeout;
    
    const performAuthCheck = async () => {
      try {
        console.log('🔍 AuthContext: Performing auth check...');
        await checkAuth();
        console.log('✅ AuthContext: Auth check completed');
      } catch (error) {
        console.error('❌ AuthContext: Initial auth check failed:', error);
        // Only set loading to false if we're sure there are no tokens
        const accessToken = apiService.getAuthToken();
        const refreshToken = localStorage.getItem(TOKEN_STORAGE_KEY);
        
        if (!accessToken && !refreshToken) {
          dispatch({ type: 'SET_LOADING', payload: false });
        } else {
          console.warn('⚠️ AuthContext: Auth check failed but tokens exist, keeping logged in');
          // Try to restore user from localStorage if available
          const savedUser = localStorage.getItem(USER_STORAGE_KEY);
          if (savedUser) {
            try {
              const userData = JSON.parse(savedUser);
              dispatch({ type: 'SET_USER', payload: userData });
            } catch (parseError) {
              dispatch({ type: 'SET_LOADING', payload: false });
            }
          } else {
            dispatch({ type: 'SET_LOADING', payload: false });
          }
        }
      }
    };
    
    // Set a timeout fallback - increased to 15 seconds and only logout if no tokens
    timeoutId = setTimeout(() => {
      console.warn('⏰ AuthContext: Auth check timeout - checking tokens before setting loading state');
      const accessToken = apiService.getAuthToken();
      const refreshToken = localStorage.getItem(TOKEN_STORAGE_KEY);
      const savedUser = localStorage.getItem(USER_STORAGE_KEY);
      
      if (accessToken || refreshToken) {
        if (savedUser) {
          try {
            const userData = JSON.parse(savedUser);
            console.log('📱 AuthContext: Timeout but tokens exist, restoring user');
            dispatch({ type: 'SET_USER', payload: userData });
            return;
          } catch (parseError) {
            console.error('🚫 AuthContext: Failed to parse saved user data on timeout');
          }
        }
        console.log('📱 AuthContext: Timeout but tokens exist, just stop loading');
        dispatch({ type: 'SET_LOADING', payload: false });
      } else {
        console.log('❌ AuthContext: Timeout and no tokens, setting loading to false');
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    }, 15000); // Increased to 15 seconds
    
    performAuthCheck().finally(() => {
      console.log('🏁 AuthContext: Auth check finished, clearing timeout');
      clearTimeout(timeoutId);
    });
    
    return () => {
      console.log('🧹 AuthContext: Cleanup timeout');
      clearTimeout(timeoutId);
    };
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