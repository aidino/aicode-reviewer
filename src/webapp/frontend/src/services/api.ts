/**
 * API Service cho AI Code Reviewer
 * 
 * Service này xử lý tất cả các HTTP requests tới backend API 
 * bằng cách sử dụng native fetch API thay vì axios.
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

// Base URL for API calls
const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000';

// Interceptor để thêm token authorization vào header
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  if (token) {
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }
  return {
    'Content-Type': 'application/json',
  };
};

// Mock data cho môi trường phát triển
const useMockData = import.meta.env.MODE === 'development';

// Tạo mock repositories để phát triển
const mockRepositories = [
  {
    id: '1',
    name: 'AI Code Reviewer',
    description: 'AI-powered code review tool that helps developers identify bugs and improve code quality.',
    url: 'https://github.com/example/aicode-reviewer',
    owner: {
      name: 'example-org',
      avatar_url: 'https://avatars.githubusercontent.com/u/12345678'
    },
    language: 'Python',
    stars: 1250,
    forks: 85,
    issues: 12,
    created_at: '2023-06-15T00:00:00Z',
    updated_at: '2024-05-01T12:34:56Z',
    default_branch: 'main',
    is_private: false,
    languages: {
      'Python': 65,
      'TypeScript': 25,
      'JavaScript': 10
    },
    cached_path: '/cache/repositories/1',
    last_commit_hash: '8f7e9d6c2a1b5f3e4d8c7b6a5f4e3d2c1b0a9f8e',
    cache_expires_at: '2024-06-01T00:00:00Z',
    cache_size_mb: 85.4
  },
  // Thêm mock repositories khác nếu cần
];

// Mock branches
const mockBranches = [
  { name: 'main', lastCommit: '8f7e9d6c2a1b', updatedAt: '2024-05-01T12:34:56Z' },
  { name: 'develop', lastCommit: '5e3d2c1b0a9f', updatedAt: '2024-05-01T10:20:30Z' },
  { name: 'feature/new-ui', lastCommit: 'c1b0a9f8e7d6', updatedAt: '2024-04-25T08:15:20Z' },
];

// Mock pull requests
const mockPRs = [
  { id: 101, number: 42, title: 'Add new repository dashboard', author: 'user1', updatedAt: '2024-05-01T11:22:33Z' },
  { id: 102, number: 41, title: 'Fix security vulnerabilities', author: 'user2', updatedAt: '2024-04-29T09:18:27Z' },
  { id: 103, number: 40, title: 'Optimize database queries', author: 'user3', updatedAt: '2024-04-28T14:05:16Z' },
];

// Mock recent scans
const mockRecentScans = [
  { 
    id: 's1', 
    created_at: '2024-05-01T14:30:00Z', 
    scan_type: 'full', 
    branch: 'main', 
    status: 'completed' 
  },
  { 
    id: 's2', 
    created_at: '2024-04-30T11:15:00Z', 
    scan_type: 'pr', 
    pr_number: '41',
    branch: 'fix-security', 
    status: 'completed' 
  },
  { 
    id: 's3', 
    created_at: '2024-04-30T10:00:00Z', 
    scan_type: 'pr', 
    pr_number: '40',
    branch: 'optimize-db', 
    status: 'failed' 
  },
  { 
    id: 's4', 
    created_at: '2024-05-02T09:20:00Z', 
    scan_type: 'full', 
    branch: 'develop', 
    status: 'in-progress' 
  }
];

interface ApiOptions {
  baseURL?: string;
  headers?: Record<string, string>;
}

class ApiService {
  private baseURL: string;
  private headers: Record<string, string>;
  private authToken: string | null = null;

  constructor(options: ApiOptions = {}) {
    this.baseURL = options.baseURL || API_BASE_URL;
    this.headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };
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
   * Sends a GET request to the specified endpoint
   */
  async get(endpoint: string) {
    try {
      const url = this.baseURL + endpoint;
      
      console.log('🌐 [API] Making request to:', url);
      console.log('🔑 [API] Has auth token:', !!this.authToken);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          ...this.headers,
          ...(this.authToken && { Authorization: `Bearer ${this.authToken}` })
        }
      });
      
      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Sends a POST request to the specified endpoint
   */
  async post(endpoint: string, data: any) {
    try {
      const url = this.baseURL + endpoint;
      
      console.log('🌐 [API] Making request to:', url);
      console.log('📦 [API] Request body:', data);
      console.log('🔑 [API] Has auth token:', !!this.authToken);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          ...this.headers,
          ...(this.authToken && { Authorization: `Bearer ${this.authToken}` })
        },
        body: JSON.stringify(data)
      });

      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Sends a PUT request to the specified endpoint
   */
  async put(endpoint: string, data: any) {
    try {
      const url = this.baseURL + endpoint;
      
      console.log('🌐 [API] Making request to:', url);
      console.log('📦 [API] Request body:', data);
      console.log('🔑 [API] Has auth token:', !!this.authToken);
      
      const response = await fetch(url, {
        method: 'PUT',
        headers: {
          ...this.headers,
          ...(this.authToken && { Authorization: `Bearer ${this.authToken}` })
        },
        body: JSON.stringify(data)
      });

      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Sends a DELETE request to the specified endpoint
   */
  async delete(endpoint: string) {
    try {
      const url = this.baseURL + endpoint;
      
      console.log('🌐 [API] Making request to:', url);
      console.log('🔑 [API] Has auth token:', !!this.authToken);
      
      const response = await fetch(url, {
        method: 'DELETE',
        headers: {
          ...this.headers,
          ...(this.authToken && { Authorization: `Bearer ${this.authToken}` })
        }
      });

      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Handle the response from the API
   */
  private async handleResponse(response: Response) {
    if (response.ok) {
      const data = await response.json();
      return {
        data,
        status: response.status,
      };
    }

    let errorData;
    try {
      errorData = await response.json();
    } catch (e) {
      errorData = {
        message: response.statusText
      };
    }

    return Promise.reject({
      status: response.status,
      message: errorData.message || 'An error occurred',
      details: errorData
    });
  }

  /**
   * Handle errors that occur during the API call
   */
  private handleError(error: any) {
    return Promise.reject({
      status: 0,
      message: error.message || 'Network error',
      details: error
    });
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
    
    return this.get(`/api/scans/?${params}`);
  }

  /**
   * Get repositories for current user.
   * 
   * Returns:
   *   Promise<ApiResponse<RepositoryListResponse>>: List of user repositories with statistics
   */
  async getRepositories(): Promise<ApiResponse<any>> {
    if (useMockData) {
      return Promise.resolve({ data: mockRepositories });
    }
    return this.get('/api/repositories/');
  }

  /**
   * Add a new repository.
   * 
   * Args:
   *   repoUrl: Repository URL
   *   accessToken: Optional PAT token for private repositories
   * 
   * Returns:
   *   Promise<ApiResponse<any>>: Added repository data
   */
  async addRepository(repoUrl: string, accessToken?: string): Promise<ApiResponse<any>> {
    const requestBody = {
      repo_url: repoUrl,
      ...(accessToken && { access_token: accessToken })
    };

    if (useMockData) {
      const newRepo = { 
        ...mockRepositories[0],
        id: Date.now().toString(),
        name: requestBody.repo_url.split('/').pop() || 'New Repository',
        url: requestBody.repo_url
      };
      return Promise.resolve({ data: newRepo });
    }
    return this.post('/api/repositories/', requestBody);
  }

  /**
   * Get detailed information for a specific repository.
   * 
   * Args:
   *   repositoryId: Repository ID
   * 
   * Returns:
   *   Promise<ApiResponse<any>>: Repository detail data
   */
  async getRepositoryDetail(repositoryId: string | number): Promise<ApiResponse<any>> {
    if (useMockData) {
      const repo = mockRepositories.find(r => r.id === repositoryId.toString());
      return Promise.resolve({ data: repo });
    }
    return this.get(`/api/repositories/${repositoryId}`);
  }

  /**
   * Update repository với metadata và code mới nhất từ remote.
   * 
   * Args:
   *   repositoryId: Repository ID
   * 
   * Returns:
   *   Promise<ApiResponse<any>>: Updated repository data
   */
  async updateRepositoryLatest(repositoryId: string | number): Promise<ApiResponse<any>> {
    if (useMockData) {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({ data: { message: 'Repository updated successfully' } });
        }, 1500);
      });
    }
    return this.post(`/api/repositories/${repositoryId}/update-latest`, {});
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

    return this.get(`/api/scans/${encodeURIComponent(scanId)}/report`);
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

    return this.get(`/api/scans/${encodeURIComponent(scanId)}/status`);
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
    return this.post('/api/scans/', scanRequest);
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

    return this.delete(`/api/scans/${encodeURIComponent(scanId)}`);
  }

  /**
   * Check API health.
   * 
   * Returns:
   *   Promise<ApiResponse<{status: string, service: string}>>: Health status
   */
  async checkHealth(): Promise<ApiResponse<{ status: string; service: string }>> {
    return this.get('/health');
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
    console.log('🔐 [API] Login attempt for:', credentials.username);
    
    const loginBody = {
      username_or_email: credentials.username,
      password: credentials.password,
    };
    
    console.log('📨 [API] Login request body (password hidden):', {
      username_or_email: credentials.username,
      password: credentials.password ? '••••••••' : '(empty)'
    });
    
    if (useMockData) {
      return Promise.resolve({
        data: {
          accessToken: 'mock-access-token',
          user: { id: 'user1', name: 'User', email: credentials.username }
        }
      });
    }
    return this.post('/auth/login', loginBody);
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
    console.log('📝 [API] Registration attempt for:', userData.username);
    console.log('📧 [API] Email:', userData.email);
    console.log('👤 [API] Full name:', userData.full_name);
    console.log('🔐 [API] Password length:', userData.password ? userData.password.length : 0);
    
    console.log('📨 [API] Registration request body (password hidden):', {
      ...userData,
      password: userData.password ? '••••••••' : '(empty)'
    });
    
    if (useMockData) {
      return Promise.resolve({
        data: {
          message: 'User registered successfully',
          user: { id: 'new-user', name: userData.full_name, email: userData.email }
        }
      });
    }
    return this.post('/auth/register', userData);
  }

  /**
   * User logout.
   * 
   * Returns:
   *   Promise<ApiResponse<{message: string}>>: Logout response
   */
  async logout(): Promise<ApiResponse<{ message: string }>> {
    return this.post('/auth/logout', {});
  }

  /**
   * Get current user profile.
   * 
   * Returns:
   *   Promise<ApiResponse<User>>: Current user data
   */
  async getCurrentUser(): Promise<ApiResponse<User>> {
    return this.get('/auth/me');
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
    return this.put('/auth/me', updates);
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
    return this.post('/auth/refresh', refreshData);
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
    return this.post('/auth/change-password', passwords);
  }

  /**
   * Get user sessions.
   * 
   * Returns:
   *   Promise<ApiResponse<UserSession[]>>: List of user sessions
   */
  async getUserSessions(): Promise<ApiResponse<UserSession[]>> {
    return this.get('/auth/sessions');
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
    return this.delete(`/auth/sessions/${sessionId}`);
  }

  /**
   * Revoke all sessions except current.
   * 
   * Returns:
   *   Promise<ApiResponse<{message: string}>>: Revoke response
   */
  async revokeAllSessions(): Promise<ApiResponse<{ message: string }>> {
    return this.delete('/auth/sessions');
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