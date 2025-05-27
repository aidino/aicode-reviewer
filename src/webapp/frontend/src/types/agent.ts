/**
 * Agent Graph Visualization Types
 * 
 * Type definitions for the agent workflow visualization system.
 */

export interface AgentNode {
  id: string;
  name: string;
  label: string;
  type: 'agent' | 'start' | 'end' | 'conditional';
  status: AgentStatus;
  position: { x: number; y: number };
  metadata?: {
    startTime?: string;
    endTime?: string;
    duration?: number;
    errorMessage?: string;
    inputData?: any;
    outputData?: any;
    logs?: string[];
  };
}

export interface AgentEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  type?: 'default' | 'conditional' | 'error';
  animated?: boolean;
}

export type AgentStatus = 
  | 'idle'       // Chưa bắt đầu
  | 'waiting'    // Đang chờ dependencies
  | 'running'    // Đang chạy
  | 'completed' // Hoàn thành thành công
  | 'error'     // Lỗi
  | 'skipped';  // Bỏ qua (conditional flow)

export interface WorkflowState {
  currentStep: string;
  nodes: AgentNode[];
  edges: AgentEdge[];
  isRunning: boolean;
  startTime?: string;
  endTime?: string;
  errorMessage?: string;
  metadata: {
    scanId: string;
    scanType: 'pr' | 'project';
    repository: string;
    totalSteps: number;
    completedSteps: number;
  };
}

export interface AgentLogEntry {
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'debug';
  message: string;
  agentId: string;
  metadata?: any;
}

export interface AgentGraphProps {
  workflowState: WorkflowState;
  onNodeClick?: (node: AgentNode) => void;
  onReplay?: () => void;
  isReplayMode?: boolean;
  height?: number;
  width?: number;
}

// WebSocket message types for real-time updates
export interface AgentUpdateMessage {
  type: 'agent_status_update' | 'workflow_progress' | 'agent_log' | 'workflow_complete';
  scanId: string;
  timestamp: string;
  data: any;
}

export interface AgentStatusUpdate {
  agentId: string;
  status: AgentStatus;
  metadata?: AgentNode['metadata'];
}

export interface WorkflowProgressUpdate {
  currentStep: string;
  completedSteps: number;
  totalSteps: number;
  estimatedTimeRemaining?: number;
} 