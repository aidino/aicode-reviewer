/**
 * MSW (Mock Service Worker) handlers for API mocking in tests.
 * 
 * This file defines mock API responses for all backend endpoints used by the frontend.
 */

import { http, HttpResponse } from 'msw';
import { ScanListItem, ReportDetail, ScanResponse } from '../../types';

// Mock data
const mockScans: ScanListItem[] = [
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

const mockReport: ReportDetail = {
  scan_info: {
    scan_id: 'demo_scan_001',
    repository: 'user/test-repo',
    scan_type: 'pr',
    pr_id: 123,
    branch: 'feature/new-feature',
    timestamp: '2025-01-28T10:00:00Z',
    report_version: '1.0.0',
  },
  summary: {
    total_findings: 5,
    severity_breakdown: {
      'Error': 1,
      'Warning': 2,
      'Info': 1,
      'Unknown': 1,
    },
    category_breakdown: {
      'Security': 1,
      'Performance': 2,
      'Code Quality': 2,
    },
    scan_status: 'completed',
    has_llm_analysis: true,
  },
  static_analysis_findings: [
    {
      rule_id: 'security.hardcoded_secret',
      severity: 'Error',
      category: 'Security',
      message: 'Hardcoded API key detected',
      file: 'src/config.py',
      line: 15,
      column: 10,
      suggestion: 'Store sensitive data in environment variables',
    },
    {
      rule_id: 'performance.inefficient_loop',
      severity: 'Warning',
      category: 'Performance',
      message: 'Inefficient nested loop detected',
      file: 'src/utils.py',
      line: 42,
      suggestion: 'Consider using dictionary lookup or set operations',
    },
  ],
  llm_review: {
    insights: 'The code contains security vulnerabilities and performance issues. See sections for details.',
    has_content: true,
    sections: {
      'Security Analysis': 'The code contains potential security vulnerabilities:\n\n1. Hardcoded secrets in configuration files\n2. Missing input validation in user-facing endpoints\n\nRecommendations:\n- Use environment variables for sensitive data\n- Implement proper input sanitization',
      'Code Quality': 'Overall code quality is good with some areas for improvement:\n\n1. Function complexity could be reduced\n2. Missing docstrings in some modules\n\nRecommendations:\n- Break down large functions\n- Add comprehensive documentation',
    },
  },
  diagrams: [
    {
      type: 'Class Diagram',
      content: `@startuml
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
      title: 'Class Diagram - plantuml',
    },
  ],
  metadata: {
    agent_versions: {
      'static_analysis': '1.0.0',
      'llm_analysis': '1.0.0',
    },
    generation_time: '2025-01-28T10:05:00Z',
    total_files_analyzed: 25,
    successful_parses: 25,
  },
};

export const handlers = [
  // Get scans list - với prefix /api/
  http.get('/api/scans/', ({ request }) => {
    const url = new URL(request.url);
    const limit = parseInt(url.searchParams.get('limit') || '50');
    const offset = parseInt(url.searchParams.get('offset') || '0');
    
    const paginatedScans = mockScans.slice(offset, offset + limit);
    
    return HttpResponse.json(paginatedScans);
  }),
  
  // Fallback pattern without /api/
  http.get('/scans', ({ request }) => {
    const url = new URL(request.url);
    const limit = parseInt(url.searchParams.get('limit') || '50');
    const offset = parseInt(url.searchParams.get('offset') || '0');
    
    const paginatedScans = mockScans.slice(offset, offset + limit);
    
    return HttpResponse.json(paginatedScans);
  }),

  // Get scan report - với prefix /api/
  http.get('/api/scans/:scanId/report', ({ params }) => {
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

  // Get scan report - fallback pattern without /api/
  http.get('/scans/:scanId/report', ({ params }) => {
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

  // Get scan status
  http.get('/scans/:scanId/status', ({ params }) => {
    const { scanId } = params;
    
    const scan = mockScans.find(s => s.scan_id === scanId);
    if (!scan) {
      return HttpResponse.json(
        { detail: 'Scan not found' },
        { status: 404 }
      );
    }
    
    return HttpResponse.json({
      scan_id: scanId,
      status: scan.status,
      total_findings: scan.total_findings,
    });
  }),

  // Create scan
  http.post('/scans', async ({ request }) => {
    const body = await request.json() as any;
    
    if (!body.repo_url) {
      return HttpResponse.json(
        { detail: 'Repository URL is required' },
        { status: 400 }
      );
    }
    
    const newScanResponse: ScanResponse = {
      scan_id: `scan_${Date.now()}`,
      status: 'pending',
      message: 'Scan created successfully',
    };
    
    return HttpResponse.json(newScanResponse, { status: 201 });
  }),

  // Delete scan
  http.delete('/scans/:scanId', ({ params }) => {
    const { scanId } = params;
    
    if (scanId === 'nonexistent') {
      return HttpResponse.json(
        { detail: 'Scan not found' },
        { status: 404 }
      );
    }
    
    return HttpResponse.json({
      message: 'Scan deleted successfully',
    });
  }),

  // Health check
  http.get('/health', () => {
    return HttpResponse.json({
      status: 'healthy',
      service: 'AI Code Reviewer API',
    });
  }),
]; 