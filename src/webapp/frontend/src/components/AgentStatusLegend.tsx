/**
 * Agent Status Legend Component
 * 
 * Displays legend for agent status colors and meanings.
 */

import React from 'react';
import { 
  Clock, 
  Pause, 
  CheckCircle, 
  AlertCircle, 
  Loader2, 
  SkipForward 
} from 'lucide-react';

import { AgentStatus } from '../types/agent';

interface StatusItem {
  status: AgentStatus;
  label: string;
  color: string;
  icon: React.ReactNode;
  description: string;
}

const statusItems: StatusItem[] = [
  {
    status: 'idle',
    label: 'Chờ',
    color: '#9CA3AF',
    icon: <Clock className="w-4 h-4" />,
    description: 'Chưa bắt đầu'
  },
  {
    status: 'waiting',
    label: 'Chờ phụ thuộc',
    color: '#F59E0B',
    icon: <Pause className="w-4 h-4" />,
    description: 'Chờ agents khác hoàn thành'
  },
  {
    status: 'running',
    label: 'Đang chạy',
    color: '#3B82F6',
    icon: <Loader2 className="w-4 h-4" />,
    description: 'Đang thực thi'
  },
  {
    status: 'completed',
    label: 'Hoàn thành',
    color: '#10B981',
    icon: <CheckCircle className="w-4 h-4" />,
    description: 'Thực thi thành công'
  },
  {
    status: 'error',
    label: 'Lỗi',
    color: '#EF4444',
    icon: <AlertCircle className="w-4 h-4" />,
    description: 'Gặp lỗi khi thực thi'
  },
  {
    status: 'skipped',
    label: 'Bỏ qua',
    color: '#6B7280',
    icon: <SkipForward className="w-4 h-4" />,
    description: 'Bỏ qua do điều kiện'
  }
];

const AgentStatusLegend: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-4 min-w-[250px]">
      <h4 className="text-sm font-semibold text-gray-800 mb-3">
        Trạng thái Agent
      </h4>
      
      <div className="space-y-2">
        {statusItems.map(({ status, label, color, icon, description }) => (
          <div 
            key={status}
            className="flex items-center space-x-3 group hover:bg-gray-50 p-1 rounded"
          >
            {/* Status dot */}
            <div 
              className="w-3 h-3 rounded-full flex-shrink-0"
              style={{ backgroundColor: color }}
            />
            
            {/* Icon */}
            <div 
              className="flex-shrink-0"
              style={{ color }}
            >
              {icon}
            </div>
            
            {/* Label and description */}
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-900">
                {label}
              </div>
              <div className="text-xs text-gray-500 group-hover:text-gray-700">
                {description}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Additional info */}
      <div className="mt-4 pt-3 border-t border-gray-200">
        <div className="text-xs text-gray-500">
          <div className="flex items-center space-x-1 mb-1">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
            <span>Agent đang chạy sẽ có hiệu ứng nhấp nháy</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-blue-500 rounded-full" />
            <span>Click vào agent để xem chi tiết</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentStatusLegend; 