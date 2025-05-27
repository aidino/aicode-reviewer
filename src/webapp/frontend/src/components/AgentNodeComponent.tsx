/**
 * Agent Node Component
 * 
 * Custom React Flow node component for displaying individual agents
 * with status, animations, and interactive features.
 */

import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { 
  Play, 
  Pause, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  SkipForward,
  Loader2,
  ChevronRight
} from 'lucide-react';

import { AgentNode, AgentStatus } from '../types/agent';

interface AgentNodeData extends AgentNode {
  onNodeClick: (node: AgentNode) => void;
}

const AgentNodeComponent: React.FC<NodeProps<AgentNodeData>> = ({ data }) => {
  const { name, label, status, type, metadata, onNodeClick } = data;

  // Status icon mapping
  const getStatusIcon = (status: AgentStatus) => {
    switch (status) {
      case 'idle':
        return <Clock className="w-5 h-5" />;
      case 'waiting':
        return <Pause className="w-5 h-5" />;
      case 'running':
        return <Loader2 className="w-5 h-5 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5" />;
      case 'error':
        return <AlertCircle className="w-5 h-5" />;
      case 'skipped':
        return <SkipForward className="w-5 h-5" />;
      default:
        return <Clock className="w-5 h-5" />;
    }
  };

  // Status color mapping
  const getStatusColor = (status: AgentStatus) => {
    switch (status) {
      case 'idle':
        return 'text-gray-500 bg-gray-50 border-gray-300';
      case 'waiting':
        return 'text-amber-600 bg-amber-50 border-amber-300';
      case 'running':
        return 'text-blue-600 bg-blue-50 border-blue-300';
      case 'completed':
        return 'text-green-600 bg-green-50 border-green-300';
      case 'error':
        return 'text-red-600 bg-red-50 border-red-300';
      case 'skipped':
        return 'text-gray-500 bg-gray-50 border-gray-300';
      default:
        return 'text-gray-500 bg-gray-50 border-gray-300';
    }
  };

  // Node type styles
  const getNodeTypeStyle = (type: AgentNode['type']) => {
    switch (type) {
      case 'start':
        return 'rounded-full';
      case 'end':
        return 'rounded-full';
      case 'conditional':
        return 'transform rotate-45';
      default:
        return 'rounded-lg';
    }
  };

  const handleClick = () => {
    onNodeClick(data);
  };

  const formatDuration = (duration?: number) => {
    if (!duration) return '';
    const seconds = Math.floor(duration / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  };

  return (
    <>
      {/* Input Handle */}
      {type !== 'start' && (
        <Handle
          type="target"
          position={Position.Left}
          className="w-3 h-3 bg-gray-400 border-2 border-white shadow-md"
        />
      )}

      {/* Main Node */}
      <div
        onClick={handleClick}
        className={`
          relative min-w-[180px] max-w-[220px] p-4 border-2 shadow-lg cursor-pointer
          transition-all duration-300 hover:shadow-xl hover:scale-105
          ${getStatusColor(status)}
          ${getNodeTypeStyle(type)}
          ${status === 'running' ? 'animate-pulse' : ''}
        `}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            {getStatusIcon(status)}
            <span className="text-sm font-medium capitalize">
              {status}
            </span>
          </div>
          <ChevronRight className="w-4 h-4 opacity-50" />
        </div>

        {/* Agent Name */}
        <div className="mb-1">
          <h4 className="font-semibold text-gray-900 truncate">
            {label}
          </h4>
          <p className="text-xs text-gray-600 truncate">
            {name}
          </p>
        </div>

        {/* Duration */}
        {metadata?.duration && (
          <div className="text-xs text-gray-500">
            Duration: {formatDuration(metadata.duration)}
          </div>
        )}

        {/* Error indicator */}
        {status === 'error' && metadata?.errorMessage && (
          <div className="mt-2 p-2 bg-red-100 border border-red-200 rounded text-xs text-red-700">
            <span className="font-medium">Error:</span>
            <span className="ml-1 truncate block">
              {metadata.errorMessage}
            </span>
          </div>
        )}

        {/* Progress indicator for running state */}
        {status === 'running' && (
          <div className="mt-2">
            <div className="w-full bg-gray-200 rounded-full h-1">
              <div className="bg-blue-500 h-1 rounded-full animate-pulse" style={{ width: '70%' }} />
            </div>
          </div>
        )}

        {/* Log count indicator */}
        {metadata?.logs && metadata.logs.length > 0 && (
          <div className="absolute top-1 right-1 bg-blue-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {metadata.logs.length}
          </div>
        )}
      </div>

      {/* Output Handle */}
      {type !== 'end' && (
        <Handle
          type="source"
          position={Position.Right}
          className="w-3 h-3 bg-gray-400 border-2 border-white shadow-md"
        />
      )}
    </>
  );
};

export default memo(AgentNodeComponent); 