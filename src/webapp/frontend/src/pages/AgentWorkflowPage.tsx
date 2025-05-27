/**
 * Agent Workflow Demo Page
 * 
 * Demonstration page for the agent workflow visualization feature.
 * Shows real-time agent status updates and interactive graph.
 */

import React, { useState, useCallback, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Play, 
  Pause, 
  RotateCcw, 
  Wifi, 
  WifiOff,
  AlertCircle
} from 'lucide-react';

import AgentGraph from '../components/AgentGraph';
import useAgentWebSocket from '../hooks/useAgentWebSocket';
import { 
  WorkflowState, 
  AgentNode, 
  AgentStatusUpdate, 
  WorkflowProgressUpdate 
} from '../types/agent';
import { 
  generateWorkflowFromScanStatus,
  createMockWorkflow 
} from '../utils/workflowGenerator';

const AgentWorkflowPage: React.FC = () => {
  const { scanId } = useParams<{ scanId: string }>();
  const navigate = useNavigate();
  
  const [workflowState, setWorkflowState] = useState<WorkflowState | null>(null);
  const [isDemo, setIsDemo] = useState(false);
  const [isDemoRunning, setIsDemoRunning] = useState(false);
  const [demoStep, setDemoStep] = useState(0);

  // Fallback to mock data if no scanId
  useEffect(() => {
    if (!scanId) {
      setIsDemo(true);
      setWorkflowState(createMockWorkflow('demo-scan-123'));
    }
  }, [scanId]);

  // WebSocket for real-time updates
  const {
    isConnected,
    isConnecting,
    error: wsError,
    reconnect,
    connectionState
  } = useAgentWebSocket({
    scanId: scanId || 'demo',
    onAgentStatusUpdate: useCallback((update: AgentStatusUpdate) => {
      setWorkflowState(prev => {
        if (!prev) return prev;
        
        const updatedNodes = prev.nodes.map(node => 
          node.id === update.agentId 
            ? { ...node, status: update.status, metadata: { ...node.metadata, ...update.metadata } }
            : node
        );
        
        return { ...prev, nodes: updatedNodes };
      });
    }, []),
    onWorkflowProgress: useCallback((update: WorkflowProgressUpdate) => {
      setWorkflowState(prev => {
        if (!prev) return prev;
        
        return {
          ...prev,
          currentStep: update.currentStep,
          metadata: {
            ...prev.metadata,
            completedSteps: update.completedSteps,
            totalSteps: update.totalSteps
          }
        };
      });
    }, []),
    onWorkflowComplete: useCallback((finalState: any) => {
      console.log('Workflow completed:', finalState);
      // Handle workflow completion
    }, []),
    autoReconnect: !isDemo,
  });

  // Demo workflow steps
  const demoSteps = [
    'start_scan',
    'fetch_code', 
    'parse_code',
    'static_analysis',
    'impact_analysis',
    'llm_analysis',
    'reporting',
    'end'
  ];

  // Start demo workflow
  const startDemo = useCallback(() => {
    if (!workflowState) return;
    
    setIsDemoRunning(true);
    setDemoStep(0);
    
    // Reset all nodes to idle
    const resetNodes = workflowState.nodes.map(node => ({
      ...node,
      status: 'idle' as const,
      metadata: {
        ...node.metadata,
        startTime: undefined,
        endTime: undefined,
        duration: undefined
      }
    }));
    
    setWorkflowState(prev => prev ? {
      ...prev,
      nodes: resetNodes,
      currentStep: 'start_scan',
      isRunning: true,
      metadata: { ...prev.metadata, completedSteps: 0 }
    } : null);
  }, [workflowState]);

  // Stop demo workflow
  const stopDemo = useCallback(() => {
    setIsDemoRunning(false);
  }, []);

  // Reset demo workflow
  const resetDemo = useCallback(() => {
    setIsDemoRunning(false);
    setDemoStep(0);
    if (workflowState) {
      setWorkflowState(createMockWorkflow('demo-scan-123'));
    }
  }, [workflowState]);

  // Demo step progression
  useEffect(() => {
    if (!isDemoRunning || !workflowState || demoStep >= demoSteps.length) {
      if (demoStep >= demoSteps.length) {
        setIsDemoRunning(false);
        // Mark workflow as completed
        setWorkflowState(prev => prev ? {
          ...prev,
          isRunning: false,
          currentStep: 'completed'
        } : null);
      }
      return;
    }

    const timeout = setTimeout(() => {
      const currentStepId = demoSteps[demoStep];
      const nextStepId = demoSteps[demoStep + 1];
      
      setWorkflowState(prev => {
        if (!prev) return prev;
        
        const updatedNodes = prev.nodes.map(node => {
          if (node.id === currentStepId) {
            return {
              ...node,
              status: 'completed' as const,
              metadata: {
                ...node.metadata,
                endTime: new Date().toISOString(),
                duration: 2000 + Math.random() * 3000 // Random duration
              }
            };
          } else if (node.id === nextStepId) {
            return {
              ...node,
              status: 'running' as const,
              metadata: {
                ...node.metadata,
                startTime: new Date().toISOString()
              }
            };
          }
          return node;
        });
        
        return {
          ...prev,
          nodes: updatedNodes,
          currentStep: nextStepId || currentStepId,
          metadata: {
            ...prev.metadata,
            completedSteps: demoStep + 1
          }
        };
      });
      
      setDemoStep(prev => prev + 1);
    }, 2000 + Math.random() * 2000); // Random timing between 2-4 seconds

    return () => clearTimeout(timeout);
  }, [isDemoRunning, demoStep, workflowState, demoSteps]);

  // Handle node click
  const handleNodeClick = useCallback((node: AgentNode) => {
    console.log('Clicked node:', node);
  }, []);

  // Handle replay
  const handleReplay = useCallback(() => {
    if (isDemo) {
      resetDemo();
      setTimeout(startDemo, 500);
    } else {
      // Handle real workflow replay
      console.log('Replay real workflow');
    }
  }, [isDemo, resetDemo, startDemo]);

  if (!workflowState) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Đang tải workflow...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate(-1)}
                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Agent Workflow Visualization
                </h1>
                <p className="text-sm text-gray-500">
                  {isDemo ? 'Demo Mode' : `Scan ID: ${scanId}`} • {workflowState.metadata.repository}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Connection Status */}
              {!isDemo && (
                <div className="flex items-center space-x-2">
                  {isConnected ? (
                    <div className="flex items-center space-x-1 text-green-600">
                      <Wifi className="w-4 h-4" />
                      <span className="text-sm">Connected</span>
                    </div>
                  ) : isConnecting ? (
                    <div className="flex items-center space-x-1 text-amber-600">
                      <div className="w-4 h-4 border-2 border-amber-600 border-t-transparent rounded-full animate-spin" />
                      <span className="text-sm">Connecting...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-1 text-red-600">
                      <WifiOff className="w-4 h-4" />
                      <span className="text-sm">Disconnected</span>
                      <button
                        onClick={reconnect}
                        className="ml-2 text-sm underline hover:no-underline"
                      >
                        Reconnect
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Demo Controls */}
              {isDemo && (
                <div className="flex items-center space-x-2">
                  {!isDemoRunning ? (
                    <button
                      onClick={startDemo}
                      className="flex items-center space-x-2 px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                    >
                      <Play className="w-4 h-4" />
                      <span>Start Demo</span>
                    </button>
                  ) : (
                    <button
                      onClick={stopDemo}
                      className="flex items-center space-x-2 px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                    >
                      <Pause className="w-4 h-4" />
                      <span>Stop Demo</span>
                    </button>
                  )}
                  
                  <button
                    onClick={resetDemo}
                    className="flex items-center space-x-2 px-3 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                  >
                    <RotateCcw className="w-4 h-4" />
                    <span>Reset</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {wsError && !isDemo && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-400 mr-2" />
            <div>
              <p className="text-sm text-red-700">
                WebSocket Error: {wsError}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="p-6">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <AgentGraph
            workflowState={workflowState}
            onNodeClick={handleNodeClick}
            onReplay={handleReplay}
            isReplayMode={!workflowState.isRunning}
            height={700}

          />
        </div>
      </div>

      {/* Footer Info */}
      <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg p-3 max-w-sm">
        <div className="text-sm space-y-1">
          <div className="flex justify-between">
            <span className="text-gray-600">Mode:</span>
            <span className="font-medium">
              {isDemo ? 'Demo' : 'Live'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Status:</span>
            <span className={`font-medium ${
              workflowState.isRunning ? 'text-blue-600' : 'text-green-600'
            }`}>
              {workflowState.isRunning ? 'Running' : 'Completed'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Progress:</span>
            <span className="font-medium">
              {workflowState.metadata.completedSteps}/{workflowState.metadata.totalSteps}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentWorkflowPage; 