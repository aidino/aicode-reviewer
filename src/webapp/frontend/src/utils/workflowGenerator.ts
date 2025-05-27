/**
 * Workflow Generator Utility
 * 
 * Utilities for generating agent workflow graphs from orchestrator data.
 * Maps orchestrator state to React Flow compatible graph structure.
 */

import { AgentNode, AgentEdge, WorkflowState, AgentStatus } from '../types/agent';

// Agent mapping from orchestrator to display
export const AGENT_MAPPING = {
  'start_scan': {
    label: 'Khởi tạo Scan',
    type: 'start' as const,
    position: { x: 100, y: 100 }
  },
  'fetch_code': {
    label: 'Lấy Code',
    type: 'agent' as const,
    position: { x: 300, y: 100 }
  },
  'parse_code': {
    label: 'Phân tích AST',
    type: 'agent' as const,
    position: { x: 500, y: 100 }
  },
  'static_analysis': {
    label: 'Phân tích Static',
    type: 'agent' as const,
    position: { x: 700, y: 100 }
  },
  'impact_analysis': {
    label: 'Phân tích Impact',
    type: 'agent' as const,
    position: { x: 900, y: 50 }
  },
  'llm_analysis': {
    label: 'Phân tích LLM',
    type: 'agent' as const,
    position: { x: 900, y: 150 }
  },
  'project_scanning': {
    label: 'Scan Project',
    type: 'agent' as const,
    position: { x: 700, y: 200 }
  },
  'reporting': {
    label: 'Tạo Report',
    type: 'agent' as const,
    position: { x: 1100, y: 100 }
  },
  'handle_error': {
    label: 'Xử lý Lỗi',
    type: 'agent' as const,
    position: { x: 600, y: 300 }
  },
  'end': {
    label: 'Hoàn thành',
    type: 'end' as const,
    position: { x: 1300, y: 100 }
  }
};

// Edge definitions for the workflow
export const WORKFLOW_EDGES: AgentEdge[] = [
  {
    id: 'start-fetch',
    source: 'start_scan',
    target: 'fetch_code',
    type: 'default'
  },
  {
    id: 'fetch-parse',
    source: 'fetch_code',
    target: 'parse_code',
    type: 'default'
  },
  {
    id: 'parse-static',
    source: 'parse_code',
    target: 'static_analysis',
    type: 'default'
  },
  {
    id: 'static-impact',
    source: 'static_analysis',
    target: 'impact_analysis',
    type: 'conditional',
    label: 'PR scan'
  },
  {
    id: 'static-project',
    source: 'static_analysis',
    target: 'project_scanning',
    type: 'conditional',
    label: 'Project scan'
  },
  {
    id: 'impact-llm',
    source: 'impact_analysis',
    target: 'llm_analysis',
    type: 'default'
  },
  {
    id: 'project-llm',
    source: 'project_scanning',
    target: 'llm_analysis',
    type: 'default'
  },
  {
    id: 'llm-report',
    source: 'llm_analysis',
    target: 'reporting',
    type: 'default'
  },
  {
    id: 'report-end',
    source: 'reporting',
    target: 'end',
    type: 'default'
  },
  // Error handling edges
  {
    id: 'fetch-error',
    source: 'fetch_code',
    target: 'handle_error',
    type: 'error',
    label: 'Error'
  },
  {
    id: 'parse-error',
    source: 'parse_code',
    target: 'handle_error',
    type: 'error',
    label: 'Error'
  },
  {
    id: 'static-error',
    source: 'static_analysis',
    target: 'handle_error',
    type: 'error',
    label: 'Error'
  },
  {
    id: 'impact-error',
    source: 'impact_analysis',
    target: 'handle_error',
    type: 'error',
    label: 'Error'
  },
  {
    id: 'llm-error',
    source: 'llm_analysis',
    target: 'handle_error',
    type: 'error',
    label: 'Error'
  },
  {
    id: 'project-error',
    source: 'project_scanning',
    target: 'handle_error',
    type: 'error',
    label: 'Error'
  },
  {
    id: 'report-error',
    source: 'reporting',
    target: 'handle_error',
    type: 'error',
    label: 'Error'
  },
  {
    id: 'error-end',
    source: 'handle_error',
    target: 'end',
    type: 'default'
  }
];

/**
 * Generate workflow state from scan status and current step
 */
export function generateWorkflowFromScanStatus(
  scanStatus: any,
  scanId: string
): WorkflowState {
  const currentStep = scanStatus?.current_step || 'start_scan';
  const isRunning = scanStatus?.status === 'running' || scanStatus?.status === 'in_progress';
  const scanType = scanStatus?.scan_type || 'project';
  const repository = scanStatus?.repository || '';

  // Generate nodes with current status
  const nodes: AgentNode[] = Object.entries(AGENT_MAPPING).map(([agentId, config]) => ({
    id: agentId,
    name: agentId,
    label: config.label,
    type: config.type,
    status: getAgentStatus(agentId, currentStep, scanStatus),
    position: config.position,
    metadata: {
      startTime: getAgentStartTime(agentId, scanStatus),
      endTime: getAgentEndTime(agentId, scanStatus),
      duration: getAgentDuration(agentId, scanStatus),
      errorMessage: getAgentError(agentId, scanStatus),
      logs: getAgentLogs(agentId, scanStatus),
    }
  }));

  // Filter edges based on scan type
  const edges = WORKFLOW_EDGES.filter(edge => {
    // For PR scans, hide project_scanning edges
    if (scanType === 'pr' && (
      edge.source === 'project_scanning' || 
      edge.target === 'project_scanning' ||
      edge.id === 'static-project'
    )) {
      return false;
    }
    
    // For project scans, hide impact_analysis edges  
    if (scanType === 'project' && (
      edge.source === 'impact_analysis' || 
      edge.target === 'impact_analysis' ||
      edge.id === 'static-impact'
    )) {
      return false;
    }
    
    return true;
  });

  // Calculate progress
  const totalSteps = nodes.filter(n => n.type === 'agent').length;
  const completedSteps = nodes.filter(n => 
    n.type === 'agent' && n.status === 'completed'
  ).length;

  return {
    currentStep,
    nodes,
    edges,
    isRunning,
    startTime: scanStatus?.created_at || scanStatus?.started_at,
    endTime: scanStatus?.completed_at,
    errorMessage: scanStatus?.error_message,
    metadata: {
      scanId,
      scanType: scanType as 'pr' | 'project',
      repository,
      totalSteps,
      completedSteps,
    }
  };
}

/**
 * Determine agent status based on current workflow step
 */
function getAgentStatus(
  agentId: string, 
  currentStep: string, 
  scanStatus: any
): AgentStatus {
  // Check for errors first
  if (scanStatus?.error_message && currentStep === 'handle_error') {
    if (agentId === 'handle_error') return 'running';
    if (agentId === currentStep) return 'error';
  }

  // Handle completed workflow
  if (scanStatus?.status === 'completed' || currentStep === 'completed') {
    if (agentId === 'end') return 'completed';
    // All agents before end should be completed
    const agentOrder = Object.keys(AGENT_MAPPING);
    const currentIndex = agentOrder.indexOf(currentStep);
    const agentIndex = agentOrder.indexOf(agentId);
    
    if (agentIndex < currentIndex || currentStep === 'completed') {
      return 'completed';
    }
  }

  // Handle current running step
  if (agentId === currentStep) {
    return 'running';
  }

  // Handle completed steps
  const agentOrder = Object.keys(AGENT_MAPPING);
  const currentIndex = agentOrder.indexOf(currentStep);
  const agentIndex = agentOrder.indexOf(agentId);

  if (agentIndex < currentIndex) {
    return 'completed';
  }

  // Handle waiting/idle steps
  if (agentIndex === currentIndex + 1) {
    return 'waiting';
  }

  return 'idle';
}

/**
 * Extract agent start time from scan status
 */
function getAgentStartTime(agentId: string, scanStatus: any): string | undefined {
  // This would be populated from actual orchestrator logs/metadata
  return scanStatus?.started_at;
}

/**
 * Extract agent end time from scan status
 */
function getAgentEndTime(agentId: string, scanStatus: any): string | undefined {
  // This would be populated from actual orchestrator logs/metadata
  return scanStatus?.completed_at;
}

/**
 * Calculate agent duration from scan status
 */
function getAgentDuration(agentId: string, scanStatus: any): number | undefined {
  // This would be calculated from actual orchestrator timing data
  return scanStatus?.duration_seconds ? scanStatus.duration_seconds * 1000 : undefined;
}

/**
 * Extract agent error message from scan status
 */
function getAgentError(agentId: string, scanStatus: any): string | undefined {
  if (scanStatus?.error_message && scanStatus?.current_step === agentId) {
    return scanStatus.error_message;
  }
  return undefined;
}

/**
 * Extract agent logs from scan status
 */
function getAgentLogs(agentId: string, scanStatus: any): string[] {
  // This would be populated from actual orchestrator logs
  // For now, return empty array
  return [];
}

/**
 * Create a mock workflow for demo purposes
 */
export function createMockWorkflow(scanId: string): WorkflowState {
  const mockScanStatus = {
    scan_id: scanId,
    status: 'running',
    current_step: 'llm_analysis',
    scan_type: 'pr',
    repository: 'example/test-repo',
    created_at: new Date(Date.now() - 300000).toISOString(), // 5 minutes ago
    started_at: new Date(Date.now() - 240000).toISOString(),  // 4 minutes ago
    duration_seconds: 240,
  };

  return generateWorkflowFromScanStatus(mockScanStatus, scanId);
}

/**
 * Generate animated edges for running workflow
 */
export function getAnimatedEdges(workflowState: WorkflowState): string[] {
  if (!workflowState.isRunning) return [];
  
  const currentNode = workflowState.nodes.find(n => n.id === workflowState.currentStep);
  if (!currentNode) return [];

  // Find edges leading to current running node
  return workflowState.edges
    .filter(edge => edge.target === workflowState.currentStep)
    .map(edge => edge.id);
} 