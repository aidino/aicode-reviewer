// Repository types
export interface Repository {
  id: string;
  name: string;
  description: string;
  url: string;
  owner: {
    name: string;
    avatar_url: string;
  };
  language: string;
  stars: number;
  forks: number;
  issues: number;
  created_at: string;
  updated_at: string;
  default_branch: string;
  is_private: boolean;
  languages: Record<string, number>;
  cached_path?: string;
  last_commit_hash?: string;
  cache_expires_at?: string;
  cache_size_mb?: number;
}

// Scan types
export type ScanType = 'full' | 'pr';

export interface Scan {
  id: string;
  created_at: string;
  scan_type: ScanType;
  branch: string;
  pr_number?: number;
  status: 'completed' | 'in-progress' | 'failed';
}

// AI Settings
export interface AISettings {
  model: string;
  modelName: string;
  apiKey?: string;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

// User types
export interface User {
  id: string;
  name: string;
  email: string;
  avatar_url?: string;
}

// Error types
export interface ApiError {
  status: number;
  message: string;
  details?: any;
} 