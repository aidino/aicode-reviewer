/**
 * Agent Graph Visualization Component
 * 
 * Interactive graph displaying the multi-agent workflow with real-time status updates.
 * Uses React Flow for graph rendering and D3 for animations.
 */

import React, { useCallback, useEffect, useState, useMemo } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Controls,
  Background,
  MiniMap,
  Panel,
  ReactFlowProvider,
  useReactFlow,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { AgentGraphProps, AgentNode, AgentEdge, AgentStatus } from '../types/agent';
import AgentNodeComponent from './AgentNodeComponent';
import AgentStatusLegend from './AgentStatusLegend';
import AgentDetailsPanel from './AgentDetailsPanel';

// Custom node types
const nodeTypes = {
  agentNode: AgentNodeComponent,
};

// Status color mapping
const statusColors = {
  idle: '#9CA3AF',      // Gray
  waiting: '#F59E0B',   // Amber
  running: '#3B82F6',   // Blue
  completed: '#10B981', // Green
  error: '#EF4444',     // Red
  skipped: '#6B7280',   // Gray-500
};

interface AgentGraphInternalProps extends AgentGraphProps {
  className?: string;
}

const AgentGraphInternal: React.FC<AgentGraphInternalProps> = ({
  workflowState,
  onNodeClick,
  onReplay,
  isReplayMode = false,
  height = 600,
  width,
  className = '',
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<AgentNode | null>(null);
  const [showDetailsPanel, setShowDetailsPanel] = useState(false);
  const { fitView } = useReactFlow();

  // Convert AgentNode to React Flow Node
  const convertToFlowNodes = useCallback((agentNodes: AgentNode[]): Node[] => {
    return agentNodes.map((agentNode) => ({
      id: agentNode.id,
      type: 'agentNode',
      position: agentNode.position,
      data: {
        ...agentNode,
        onNodeClick: (node: AgentNode) => {
          setSelectedNode(node);
          setShowDetailsPanel(true);
          onNodeClick?.(node);
        },
      },
      style: {
        border: `2px solid ${statusColors[agentNode.status]}`,
        borderRadius: '12px',
        boxShadow: agentNode.status === 'running' 
          ? `0 0 20px ${statusColors[agentNode.status]}40` 
          : '0 4px 12px rgba(0, 0, 0, 0.15)',
      },
      className: `agent-node agent-node-${agentNode.status}`,
    }));
  }, [onNodeClick]);

  // Convert AgentEdge to React Flow Edge
  const convertToFlowEdges = useCallback((agentEdges: AgentEdge[]): Edge[] => {
    return agentEdges.map((agentEdge) => ({
      id: agentEdge.id,
      source: agentEdge.source,
      target: agentEdge.target,
      label: agentEdge.label,
      type: agentEdge.type === 'conditional' ? 'smoothstep' : 'default',
      animated: agentEdge.animated || false,
      style: {
        stroke: agentEdge.type === 'error' ? statusColors.error : '#64748B',
        strokeWidth: 2,
      },
      labelStyle: {
        fontSize: '12px',
        fontWeight: 'bold',
      },
    }));
  }, []);

  // Update nodes and edges when workflowState changes
  useEffect(() => {
    const flowNodes = convertToFlowNodes(workflowState.nodes);
    const flowEdges = convertToFlowEdges(workflowState.edges);
    
    setNodes(flowNodes);
    setEdges(flowEdges);
    
    // Auto-fit view when workflow starts
    if (workflowState.isRunning) {
      setTimeout(() => fitView({ padding: 0.1 }), 100);
    }
  }, [workflowState, convertToFlowNodes, convertToFlowEdges, setNodes, setEdges, fitView]);

  // Handle edge connection (for future interactive editing)
  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // Close details panel
  const handleCloseDetails = useCallback(() => {
    setShowDetailsPanel(false);
    setSelectedNode(null);
  }, []);

  // Progress percentage
  const progressPercentage = useMemo(() => {
    const { completedSteps, totalSteps } = workflowState.metadata;
    return totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0;
  }, [workflowState.metadata]);

  // Current step status
  const currentStepNode = useMemo(() => {
    return workflowState.nodes.find(node => node.id === workflowState.currentStep);
  }, [workflowState.nodes, workflowState.currentStep]);

  return (
    <div className={`agent-graph-container ${className}`} style={{ height, width }}>
      {/* Header with status and controls */}
      <Panel position="top-left" className="bg-white rounded-lg shadow-lg p-4 max-w-sm">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-800">
            Agent Workflow
          </h3>
          {isReplayMode && (
            <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-md text-sm font-medium">
              Replay Mode
            </span>
          )}
        </div>
        
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Progress:</span>
            <span className="text-sm font-medium text-gray-800">
              {progressPercentage}% ({workflowState.metadata.completedSteps}/{workflowState.metadata.totalSteps})
            </span>
          </div>
          
          {currentStepNode && (
            <div className="flex items-center space-x-2">
              <div 
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: statusColors[currentStepNode.status] }}
              />
              <span className="text-sm text-gray-700">
                {currentStepNode.label}
              </span>
            </div>
          )}
          
          {workflowState.isRunning && (
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progressPercentage}%` }}
              />
            </div>
          )}
        </div>
        
        {onReplay && !workflowState.isRunning && (
          <button
            onClick={onReplay}
            className="mt-3 w-full px-3 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm font-medium"
          >
            Replay Workflow
          </button>
        )}
      </Panel>

      {/* Status Legend */}
      <Panel position="top-right">
        <AgentStatusLegend />
      </Panel>

      {/* React Flow Graph */}
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
        className="bg-gray-50"
      >
        <Background color="#E5E7EB" gap={20} />
        <Controls 
          position="bottom-right"
          className="bg-white shadow-lg rounded-lg"
        />
        <MiniMap 
          position="bottom-left"
          className="bg-white shadow-lg rounded-lg"
          nodeColor={(node) => {
            const agentNode = workflowState.nodes.find(n => n.id === node.id);
            return agentNode ? statusColors[agentNode.status] : '#9CA3AF';
          }}
        />
      </ReactFlow>

      {/* Agent Details Panel */}
      {showDetailsPanel && selectedNode && (
        <AgentDetailsPanel
          node={selectedNode}
          onClose={handleCloseDetails}
          isReplayMode={isReplayMode}
        />
      )}
    </div>
  );
};

// Main component with ReactFlowProvider wrapper
const AgentGraph: React.FC<AgentGraphProps> = (props) => {
  return (
    <ReactFlowProvider>
      <AgentGraphInternal {...props} />
    </ReactFlowProvider>
  );
};

export default AgentGraph; 