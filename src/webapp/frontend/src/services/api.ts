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
  ApiError
} from '../types';

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
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
      
      const defaultHeaders = {
        'Content-Type': 'application/json',
        ...options.headers,
      };

      const response = await fetch(url, {
        ...options,
        headers: defaultHeaders,
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
}

// Export singleton instance
export const apiService = new ApiService();

// Export class for testing purposes
export { ApiService };

// Legacy compatibility - export WorkspaceReport function
export const WorkspaceReport = (scanId: string): Promise<ApiResponse<ReportDetail>> => {
  return apiService.getWorkspaceReport(scanId);
}; 