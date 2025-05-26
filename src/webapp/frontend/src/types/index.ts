/**
 * TypeScript types for AI Code Reviewer frontend.
 * These types match the Pydantic models in the backend.
 */

export type ScanType = 'pr' | 'project';
export type ScanStatus = 'pending' | 'running' | 'completed' | 'failed';
export type SeverityLevel = 'low' | 'medium' | 'high' | 'critical';

export interface ScanInfo {
  scan_id: string;
  scan_type: ScanType;
  repository: string;
  branch?: string;
  pr_id?: number;
  target_branch?: string;
  source_branch?: string;
  commit_hash?: string;
  created_at: string;
  completed_at?: string;
}

export interface ScanSummary {
  total_findings: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  scan_status: ScanStatus;
  has_llm_analysis: boolean;
  execution_time_seconds?: number;
}

export interface StaticAnalysisFinding {
  id: string;
  rule_id: string;
  severity: SeverityLevel;
  category: string;
  message: string;
  file_path: string;
  line_number: number;
  column_number?: number;
  suggestion?: string;
  code_snippet?: string;
}

export interface LLMReview {
  section: string;
  content: string;
  confidence_score?: number;
  model_used?: string;
}

export interface DiagramData {
  diagram_type: string;
  diagram_content: string;
  format: string;
  metadata?: Record<string, any>;
}

export interface ScanMetadata {
  total_files_analyzed: number;
  languages_detected: string[];
  analysis_duration_seconds: number;
  llm_provider?: string;
  llm_model?: string;
  timestamp: string;
}

export interface ReportDetail {
  scan_info: ScanInfo;
  summary: ScanSummary;
  static_analysis_findings: StaticAnalysisFinding[];
  llm_analysis: LLMReview[];
  diagrams: DiagramData[];
  metadata: ScanMetadata;
}

export interface ScanListItem {
  scan_id: string;
  scan_type: ScanType;
  repository: string;
  status: ScanStatus;
  created_at: string;
  total_findings: number;
  pr_id?: number;
}

export interface ScanRequest {
  repo_url: string;
  scan_type: ScanType;
  pr_id?: number;
  target_branch?: string;
  source_branch?: string;
}

export interface ScanResponse {
  scan_id: string;
  status: ScanStatus;
  message: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

// API Response wrapper
export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
} 