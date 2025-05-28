/**
 * Authentication mocks cho testing.
 * 
 * Cung cấp mock data và utilities cho testing authentication components.
 */

import { vi } from 'vitest';
import { User, LoginResponse, UserSession, AuthTokens } from '../../types';

// Mock User data
export const mockUser: User = {
  id: 'user-123',
  username: 'testuser',
  email: 'test@example.com',
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
  is_active: true,
  role: 'user',
  profile: {
    user_id: 'user-123',
    full_name: 'Test User',
    avatar_url: '',
    timezone: 'Asia/Ho_Chi_Minh',
    preferences: { theme: 'light' },
  },
};

// Mock Auth Tokens
export const mockTokens: AuthTokens = {
  access_token: 'mock-access-token',
  refresh_token: 'mock-refresh-token',
  token_type: 'Bearer',
  expires_in: 900, // 15 minutes
};

// Mock Login Response
export const mockLoginResponse: LoginResponse = {
  user: mockUser,
  tokens: mockTokens,
};

// Mock User Sessions
export const mockUserSessions: UserSession[] = [
  {
    id: 'session-1',
    user_id: 'user-123',
    token_id: 'token-1',
    created_at: '2025-01-01T00:00:00Z',
    last_used_at: '2025-01-01T01:00:00Z',
    is_active: true,
    user_agent: 'Mozilla/5.0 (Chrome)',
    ip_address: '192.168.1.1',
  },
  {
    id: 'session-2',
    user_id: 'user-123',
    token_id: 'token-2',
    created_at: '2025-01-01T00:00:00Z',
    last_used_at: '2025-01-01T02:00:00Z',
    is_active: true,
    user_agent: 'Mozilla/5.0 (Firefox)',
    ip_address: '192.168.1.2',
  },
];

// Mock API Service
export const mockApiService = {
  login: vi.fn().mockResolvedValue({ data: mockLoginResponse }),
  register: vi.fn().mockResolvedValue({ data: mockLoginResponse }),
  logout: vi.fn().mockResolvedValue({ data: { message: 'Logged out successfully' } }),
  getCurrentUser: vi.fn().mockResolvedValue({ data: mockUser }),
  updateProfile: vi.fn().mockResolvedValue({ data: mockUser }),
  changePassword: vi.fn().mockResolvedValue({ data: { message: 'Password changed successfully' } }),
  refreshToken: vi.fn().mockResolvedValue({ data: mockTokens }),
  getUserSessions: vi.fn().mockResolvedValue({ data: mockUserSessions }),
  revokeSession: vi.fn().mockResolvedValue({ data: { message: 'Session revoked' } }),
  revokeAllSessions: vi.fn().mockResolvedValue({ data: { message: 'All sessions revoked' } }),
  setAuthToken: vi.fn(),
  getAuthToken: vi.fn().mockReturnValue('mock-token'),
};

// Mock AuthContext
export const mockAuthContext = {
  user: mockUser,
  loading: false,
  login: vi.fn().mockResolvedValue(undefined),
  register: vi.fn().mockResolvedValue(undefined),
  logout: vi.fn().mockResolvedValue(undefined),
  refreshToken: vi.fn().mockResolvedValue(undefined),
  updateProfile: vi.fn().mockResolvedValue(undefined),
  changePassword: vi.fn().mockResolvedValue(undefined),
  isAuthenticated: true,
};

// Mock localStorage
export const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
};

// Setup localStorage mock
export const setupLocalStorageMock = () => {
  Object.defineProperty(window, 'localStorage', {
    value: mockLocalStorage,
    writable: true,
  });
};

// Reset all mocks
export const resetAllAuthMocks = () => {
  Object.values(mockApiService).forEach(mock => {
    if (typeof mock === 'function') {
      mock.mockClear();
    }
  });
  
  Object.values(mockAuthContext).forEach(mock => {
    if (typeof mock === 'function') {
      mock.mockClear();
    }
  });
  
  Object.values(mockLocalStorage).forEach(mock => {
    if (typeof mock === 'function') {
      mock.mockClear();
    }
  });
}; 