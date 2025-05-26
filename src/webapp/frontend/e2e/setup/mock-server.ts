/**
 * Mock server setup for E2E testing.
 * 
 * This file provides a lightweight mock server that can be used during E2E tests
 * to avoid dependency on the actual backend API.
 */

import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

// Mock data - same as used in unit tests for consistency
const mockScans = [
  {
    scan_id: 'demo_scan_001',
    scan_type: 'pr',
    repository: 'user/test-repo',
    status: 'completed',
    created_at: '2025-01-28T10:00:00Z',
    total_findings: 5,
    pr_id: 123,
  },
  {
    scan_id: 'project_scan_002',
    scan_type: 'project',
    repository: 'org/project-repo',
    status: 'running',
    created_at: '2025-01-28T11:00:00Z',
    total_findings: 0,
  },
  {
    scan_id: 'pr_scan_003',
    scan_type: 'pr',
    repository: 'team/feature-repo',
    status: 'failed',
    created_at: '2025-01-28T12:00:00Z',
    total_findings: 0,
    pr_id: 456,
  },
];

const mockReport = {
  scan_info: {
    scan_id: 'demo_scan_001',
    scan_type: 'pr',
    repository: 'user/test-repo',
    branch: 'feature/new-feature',
    pr_id: 123,
    target_branch: 'main',
    source_branch: 'feature/new-feature',
    commit_hash: 'abc123def456',
    created_at: '2025-01-28T10:00:00Z',
    completed_at: '2025-01-28T10:05:00Z',
  },
  summary: {
    total_findings: 5,
    critical_count: 1,
    high_count: 2,
    medium_count: 1,
    low_count: 1,
    scan_status: 'completed',
    has_llm_analysis: true,
    execution_time_seconds: 300,
  },
  static_analysis_findings: [
    {
      id: 'finding_1',
      rule_id: 'security.hardcoded_secret',
      severity: 'critical',
      category: 'Security',
      message: 'Hardcoded API key detected',
      file_path: 'src/config.py',
      line_number: 15,
      column_number: 10,
      suggestion: 'Store sensitive data in environment variables',
      code_snippet: 'API_KEY = "sk-1234567890abcdef"',
    },
    {
      id: 'finding_2',
      rule_id: 'performance.inefficient_loop',
      severity: 'high',
      category: 'Performance',
      message: 'Inefficient nested loop detected',
      file_path: 'src/utils.py',
      line_number: 42,
      suggestion: 'Consider using dictionary lookup or set operations',
      code_snippet: 'for item in list1:\n    for item2 in list2:\n        if item == item2:',
    },
  ],
  llm_analysis: [
    {
      section: 'Security Analysis',
      content: 'The code contains potential security vulnerabilities:\n\n1. Hardcoded secrets in configuration files\n2. Missing input validation in user-facing endpoints\n\nRecommendations:\n- Use environment variables for sensitive data\n- Implement proper input sanitization',
      confidence_score: 0.85,
      model_used: 'gpt-4',
    },
    {
      section: 'Code Quality',
      content: 'Overall code quality is good with some areas for improvement:\n\n1. Function complexity could be reduced\n2. Missing docstrings in some modules\n\nRecommendations:\n- Break down large functions\n- Add comprehensive documentation',
      confidence_score: 0.78,
      model_used: 'gpt-4',
    },
  ],
  diagrams: [
    {
      diagram_type: 'Class Diagram',
      diagram_content: `@startuml
class User {
  +String name
  +String email
  +login()
}
class Admin {
  +String permissions
  +manage()
}
User <|-- Admin
@enduml`,
      format: 'plantuml',
      metadata: {
        generated_at: '2025-01-28T10:03:00Z',
        complexity_score: 0.6,
      },
    },
  ],
  metadata: {
    total_files_analyzed: 25,
    languages_detected: ['Python', 'JavaScript'],
    analysis_duration_seconds: 300,
    llm_provider: 'openai',
    llm_model: 'gpt-4',
    timestamp: '2025-01-28T10:05:00Z',
  },
};

// Create handlers for API endpoints
const handlers = [
  // Get scans list
  http.get('http://localhost:8000/scans', ({ request }) => {
    const url = new URL(request.url);
    const limit = parseInt(url.searchParams.get('limit') || '50');
    const offset = parseInt(url.searchParams.get('offset') || '0');
    
    const paginatedScans = mockScans.slice(offset, offset + limit);
    
    return HttpResponse.json(paginatedScans);
  }),

  // Get scan report
  http.get('http://localhost:8000/scans/:scanId/report', ({ params }) => {
    const { scanId } = params;
    
    if (scanId === 'nonexistent') {
      return HttpResponse.json(
        { detail: 'Scan not found' },
        { status: 404 }
      );
    }
    
    if (scanId === 'error_scan') {
      return HttpResponse.json(
        { detail: 'Internal server error' },
        { status: 500 }
      );
    }
    
    // Return mock report with updated scan_id
    const report = {
      ...mockReport,
      scan_info: {
        ...mockReport.scan_info,
        scan_id: scanId as string,
      },
    };
    
    return HttpResponse.json(report);
  }),

  // Health check
  http.get('http://localhost:8000/health', () => {
    return HttpResponse.json({
      status: 'healthy',
      service: 'AI Code Reviewer API (Mock)',
    });
  }),
];

// Create and export the server
export const server = setupServer(...handlers);

// Setup functions for testing
export const startMockServer = () => {
  server.listen({ onUnhandledRequest: 'warn' });
  console.log('Mock server started for E2E testing');
};

export const stopMockServer = () => {
  server.close();
  console.log('Mock server stopped');
};

export const resetMockServer = () => {
  server.resetHandlers();
};

export { handlers, mockScans, mockReport }; 