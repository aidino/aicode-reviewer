/**
 * API service for communicating with the AI Code Reviewer backend.
 * 
 * This service provides methods to interact with the FastAPI backend endpoints.
 */

import {
  ReportDetail,
  ScanListItem,
  ScanRequest,
  ScanResponse,
  ScanStatus,
  ApiResponse,
  ApiError,
  // Authentication types
  LoginRequest,
  RegisterRequest,
  LoginResponse,
  User,
  UserSession,
  RefreshTokenRequest,
  AuthTokens,
  ChangePasswordRequest,
  UpdateProfileRequest
} from '../types';

// API configuration
const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || '';

class ApiService {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    // Khôi phục token từ localStorage khi khởi tạo
    this.authToken = localStorage.getItem('access_token');
  }

  /**
   * Set authorization token for API requests.
   * 
   * Args:
   *   token: JWT access token
   */
  setAuthToken(token: string | null): void {
    this.authToken = token;
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
  }

  /**
   * Get authorization token.
   * 
   * Returns:
   *   string | null: Current access token
   */
  getAuthToken(): string | null {
    return this.authToken;
  }

  /**
   * Generic fetch wrapper with error handling.
   * 
   * Args:
   *   endpoint: API endpoint path
   *   options: Fetch options
   * 
   * Returns:
   *   Promise<ApiResponse<T>>: API response wrapper
   */
  private async fetchWithErrorHandling<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      
      const defaultHeaders: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      // Thêm Authorization header nếu có token
      if (this.authToken) {
        defaultHeaders['Authorization'] = `Bearer ${this.authToken}`;
      }

      const response = await fetch(url, {
        ...options,
        headers: {
          ...defaultHeaders,
          ...options.headers,
        },
      });

      if (!response.ok) {
        let errorDetail = `HTTP ${response.status}`;
        try {
          const errorData = await response.json();
          errorDetail = errorData.detail || errorDetail;
        } catch {
          // If we can't parse the error, use the status text
          errorDetail = response.statusText || errorDetail;
        }

        const apiError: ApiError = {
          detail: errorDetail,
          status_code: response.status,
        };

        return { error: apiError };
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      const apiError: ApiError = {
        detail: error instanceof Error ? error.message : 'Unknown error occurred',
        status_code: 0,
      };
      return { error: apiError };
    }
  }

  /**
   * Get all scans with optional pagination.
   * 
   * Args:
   *   limit: Maximum number of scans to return
   *   offset: Number of scans to skip
   * 
   * Returns:
   *   Promise<ApiResponse<ScanListItem[]>>: List of scans
   */
  async getScans(limit: number = 50, offset: number = 0): Promise<ApiResponse<ScanListItem[]>> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    
    return this.fetchWithErrorHandling<ScanListItem[]>(`/api/scans/?${params}`);
  }

  /**
   * Get detailed report for a specific scan.
   * 
   * Args:
   *   scanId: The scan ID to retrieve report for
   * 
   * Returns:
   *   Promise<ApiResponse<ReportDetail>>: Detailed scan report
   */
  async getWorkspaceReport(scanId: string): Promise<ApiResponse<ReportDetail>> {
    if (!scanId || scanId.trim() === '') {
      return {
        error: {
          detail: 'Scan ID is required',
          status_code: 400,
        },
      };
    }

    return this.fetchWithErrorHandling<ReportDetail>(`/api/scans/${encodeURIComponent(scanId)}/report`);
  }

  /**
   * Get scan status.
   * 
   * Args:
   *   scanId: The scan ID to check status for
   * 
   * Returns:
   *   Promise<ApiResponse<{scan_id: string, status: ScanStatus, total_findings: number}>>
   */
  async getScanStatus(scanId: string): Promise<ApiResponse<{
    scan_id: string;
    status: ScanStatus;
    total_findings: number;
  }>> {
    if (!scanId || scanId.trim() === '') {
      return {
        error: {
          detail: 'Scan ID is required',
          status_code: 400,
        },
      };
    }

    return this.fetchWithErrorHandling(`/api/scans/${encodeURIComponent(scanId)}/status`);
  }

  /**
   * Create a new scan.
   * 
   * Args:
   *   scanRequest: Scan configuration
   * 
   * Returns:
   *   Promise<ApiResponse<ScanResponse>>: Created scan response
   */
  async createScan(scanRequest: ScanRequest): Promise<ApiResponse<ScanResponse>> {
    return this.fetchWithErrorHandling<ScanResponse>('/api/scans/', {
      method: 'POST',
      body: JSON.stringify(scanRequest),
    });
  }

  /**
   * Delete a scan.
   * 
   * Args:
   *   scanId: The scan ID to delete
   * 
   * Returns:
   *   Promise<ApiResponse<{message: string}>>: Deletion response
   */
  async deleteScan(scanId: string): Promise<ApiResponse<{ message: string }>> {
    if (!scanId || scanId.trim() === '') {
      return {
        error: {
          detail: 'Scan ID is required',
          status_code: 400,
        },
      };
    }

    return this.fetchWithErrorHandling(`/api/scans/${encodeURIComponent(scanId)}`, {
      method: 'DELETE',
    });
  }

  /**
   * Check API health.
   * 
   * Returns:
   *   Promise<ApiResponse<{status: string, service: string}>>: Health status
   */
  async checkHealth(): Promise<ApiResponse<{ status: string; service: string }>> {
    return this.fetchWithErrorHandling('/health');
  }

  // Authentication Methods

  /**
   * User login.
   * 
   * Args:
   *   credentials: Login credentials
   * 
   * Returns:
   *   Promise<ApiResponse<LoginResponse>>: Login response with user and tokens
   */
  async login(credentials: LoginRequest): Promise<ApiResponse<LoginResponse>> {
    return this.fetchWithErrorHandling<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        username_or_email: credentials.username,
        password: credentials.password,
      }),
    });
  }

  /**
   * User registration.
   * 
   * Args:
   *   userData: Registration data
   * 
   * Returns:
   *   Promise<ApiResponse<LoginResponse>>: Registration response with user and tokens
   */
  async register(userData: RegisterRequest): Promise<ApiResponse<LoginResponse>> {
    return this.fetchWithErrorHandling<LoginResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  /**
   * User logout.
   * 
   * Returns:
   *   Promise<ApiResponse<{message: string}>>: Logout response
   */
  async logout(): Promise<ApiResponse<{ message: string }>> {
    return this.fetchWithErrorHandling<{ message: string }>('/auth/logout', {
      method: 'POST',
    });
  }

  /**
   * Get current user profile.
   * 
   * Returns:
   *   Promise<ApiResponse<User>>: Current user data
   */
  async getCurrentUser(): Promise<ApiResponse<User>> {
    return this.fetchWithErrorHandling<User>('/auth/me');
  }

  /**
   * Update user profile.
   * 
   * Args:
   *   updates: Profile updates
   * 
   * Returns:
   *   Promise<ApiResponse<User>>: Updated user data
   */
  async updateProfile(updates: UpdateProfileRequest): Promise<ApiResponse<User>> {
    return this.fetchWithErrorHandling<User>('/auth/me', {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  /**
   * Refresh access token.
   * 
   * Args:
   *   refreshData: Refresh token data
   * 
   * Returns:
   *   Promise<ApiResponse<AuthTokens>>: New tokens
   */
  async refreshToken(refreshData: RefreshTokenRequest): Promise<ApiResponse<AuthTokens>> {
    return this.fetchWithErrorHandling<AuthTokens>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify(refreshData),
    });
  }

  /**
   * Change user password.
   * 
   * Args:
   *   passwords: Current and new password
   * 
   * Returns:
   *   Promise<ApiResponse<{message: string}>>: Password change response
   */
  async changePassword(passwords: ChangePasswordRequest): Promise<ApiResponse<{ message: string }>> {
    return this.fetchWithErrorHandling<{ message: string }>('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify(passwords),
    });
  }

  /**
   * Get user sessions.
   * 
   * Returns:
   *   Promise<ApiResponse<UserSession[]>>: List of user sessions
   */
  async getUserSessions(): Promise<ApiResponse<UserSession[]>> {
    return this.fetchWithErrorHandling<UserSession[]>('/auth/sessions');
  }

  /**
   * Revoke a specific session.
   * 
   * Args:
   *   sessionId: Session ID to revoke
   * 
   * Returns:
   *   Promise<ApiResponse<{message: string}>>: Revoke response
   */
  async revokeSession(sessionId: string): Promise<ApiResponse<{ message: string }>> {
    return this.fetchWithErrorHandling<{ message: string }>(`/auth/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  }

  /**
   * Revoke all sessions except current.
   * 
   * Returns:
   *   Promise<ApiResponse<{message: string}>>: Revoke response
   */
  async revokeAllSessions(): Promise<ApiResponse<{ message: string }>> {
    return this.fetchWithErrorHandling<{ message: string }>('/auth/sessions', {
      method: 'DELETE',
    });
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export class for testing purposes
export { ApiService };

// Legacy compatibility - export WorkspaceReport function
export const WorkspaceReport = (scanId: string): Promise<ApiResponse<ReportDetail>> => {
  return apiService.getWorkspaceReport(scanId);
}; 