/**
 * TypeScript types for AI Code Reviewer frontend.
 * These types match the Pydantic models in the backend.
 */

export type ScanType = 'pr' | 'project';
export type ScanStatus = 'pending' | 'running' | 'completed' | 'failed';
export type SeverityLevel = 'Error' | 'Warning' | 'Info' | 'Unknown';

export interface ScanInfo {
  scan_id: string;
  repository: string;
  pr_id?: number;
  branch?: string;
  scan_type: ScanType;
  timestamp: string;
  report_version: string;
}

export interface ScanSummary {
  total_findings: number;
  severity_breakdown: Record<SeverityLevel, number>;
  category_breakdown: Record<string, number>;
  scan_status: ScanStatus;
  has_llm_analysis: boolean;
  error_message?: string;
}

export interface StaticAnalysisFinding {
  rule_id: string;
  message: string;
  line: number;
  column?: number;
  severity: SeverityLevel;
  category: string;
  file: string;
  suggestion?: string;
}

export interface LLMReview {
  insights: string;
  has_content: boolean;
  sections: Record<string, string>;
}

export interface DiagramData {
  type: string;
  content: string;
  format: string;
  title?: string;
  description?: string;
}

export interface ScanMetadata {
  agent_versions: Record<string, string>;
  generation_time: string;
  total_files_analyzed: number;
  successful_parses: number;
}

export interface ReportDetail {
  scan_info: ScanInfo;
  summary: ScanSummary;
  static_analysis_findings: StaticAnalysisFinding[];
  llm_review: LLMReview;
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

export interface ScanInitiateResponse {
  scan_id: string;
  job_id: string;
  status: ScanStatus;
  message: string;
  estimated_duration?: number;
  repository: string;
  scan_type: ScanType;
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

// Feedback Types
export type FeedbackType = 'finding' | 'llm_suggestion' | 'llm_insight' | 'diagram' | 'overall_report';
export type FeedbackRating = 'very_helpful' | 'helpful' | 'neutral' | 'not_helpful' | 'very_unhelpful';

export interface FeedbackRequest {
  scan_id: string;
  finding_id?: string;
  feedback_type: FeedbackType;
  is_helpful: boolean;
  rating?: FeedbackRating;
  comment?: string;
  user_id?: string;
  item_content?: string;
  rule_id?: string;
  suggestion_type?: string;
}

export interface FeedbackResponse {
  feedback_id: string;
  message: string;
  timestamp: string;
}

export interface FeedbackSummary {
  scan_id: string;
  total_feedback_count: number;
  helpful_count: number;
  not_helpful_count: number;
  feedback_types: Record<FeedbackType, number>;
  average_rating?: number;
}

export interface FeedbackDetail {
  feedback_id: string;
  scan_id: string;
  finding_id?: string;
  feedback_type: FeedbackType;
  is_helpful: boolean;
  rating?: FeedbackRating;
  comment: string;
  user_id?: string;
  item_content?: string;
  rule_id?: string;
  suggestion_type?: string;
  timestamp: string;
  metadata?: Record<string, any>;
} 