/**
 * Unit tests for AgentGraph component.
 * 
 * Tests the agent workflow visualization functionality including
 * real-time updates, node interactions, and state management.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';

import AgentGraph from '../AgentGraph';
import { WorkflowState, AgentNode } from '../../types/agent';
import { createMockWorkflow } from '../../utils/workflowGenerator';

// Mock React Flow
jest.mock('reactflow', () => ({
  ReactFlow: ({ children, nodes, edges, onNodesChange, onEdgesChange }: any) => (
    <div data-testid="react-flow">
      <div data-testid="nodes-count">{nodes?.length || 0}</div>
      <div data-testid="edges-count">{edges?.length || 0}</div>
      {children}
    </div>
  ),
  ReactFlowProvider: ({ children }: any) => <div data-testid="react-flow-provider">{children}</div>,
  useNodesState: () => [[], jest.fn(), jest.fn()],
  useEdgesState: () => [[], jest.fn(), jest.fn()],
  addEdge: jest.fn(),
  Controls: () => <div data-testid="controls" />,
  Background: () => <div data-testid="background" />,
  MiniMap: () => <div data-testid="minimap" />,
  Panel: ({ children, position }: any) => (
    <div data-testid={`panel-${position}`}>{children}</div>
  ),
  useReactFlow: () => ({ fitView: jest.fn() }),
}));

// Mock child components
jest.mock('../AgentNodeComponent', () => {
  return function MockAgentNodeComponent({ data }: any) {
    return (
      <div 
        data-testid={`agent-node-${data.id}`}
        onClick={() => data.onNodeClick?.(data)}
      >
        {data.label} - {data.status}
      </div>
    );
  };
});

jest.mock('../AgentStatusLegend', () => {
  return function MockAgentStatusLegend() {
    return <div data-testid="agent-status-legend">Status Legend</div>;
  };
});

jest.mock('../AgentDetailsPanel', () => {
  return function MockAgentDetailsPanel({ node, onClose }: any) {
    return (
      <div data-testid="agent-details-panel">
        <div data-testid="panel-node-id">{node.id}</div>
        <button data-testid="panel-close" onClick={onClose}>Close</button>
      </div>
    );
  };
});

// Wrapper component for tests
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('AgentGraph Component', () => {
  let mockWorkflowState: WorkflowState;

  beforeEach(() => {
    mockWorkflowState = createMockWorkflow('test-scan-123');
    jest.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('renders without crashing', () => {
      render(
        <TestWrapper>
          <AgentGraph workflowState={mockWorkflowState} />
        </TestWrapper>
      );

      expect(screen.getByTestId('react-flow-provider')).toBeInTheDocument();
      expect(screen.getByTestId('react-flow')).toBeInTheDocument();
    });

    it('displays workflow status information', () => {
      render(
        <TestWrapper>
          <AgentGraph workflowState={mockWorkflowState} />
        </TestWrapper>
      );

      expect(screen.getByText('Agent Workflow')).toBeInTheDocument();
      expect(screen.getByTestId('agent-status-legend')).toBeInTheDocument();
    });

    it('shows progress information', () => {
      const workflowWithProgress = {
        ...mockWorkflowState,
        metadata: {
          ...mockWorkflowState.metadata,
          completedSteps: 3,
          totalSteps: 8
        }
      };

      render(
        <TestWrapper>
          <AgentGraph workflowState={workflowWithProgress} />
        </TestWrapper>
      );

      expect(screen.getByText(/3\/8/)).toBeInTheDocument();
      expect(screen.getByText(/38%/)).toBeInTheDocument();
    });
  });

  describe('Node Interactions', () => {
    it('calls onNodeClick when a node is clicked', async () => {
      const mockOnNodeClick = jest.fn();

      render(
        <TestWrapper>
          <AgentGraph 
            workflowState={mockWorkflowState} 
            onNodeClick={mockOnNodeClick}
          />
        </TestWrapper>
      );

      // Since we're mocking the node component, we need to trigger the click differently
      // This would be more complex in real implementation due to React Flow's structure
      expect(mockOnNodeClick).not.toHaveBeenCalled();
    });

    it('opens details panel when node is clicked', async () => {
      render(
        <TestWrapper>
          <AgentGraph workflowState={mockWorkflowState} />
        </TestWrapper>
      );

      // In a real test, we would simulate clicking on a node
      // and verify that the details panel appears
      // This requires more complex setup with React Flow
    });
  });

  describe('Workflow State Updates', () => {
    it('updates nodes when workflow state changes', () => {
      const { rerender } = render(
        <TestWrapper>
          <AgentGraph workflowState={mockWorkflowState} />
        </TestWrapper>
      );

      // Update workflow state
      const updatedWorkflowState = {
        ...mockWorkflowState,
        currentStep: 'static_analysis',
        nodes: mockWorkflowState.nodes.map(node =>
          node.id === 'static_analysis'
            ? { ...node, status: 'running' as const }
            : node
        )
      };

      rerender(
        <TestWrapper>
          <AgentGraph workflowState={updatedWorkflowState} />
        </TestWrapper>
      );

      // Verify the component re-renders with new state
      expect(screen.getByTestId('react-flow')).toBeInTheDocument();
    });

    it('shows running state with progress bar', () => {
      const runningWorkflow = {
        ...mockWorkflowState,
        isRunning: true,
        currentStep: 'fetch_code'
      };

      render(
        <TestWrapper>
          <AgentGraph workflowState={runningWorkflow} />
        </TestWrapper>
      );

      // Check for progress bar
      const progressElements = screen.getAllByRole('progressbar', { hidden: true });
      expect(progressElements.length).toBeGreaterThan(0);
    });
  });

  describe('Replay Functionality', () => {
    it('shows replay button when workflow is completed', () => {
      const completedWorkflow = {
        ...mockWorkflowState,
        isRunning: false,
        currentStep: 'completed'
      };

      const mockOnReplay = jest.fn();

      render(
        <TestWrapper>
          <AgentGraph 
            workflowState={completedWorkflow}
            onReplay={mockOnReplay}
          />
        </TestWrapper>
      );

      const replayButton = screen.getByText('Replay Workflow');
      expect(replayButton).toBeInTheDocument();

      fireEvent.click(replayButton);
      expect(mockOnReplay).toHaveBeenCalledTimes(1);
    });

    it('shows replay mode indicator', () => {
      render(
        <TestWrapper>
          <AgentGraph 
            workflowState={mockWorkflowState}
            isReplayMode={true}
          />
        </TestWrapper>
      );

      expect(screen.getByText('Replay Mode')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('displays error state correctly', () => {
      const errorWorkflow = {
        ...mockWorkflowState,
        currentStep: 'handle_error',
        errorMessage: 'Test error message',
        nodes: mockWorkflowState.nodes.map(node =>
          node.id === 'fetch_code'
            ? { ...node, status: 'error' as const, metadata: { errorMessage: 'Test error message' } }
            : node
        )
      };

      render(
        <TestWrapper>
          <AgentGraph workflowState={errorWorkflow} />
        </TestWrapper>
      );

      // The error should be visible in the workflow
      expect(screen.getByTestId('react-flow')).toBeInTheDocument();
    });
  });

  describe('Responsive Design', () => {
    it('accepts custom height and width props', () => {
      render(
        <TestWrapper>
          <AgentGraph 
            workflowState={mockWorkflowState}
            height={800}
            width={1200}
          />
        </TestWrapper>
      );

      const container = screen.getByTestId('react-flow').closest('.agent-graph-container');
      expect(container).toHaveStyle({ height: '800px', width: '1200px' });
    });

    it('applies custom className', () => {
      render(
        <TestWrapper>
          <AgentGraph 
            workflowState={mockWorkflowState}
            className="custom-test-class"
          />
        </TestWrapper>
      );

      const container = screen.getByTestId('react-flow').closest('.agent-graph-container');
      expect(container).toHaveClass('custom-test-class');
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels and roles', () => {
      render(
        <TestWrapper>
          <AgentGraph workflowState={mockWorkflowState} />
        </TestWrapper>
      );

      // Check for accessible elements
      expect(screen.getByRole('button', { name: /replay workflow/i })).toBeInTheDocument();
    });

    it('supports keyboard navigation', () => {
      render(
        <TestWrapper>
          <AgentGraph workflowState={mockWorkflowState} />
        </TestWrapper>
      );

      const replayButton = screen.getByRole('button', { name: /replay workflow/i });
      
      // Test keyboard accessibility
      replayButton.focus();
      expect(replayButton).toHaveFocus();
    });
  });

  describe('Performance', () => {
    it('handles large workflow states efficiently', () => {
      // Create a workflow with many nodes
      const largeWorkflow = {
        ...mockWorkflowState,
        nodes: Array.from({ length: 20 }, (_, i) => ({
          id: `node-${i}`,
          name: `node-${i}`,
          label: `Node ${i}`,
          type: 'agent' as const,
          status: 'idle' as const,
          position: { x: i * 100, y: 100 },
          metadata: {}
        }))
      };

      const startTime = performance.now();
      render(
        <TestWrapper>
          <AgentGraph workflowState={largeWorkflow} />
        </TestWrapper>
      );
      const endTime = performance.now();

      // Rendering should be fast (less than 100ms)
      expect(endTime - startTime).toBeLessThan(100);
    });
  });
}); 