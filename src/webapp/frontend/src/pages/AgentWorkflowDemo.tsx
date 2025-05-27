/**
 * Simple Agent Workflow Demo Page
 * 
 * Simplified demo page for testing agent workflow visualization
 * without complex WebSocket dependencies.
 */

import React, { useState, useCallback } from 'react';
import { ArrowLeft, Play, RotateCcw } from 'lucide-react';

import { createMockWorkflow } from '../utils/workflowGenerator';
import { WorkflowState, AgentNode } from '../types/agent';

const AgentWorkflowDemo: React.FC = () => {
  const [workflowState, setWorkflowState] = useState<WorkflowState>(() => 
    createMockWorkflow('demo-scan-123')
  );

  const handleNodeClick = useCallback((node: AgentNode) => {
    console.log('Clicked node:', node);
    alert(`Clicked on agent: ${node.label}\nStatus: ${node.status}`);
  }, []);

  const handleReplay = useCallback(() => {
    setWorkflowState(createMockWorkflow('demo-scan-123'));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => window.history.back()}
                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Agent Workflow Demo
                </h1>
                <p className="text-sm text-gray-500">
                  Interactive agent workflow visualization
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={handleReplay}
                className="flex items-center space-x-2 px-3 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Reset</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Placeholder for AgentGraph - will be uncommented once tests pass */}
          <div className="h-96 flex items-center justify-center bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg">
            <div className="text-center">
              <div className="text-6xl mb-4">🔧</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Agent Graph Visualization
              </h3>
              <p className="text-gray-600 mb-4 max-w-md">
                Interactive workflow visualization is being developed. 
                Click the nodes below to test the interaction.
              </p>
              
              {/* Simple node representation */}
              <div className="flex items-center justify-center space-x-4 mt-6">
                {workflowState.nodes.slice(0, 5).map((node) => (
                  <button
                    key={node.id}
                    onClick={() => handleNodeClick(node)}
                    className={`
                      px-4 py-2 rounded-lg border-2 font-medium transition-all
                      ${node.status === 'completed' ? 'bg-green-100 border-green-300 text-green-800' :
                        node.status === 'running' ? 'bg-blue-100 border-blue-300 text-blue-800 animate-pulse' :
                        node.status === 'error' ? 'bg-red-100 border-red-300 text-red-800' :
                        'bg-gray-100 border-gray-300 text-gray-800'}
                    `}
                  >
                    {node.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
          
          {/* Uncomment this when AgentGraph is ready */}
          {/*
          <AgentGraph
            workflowState={workflowState}
            onNodeClick={handleNodeClick}
            onReplay={handleReplay}
            isReplayMode={!workflowState.isRunning}
            height={700}
          />
          */}
        </div>
      </div>

      {/* Workflow Info */}
      <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg p-4 max-w-sm">
        <h4 className="text-sm font-semibold text-gray-800 mb-2">Workflow Status</h4>
        <div className="text-sm space-y-1">
          <div className="flex justify-between">
            <span className="text-gray-600">Current Step:</span>
            <span className="font-medium">{workflowState.currentStep}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Progress:</span>
            <span className="font-medium">
              {workflowState.metadata.completedSteps}/{workflowState.metadata.totalSteps}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Repository:</span>
            <span className="font-medium text-xs">{workflowState.metadata.repository}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentWorkflowDemo; 