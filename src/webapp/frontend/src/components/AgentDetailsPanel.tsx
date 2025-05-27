/**
 * Agent Details Panel Component
 * 
 * Detailed view panel that appears when clicking on an agent node.
 * Shows logs, input/output data, execution metrics, and other metadata.
 */

import React, { useState, useMemo } from 'react';
import { 
  X, 
  Clock, 
  AlertCircle, 
  Info, 
  ChevronDown, 
  ChevronRight,
  Code,
  FileText,
  Activity,
  Filter
} from 'lucide-react';

import { AgentNode, AgentLogEntry } from '../types/agent';

interface AgentDetailsPanelProps {
  node: AgentNode;
  onClose: () => void;
  isReplayMode?: boolean;
}

interface TabConfig {
  id: string;
  label: string;
  icon: React.ReactNode;
  count?: number;
}

const AgentDetailsPanel: React.FC<AgentDetailsPanelProps> = ({
  node,
  onClose,
  isReplayMode = false
}) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']));
  const [logFilter, setLogFilter] = useState<string>('all');

  // Parse logs if they exist
  const logs = useMemo(() => {
    if (!node.metadata?.logs) return [];
    
    // Convert string logs to AgentLogEntry format
    return node.metadata.logs.map((log, index) => {
      try {
        // Try to parse as JSON first
        const parsed = JSON.parse(log);
        return parsed as AgentLogEntry;
      } catch {
        // Fallback to simple string format
        return {
          timestamp: new Date().toISOString(),
          level: 'info' as const,
          message: log,
          agentId: node.id,
        };
      }
    });
  }, [node.metadata?.logs, node.id]);

  // Filter logs based on selected filter
  const filteredLogs = useMemo(() => {
    if (logFilter === 'all') return logs;
    return logs.filter(log => log.level === logFilter);
  }, [logs, logFilter]);

  // Tab configuration
  const tabs: TabConfig[] = [
    {
      id: 'overview',
      label: 'Tổng quan',
      icon: <Info className="w-4 h-4" />,
    },
    {
      id: 'logs',
      label: 'Logs',
      icon: <FileText className="w-4 h-4" />,
      count: logs.length,
    },
    {
      id: 'data',
      label: 'Dữ liệu',
      icon: <Code className="w-4 h-4" />,
    },
    {
      id: 'metrics',
      label: 'Metrics',
      icon: <Activity className="w-4 h-4" />,
    },
  ];

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const formatTimestamp = (timestamp?: string) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleString();
  };

  const formatDuration = (duration?: number) => {
    if (!duration) return 'N/A';
    const seconds = Math.floor(duration / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  };

  const getLogLevelColor = (level: AgentLogEntry['level']) => {
    switch (level) {
      case 'error': return 'text-red-600 bg-red-50';
      case 'warning': return 'text-amber-600 bg-amber-50';
      case 'info': return 'text-blue-600 bg-blue-50';
      case 'debug': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-white shadow-2xl border-l border-gray-200 z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div 
            className="w-4 h-4 rounded-full"
            style={{ 
              backgroundColor: node.status === 'running' ? '#3B82F6' :
                               node.status === 'completed' ? '#10B981' :
                               node.status === 'error' ? '#EF4444' :
                               node.status === 'waiting' ? '#F59E0B' : '#9CA3AF'
            }}
          />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {node.label}
            </h3>
            <p className="text-sm text-gray-500">{node.name}</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors
              ${activeTab === tab.id 
                ? 'border-blue-500 text-blue-600 bg-blue-50' 
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }
            `}
          >
            {tab.icon}
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span className="bg-gray-200 text-gray-700 text-xs rounded-full px-2 py-0.5">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-4">
            {/* Status */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-gray-800 mb-2">Trạng thái</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Hiện tại:</span>
                  <span className={`ml-2 capitalize font-medium ${
                    node.status === 'completed' ? 'text-green-600' :
                    node.status === 'error' ? 'text-red-600' :
                    node.status === 'running' ? 'text-blue-600' :
                    'text-gray-600'
                  }`}>
                    {node.status}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Loại:</span>
                  <span className="ml-2 font-medium">{node.type}</span>
                </div>
              </div>
            </div>

            {/* Timing */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-gray-800 mb-2">Thời gian</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Bắt đầu:</span>
                  <span className="font-mono text-xs">
                    {formatTimestamp(node.metadata?.startTime)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Kết thúc:</span>
                  <span className="font-mono text-xs">
                    {formatTimestamp(node.metadata?.endTime)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Thời lượng:</span>
                  <span className="font-medium">
                    {formatDuration(node.metadata?.duration)}
                  </span>
                </div>
              </div>
            </div>

            {/* Error Details */}
            {node.status === 'error' && node.metadata?.errorMessage && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <AlertCircle className="w-4 h-4 text-red-500" />
                  <h4 className="text-sm font-semibold text-red-800">Lỗi</h4>
                </div>
                <p className="text-sm text-red-700 font-mono">
                  {node.metadata.errorMessage}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Logs Tab */}
        {activeTab === 'logs' && (
          <div className="space-y-4">
            {/* Log Filter */}
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <select
                value={logFilter}
                onChange={(e) => setLogFilter(e.target.value)}
                className="text-sm border border-gray-300 rounded-md px-2 py-1"
              >
                <option value="all">Tất cả ({logs.length})</option>
                <option value="error">Lỗi ({logs.filter(l => l.level === 'error').length})</option>
                <option value="warning">Cảnh báo ({logs.filter(l => l.level === 'warning').length})</option>
                <option value="info">Thông tin ({logs.filter(l => l.level === 'info').length})</option>
                <option value="debug">Debug ({logs.filter(l => l.level === 'debug').length})</option>
              </select>
            </div>

            {/* Log Entries */}
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {filteredLogs.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>Không có logs</p>
                </div>
              ) : (
                filteredLogs.map((log, index) => (
                  <div key={index} className={`rounded-lg p-3 border ${getLogLevelColor(log.level)}`}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-medium uppercase">
                        {log.level}
                      </span>
                      <span className="text-xs font-mono">
                        {formatTimestamp(log.timestamp)}
                      </span>
                    </div>
                    <p className="text-sm break-words">
                      {log.message}
                    </p>
                    {log.metadata && (
                      <details className="mt-2">
                        <summary className="text-xs cursor-pointer">Metadata</summary>
                        <pre className="text-xs mt-1 overflow-x-auto">
                          {JSON.stringify(log.metadata, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Data Tab */}
        {activeTab === 'data' && (
          <div className="space-y-4">
            {/* Input Data */}
            <div>
              <button
                onClick={() => toggleSection('input')}
                className="flex items-center space-x-2 w-full text-left"
              >
                {expandedSections.has('input') ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )}
                <h4 className="text-sm font-semibold text-gray-800">Dữ liệu đầu vào</h4>
              </button>
              
              {expandedSections.has('input') && (
                <div className="mt-2 bg-gray-50 rounded-lg p-3">
                  {node.metadata?.inputData ? (
                    <pre className="text-xs overflow-x-auto">
                      {JSON.stringify(node.metadata.inputData, null, 2)}
                    </pre>
                  ) : (
                    <p className="text-sm text-gray-500">Không có dữ liệu đầu vào</p>
                  )}
                </div>
              )}
            </div>

            {/* Output Data */}
            <div>
              <button
                onClick={() => toggleSection('output')}
                className="flex items-center space-x-2 w-full text-left"
              >
                {expandedSections.has('output') ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )}
                <h4 className="text-sm font-semibold text-gray-800">Dữ liệu đầu ra</h4>
              </button>
              
              {expandedSections.has('output') && (
                <div className="mt-2 bg-gray-50 rounded-lg p-3">
                  {node.metadata?.outputData ? (
                    <pre className="text-xs overflow-x-auto">
                      {JSON.stringify(node.metadata.outputData, null, 2)}
                    </pre>
                  ) : (
                    <p className="text-sm text-gray-500">Chưa có dữ liệu đầu ra</p>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Metrics Tab */}
        {activeTab === 'metrics' && (
          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-gray-800 mb-3">Performance Metrics</h4>
              <div className="grid grid-cols-1 gap-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Memory Usage:</span>
                  <span className="font-medium">N/A</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">CPU Usage:</span>
                  <span className="font-medium">N/A</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">API Calls:</span>
                  <span className="font-medium">N/A</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Cache Hits:</span>
                  <span className="font-medium">N/A</span>
                </div>
              </div>
            </div>
            
            <div className="text-xs text-gray-500 text-center py-4">
              Metrics sẽ được cập nhật trong phiên bản tiếp theo
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      {isReplayMode && (
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center space-x-2 text-sm text-blue-600">
            <Clock className="w-4 h-4" />
            <span>Đang ở chế độ xem lại workflow</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentDetailsPanel; 