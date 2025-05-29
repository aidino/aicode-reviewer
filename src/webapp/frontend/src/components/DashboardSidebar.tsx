import React from 'react';
import { motion } from 'framer-motion';
import {
  BarChart3,
  History,
  Settings,
  ChevronLeft,
  ChevronRight,
  FileText,
  TrendingUp,
  Shield,
  Zap,
  User,
  LogOut
} from 'lucide-react';
import { useSidebar } from '../contexts/SidebarContext';
import { useAuth } from '../contexts/AuthContext';

interface SidebarProps {
  className?: string;
  healthData?: {
    status: string;
    uptime: string;
    version: string;
  } | null;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  href?: string;
  onClick?: () => void;
  badge?: string;
  color?: string;
}

const DashboardSidebar: React.FC<SidebarProps> = ({ className = '', healthData }) => {
  const { isCollapsed, toggleSidebar } = useSidebar();
  const { user, logout } = useAuth();

  const navigationItems: NavItem[] = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: <BarChart3 size={20} />,
      href: '/dashboard',
      color: 'var(--soft-primary)'
    },
    {
      id: 'scan-history',
      label: 'Lịch sử Scan',
      icon: <History size={20} />,
      href: '/scans',
      badge: 'Hot',
      color: 'var(--soft-info)'
    },
    {
      id: 'reports',
      label: 'Báo cáo',
      icon: <FileText size={20} />,
      href: '/reports',
      color: 'var(--soft-success)'
    },
    {
      id: 'analytics',
      label: 'Phân tích',
      icon: <TrendingUp size={20} />,
      href: '/analytics',
      color: 'var(--soft-warning)'
    },
    {
      id: 'security',
      label: 'Bảo mật',
      icon: <Shield size={20} />,
      href: '/security',
      color: 'var(--soft-danger)'
    }
  ];

  const settingsItems: NavItem[] = [
    {
      id: 'profile',
      label: 'Hồ sơ',
      icon: <User size={20} />,
      href: '/profile',
      color: 'var(--soft-info)'
    },
    {
      id: 'settings',
      label: 'Cài đặt',
      icon: <Settings size={20} />,
      href: '/settings',
      color: '#6b7280'
    },
    {
      id: 'logout',
      label: 'Đăng xuất',
      icon: <LogOut size={20} />,
      onClick: logout,
      color: 'var(--soft-danger)'
    }
  ];

  const handleNavigation = (item: NavItem) => {
    if (item.onClick) {
      item.onClick();
    } else if (item.href) {
      window.location.href = item.href;
    }
  };

  const getHealthStatusColor = (status: string): string => {
    switch (status?.toLowerCase()) {
      case 'healthy': return 'var(--soft-success)';
      case 'warning': return 'var(--soft-warning)';
      case 'error': return 'var(--soft-danger)';
      default: return '#6b7280';
    }
  };

  return (
    <motion.div
      className={`dashboard-sidebar ${isCollapsed ? 'collapsed' : ''} ${className}`}
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="sidebar-header">
        {!isCollapsed && (
          <motion.div
            className="sidebar-title"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Zap className="sidebar-logo" size={24} />
            <span>AI Reviewer</span>
          </motion.div>
        )}

        <motion.button
          className="sidebar-toggle"
          onClick={toggleSidebar}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </motion.button>
      </div>

      {/* Navigation */}
      <div className="sidebar-nav">
        <div className="nav-section">
          {!isCollapsed && (
            <motion.h3
              className="nav-section-title"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              Navigation
            </motion.h3>
          )}

          <div className="nav-items">
            {navigationItems.map((item, index) => (
              <motion.button
                key={item.id}
                className="nav-item"
                onClick={() => handleNavigation(item)}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.1 * index + 0.2 }}
                whileHover={{
                  x: 5,
                  transition: { duration: 0.2 }
                }}
                whileTap={{ scale: 0.98 }}
              >
                <div
                  className="nav-item-icon"
                  style={{ color: item.color }}
                >
                  {item.icon}
                </div>

                {!isCollapsed && (
                  <>
                    <span className="nav-item-label">{item.label}</span>
                    {item.badge && (
                      <span className="nav-item-badge">{item.badge}</span>
                    )}
                  </>
                )}
              </motion.button>
            ))}
          </div>
        </div>

        {/* Settings Section */}
        <div className="nav-section">
          {!isCollapsed && (
            <motion.h3
              className="nav-section-title"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              Settings
            </motion.h3>
          )}

          <div className="nav-items">
            {settingsItems.map((item, index) => (
              <motion.button
                key={item.id}
                className="nav-item"
                onClick={() => handleNavigation(item)}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.1 * index + 0.6 }}
                whileHover={{
                  x: 5,
                  transition: { duration: 0.2 }
                }}
                whileTap={{ scale: 0.98 }}
              >
                <div
                  className="nav-item-icon"
                  style={{ color: item.color }}
                >
                  {item.icon}
                </div>

                {!isCollapsed && (
                  <span className="nav-item-label">{item.label}</span>
                )}
              </motion.button>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      {!isCollapsed && (
        <motion.div
          className="sidebar-footer"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <div className="footer-info">
            {/* User Information */}
            {user && (
              <div className="footer-user">
                <div className="flex items-center gap-3 mb-3 p-3 bg-white/50 rounded-xl border border-gray-200/50">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                    {user.username && user.username.length > 0 ? user.username.charAt(0).toUpperCase() : '?'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-900 truncate">
                      {user.profile?.full_name || user.username || 'Anonymous'}
                    </div>
                    <div className="text-xs text-gray-500 truncate">
                      {user.email || 'No email'}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* System Health */}
            {healthData && (
              <div className="footer-health">
                <div className="flex items-center gap-2 mb-2">
                  <div 
                    className="status-indicator"
                    style={{ backgroundColor: getHealthStatusColor(healthData.status) }}
                  ></div>
                  <span className="footer-health-label">
                    System: {healthData.status ? healthData.status.toUpperCase() : 'UNKNOWN'}
                  </span>
                </div>
                <div className="footer-health-details">
                  <div className="text-xs">Uptime: {healthData.uptime}</div>
                  <div className="text-xs">Version: {healthData.version}</div>
                </div>
              </div>
            )}
            
            <div className="footer-version">AI Code Reviewer v2.1.0</div>
            <div className="footer-status">
              <div className="status-indicator status-online"></div>
              <span>Backend Online</span>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default DashboardSidebar; 