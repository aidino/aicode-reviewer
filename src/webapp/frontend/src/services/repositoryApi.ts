/**
 * API service for Repository-related functionality.
 * 
 * This module handles all Repository API interactions.
 */

import { Repository, AISettings } from '../types';
import { apiService } from './api';

// Mock repository data
const mockRepository: Repository = {
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
  cache_size_mb: 85.4,
  ai_settings: {
    llm_model: 'gpt-4o',
    model_provider: 'openai',
    api_key: 'sk-***************************',
    include_patterns: ['*.py', '*.ts', '*.tsx'],
    exclude_patterns: ['node_modules/**', 'venv/**', '**/__pycache__/**'],
    max_files_per_scan: 100,
    max_tokens_per_file: 8000,
    scan_depth: 2
  }
};

// Mock recent scans
const mockRecentScans = [
  { 
    id: 's1', 
    created_at: '2024-05-01T14:30:00Z', 
    scan_type: 'full', 
    branch: 'main', 
    status: 'completed',
    findings_count: 42
  },
  { 
    id: 's2', 
    created_at: '2024-04-30T11:15:00Z', 
    scan_type: 'pr', 
    pr_number: '41',
    branch: 'fix-security', 
    status: 'completed',
    findings_count: 15 
  },
  { 
    id: 's3', 
    created_at: '2024-04-30T10:00:00Z', 
    scan_type: 'pr', 
    pr_number: '40',
    branch: 'optimize-db', 
    status: 'failed',
    findings_count: 0
  },
  { 
    id: 's4', 
    created_at: '2024-05-02T09:20:00Z', 
    scan_type: 'full', 
    branch: 'develop', 
    status: 'in-progress',
    findings_count: 0 
  }
];

// Base API URL
const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000';

// Helper to get auth headers
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

/**
 * Get repository details by ID
 */
export const getRepositoryById = async (repositoryId: string): Promise<Repository> => {
  // For development, return mock data
  if (import.meta.env.MODE === 'development') {
    console.log('Using mock repository data');
    return Promise.resolve(mockRepository);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/repositories/${repositoryId}`, {
      headers: getAuthHeaders(),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch repository: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching repository:', error);
    throw error;
  }
};

/**
 * Update repository settings
 */
export const updateRepository = async (repositoryId: string, updates: Partial<Repository>): Promise<Repository> => {
  // For development, return mock data
  if (import.meta.env.MODE === 'development') {
    console.log('Using mock repository update');
    return Promise.resolve({...mockRepository, ...updates});
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/repositories/${repositoryId}`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(updates),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to update repository: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error updating repository:', error);
    throw error;
  }
};

/**
 * Update AI settings for a repository
 */
export const updateAISettings = async (repositoryId: string, settings: AISettings): Promise<Repository> => {
  // For development, return mock data
  if (import.meta.env.MODE === 'development') {
    console.log('Using mock AI settings update');
    return Promise.resolve({...mockRepository, ai_settings: settings});
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/repositories/${repositoryId}/ai-settings`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(settings),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to update AI settings: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error updating AI settings:', error);
    throw error;
  }
};

/**
 * Get recent scans for a repository
 */
export const getRecentScans = async (repositoryId: string, limit = 10): Promise<any[]> => {
  // For development, return mock data
  if (import.meta.env.MODE === 'development') {
    console.log('Using mock recent scans');
    return Promise.resolve(mockRecentScans);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/repositories/${repositoryId}/scans?limit=${limit}`, {
      headers: getAuthHeaders(),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch recent scans: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching recent scans:', error);
    throw error;
  }
};

/**
 * Start a new scan for a repository
 */
export const startRepositoryScan = async (repositoryId: string, scanData: { scan_type: 'full' | 'pr', pr_number?: string }): Promise<any> => {
  // For development, return mock data
  if (import.meta.env.MODE === 'development') {
    console.log('Using mock scan creation');
    return Promise.resolve({ 
      scan_id: 'new-scan-123', 
      status: 'queued',
      message: 'Scan queued successfully' 
    });
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/repositories/${repositoryId}/scans`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(scanData),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to start scan: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error starting scan:', error);
    throw error;
  }
};

export const repositoryApi = {
  /**
   * Lấy danh sách các lần scan gần đây của repository
   * @param repositoryId ID của repository
   */
  getRecentScans: (repositoryId: string) => {
    return apiService.get(`/api/repositories/${repositoryId}/scans`);
  },

  /**
   * Lấy thông tin cài đặt AI của repository
   * @param repositoryId ID của repository
   */
  getRepositoryAISettings: (repositoryId: string) => {
    return apiService.get(`/api/repositories/${repositoryId}/ai-settings`);
  },

  /**
   * Lưu cài đặt AI cho repository
   * @param repositoryId ID của repository
   * @param settings Thông tin cài đặt AI
   */
  saveRepositoryAISettings: (repositoryId: string, settings: any) => {
    return apiService.post(`/api/repositories/${repositoryId}/ai-settings`, settings);
  },

  /**
   * Bắt đầu scan repository
   * @param scanData Thông tin về scan
   */
  startRepositoryScan: (scanData: any) => {
    return apiService.post(`/api/repositories/${scanData.repositoryId}/scan`, scanData);
  },

  /**
   * Tạo một scan mới
   * @param repositoryId ID của repository
   * @param scanData Dữ liệu scan
   */
  createScan: (repositoryId: string, scanData: any) => {
    return apiService.post(`/api/repositories/${repositoryId}/scans`, scanData);
  },
}; 