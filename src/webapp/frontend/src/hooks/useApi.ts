/**
 * Custom React hooks for API state management.
 * 
 * These hooks provide a consistent way to handle loading states,
 * errors, and data fetching for API calls.
 */

import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';
import {
  ReportDetail,
  ScanListItem,
  ScanRequest,
  ScanResponse,
  ApiResponse,
  ApiError
} from '../types';

// Generic API hook state
interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
}

/**
 * Hook for fetching scans list.
 * 
 * Args:
 *   limit: Maximum number of scans to fetch
 *   offset: Number of scans to skip for pagination
 * 
 * Returns:
 *   Object containing data, loading state, error, and refresh function
 */
export const useScans = (limit: number = 50, offset: number = 0) => {
  const [state, setState] = useState<ApiState<ScanListItem[]>>({
    data: null,
    loading: true,
    error: null,
  });

  const fetchScans = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    const response = await apiService.getScans(limit, offset);
    
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
  }, [limit, offset]);

  useEffect(() => {
    fetchScans();
  }, [fetchScans]);

  return {
    ...state,
    refetch: fetchScans,
  };
};

/**
 * Hook for fetching a specific scan report.
 * 
 * Args:
 *   scanId: The scan ID to fetch report for
 * 
 * Returns:
 *   Object containing data, loading state, error, and refresh function
 */
export const useReport = (scanId: string | undefined) => {
  const [state, setState] = useState<ApiState<ReportDetail>>({
    data: null,
    loading: true,
    error: null,
  });

  const fetchReport = useCallback(async () => {
    if (!scanId) {
      setState({
        data: null,
        loading: false,
        error: {
          detail: 'Scan ID is required',
          status_code: 400,
        },
      });
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));
    
    const response = await apiService.getWorkspaceReport(scanId);
    
    if (response.error) {
      setState({
        data: null,
        loading: false,
        error: response.error,
      });
    } else {
      setState({
        data: response.data || null,
        loading: false,
        error: null,
      });
    }
  }, [scanId]);

  useEffect(() => {
    fetchReport();
  }, [fetchReport]);

  return {
    ...state,
    refetch: fetchReport,
  };
};

/**
 * Hook for scan creation with loading state management.
 * 
 * Returns:
 *   Object containing createScan function, loading state, and error
 */
export const useCreateScan = () => {
  const [state, setState] = useState<ApiState<ScanResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const createScan = useCallback(async (scanRequest: ScanRequest): Promise<ScanResponse | null> => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    const response = await apiService.createScan(scanRequest);
    
    if (response.error) {
      setState({
        data: null,
        loading: false,
        error: response.error,
      });
      return null;
    } else {
      const scanResponse = response.data!;
      setState({
        data: scanResponse,
        loading: false,
        error: null,
      });
      return scanResponse;
    }
  }, []);

  return {
    ...state,
    createScan,
  };
};

/**
 * Hook for scan deletion with loading state management.
 * 
 * Returns:
 *   Object containing deleteScan function, loading state, and error
 */
export const useDeleteScan = () => {
  const [state, setState] = useState<ApiState<{ message: string }>>({
    data: null,
    loading: false,
    error: null,
  });

  const deleteScan = useCallback(async (scanId: string): Promise<boolean> => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    const response = await apiService.deleteScan(scanId);
    
    if (response.error) {
      setState({
        data: null,
        loading: false,
        error: response.error,
      });
      return false;
    } else {
      setState({
        data: response.data || { message: 'Scan deleted successfully' },
        loading: false,
        error: null,
      });
      return true;
    }
  }, []);

  return {
    ...state,
    deleteScan,
  };
};

/**
 * Generic hook for any API call with manual trigger.
 * 
 * Returns:
 *   Object containing execute function, loading state, data, and error
 */
export const useApiCall = <T>() => {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async (apiCall: () => Promise<ApiResponse<T>>): Promise<T | null> => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    const response = await apiCall();
    
    if (response.error) {
      setState({
        data: null,
        loading: false,
        error: response.error,
      });
      return null;
    } else {
      setState({
        data: response.data || null,
        loading: false,
        error: null,
      });
      return response.data || null;
    }
  }, []);

  return {
    ...state,
    execute,
  };
}; 