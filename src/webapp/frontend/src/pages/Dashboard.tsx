import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, TrendingDown, Activity, AlertCircle, CheckCircle, Clock, Users, Bug, Folder, Brain, Plus, GitBranch, Star, Eye, Edit, Trash2, X } from 'lucide-react';
import Layout from '../components/Layout';
import AddRepositoryModal from '../components/AddRepositoryModal';
import { apiService } from '../services/api';
// import { useSidebar } from '../contexts/SidebarContext'; // No longer needed in Dashboard component
import '../styles/Dashboard.css';
import '../styles/components.css';

// Types for Dashboard API
interface DashboardSummary {
  time_range: string;
  generated_at: string;
  scan_metrics: {
    total_scans: number;
    active_scans: number;
    completed_scans: number;
    failed_scans: number;
    avg_scan_duration: number;
    scans_by_type: Record<string, number>;
    scans_by_status: Record<string, number>;
  };
  findings_metrics: {
    total_findings: number;
    avg_findings_per_scan: number;
    findings_by_severity: Record<string, number>;
    findings_by_category: Record<string, number>;
    top_rules: Array<{
      rule_id: string;
      count: number;
      percentage: number;
    }>;
  };
  repository_metrics: {
    total_repositories: number;
    most_scanned_repos: Array<{
      repository: string;
      scan_count: number;
    }>;
    languages_analyzed: Record<string, number>;
    avg_repository_health: number;
  };
  xai_metrics: {
    total_xai_analyses: number;
    avg_confidence_score: number;
    confidence_distribution: Record<string, number>;
    reasoning_quality_score: number;
  };
  findings_trend: {
    total_findings: Array<{
      date: string;
      value: number;
      count: number;
    }>;
    severity_trends: Record<string, Array<{
      date: string;
      value: number;
      count: number;
    }>>;
    category_trends: Record<string, Array<{
      date: string;
      value: number;
      count: number;
    }>>;
  };
  recent_scans: Array<{
    scan_id: string;
    repository: string;
    status: string;
    timestamp: string;
    findings_count: number;
  }>;
  recent_findings: Array<{
    rule_id: string;
    severity: string;
    message: string;
    timestamp: string;
    scan_id: string;
  }>;
  system_health: {
    status: string;
    scan_success_rate: number;
    avg_response_time: string;
    error_rate: number;
    uptime: string;
    last_updated: string;
  };
}

interface Repository {
  id: string;
  name: string;
  url: string;
  description?: string;
  language: string;
  stars: number;
  forks: number;
  last_scan?: string;
  scan_count: number;
  health_score: number;
  issues_count: number;
  status: 'active' | 'archived' | 'private';
}



// Helper function to format numbers
const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
};

interface SoftStatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: {
    value: string;
    type: 'positive' | 'negative' | 'neutral';
  };
  color?: 'primary' | 'success' | 'warning' | 'info';
}

const SoftStatCard: React.FC<SoftStatCardProps> = ({ 
  title, 
  value, 
  subtitle, 
  icon, 
  trend, 
  color = 'primary' 
}) => {
  const colorMap = {
    primary: 'var(--soft-gradient-primary)',
    success: 'var(--soft-gradient-success)',
    warning: 'var(--soft-gradient-warning)',
    info: 'var(--soft-gradient-info)'
  };

  return (
    <motion.div 
      className="stat-card-soft soft-fade-in"
      whileHover={{ y: -5 }}
      transition={{ duration: 0.2 }}
    >
      <div className="stat-icon" style={{ background: colorMap[color] }}>
        {icon}
      </div>
      <div className="stat-number">{typeof value === 'number' ? formatNumber(value) : value}</div>
      <div className="stat-label">{title}</div>
      {subtitle && (
        <div className="text-xs text-gray-500 mt-1">{subtitle}</div>
      )}
      {trend && (
        <div className={`stat-trend ${trend.type}`}>
          {trend.type === 'positive' ? (
            <TrendingUp size={12} className="inline mr-1" />
          ) : trend.type === 'negative' ? (
            <TrendingDown size={12} className="inline mr-1" />
          ) : (
            <Activity size={12} className="inline mr-1" />
          )}
          {trend.value}
        </div>
      )}
    </motion.div>
  );
};

const Dashboard: React.FC = () => {
  // const { isCollapsed } = useSidebar(); // Removed as Layout handles sidebar spacing
  const [dashboardData, setDashboardData] = useState<DashboardSummary | null>(null);
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('LAST_30_DAYS');
  
  // Repository management states  
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [showAddRepositoryModal, setShowAddRepositoryModal] = useState(false);

  const timeRangeOptions = [
    { value: 'LAST_7_DAYS', label: '7 ngày qua' },
    { value: 'LAST_30_DAYS', label: '30 ngày qua' },
    { value: 'LAST_90_DAYS', label: '90 ngày qua' },
    { value: 'LAST_YEAR', label: '1 năm qua' }
  ];



  const fetchDashboardData = async (timeRange: string) => {
    try {
      // 🔄 Fetch repositories from API
      const repositoriesResponse = await apiService.getRepositories();
      
      if (repositoriesResponse.error) {
        console.error('❌ Failed to fetch repositories:', repositoriesResponse.error);
        throw new Error(repositoriesResponse.error.detail || 'Không thể tải danh sách repositories');
      }

      const repositoriesData = repositoriesResponse.data;
      console.log('✅ Fetched repositories from API:', repositoriesData);

      // Convert API response to frontend Repository format
      const frontendRepositories: Repository[] = repositoriesData.repositories.map((repo: any) => ({
        id: repo.id.toString(),
        name: repo.name,
        url: repo.url,
        description: repo.description,
        language: repo.language || 'Unknown',
        stars: repo.stars || 0,
        forks: repo.forks || 0,
        last_scan: repo.last_synced_at,
        scan_count: 0, // Default for now, later can be calculated from scans
        health_score: 85, // Default health score, later can be calculated
        issues_count: 0, // Default for now, later can be calculated from findings
        status: repo.is_private ? 'private' : 'active'
      }));

      // Mock data for dashboard statistics (will be replaced with real API later)
      const mockDashboardData: DashboardSummary = {
        time_range: timeRange,
        generated_at: new Date().toISOString(),
        scan_metrics: {
          total_scans: 1250,
          active_scans: 5,
          completed_scans: 1200,
          failed_scans: 45,
          avg_scan_duration: 45.2,
          scans_by_type: { 'full': 800, 'pr': 450 },
          scans_by_status: { 'completed': 1200, 'failed': 45, 'running': 5 }
        },
        findings_metrics: {
          total_findings: 8420,
          avg_findings_per_scan: 6.7,
          findings_by_severity: { 'error': 1250, 'warning': 4800, 'info': 2370 },
          findings_by_category: { 'security': 890, 'quality': 3200, 'style': 4330 },
          top_rules: [
            { rule_id: 'unused-variable', count: 542, percentage: 15.2 },
            { rule_id: 'potential-sql-injection', count: 234, percentage: 8.7 },
            { rule_id: 'missing-documentation', count: 189, percentage: 6.4 },
            { rule_id: 'code-complexity', count: 156, percentage: 5.1 },
            { rule_id: 'security-vulnerability', count: 98, percentage: 3.2 }
          ]
        },
        repository_metrics: {
          total_repositories: repositoriesData.total_count, // Use real count from API
          most_scanned_repos: frontendRepositories.slice(0, 5).map(repo => ({
            repository: repo.name,
            scan_count: repo.scan_count
          })),
          languages_analyzed: repositoriesData.summary.languages || {},
          avg_repository_health: 87.5
        },
        xai_metrics: {
          total_xai_analyses: 2340,
          avg_confidence_score: 85.4,
          confidence_distribution: { 'high': 1680, 'medium': 520, 'low': 140 },
          reasoning_quality_score: 92.1
        },
        findings_trend: {
          total_findings: [
            { date: '2025-01-01', value: 156, count: 156 },
            { date: '2025-01-07', value: 189, count: 189 },
            { date: '2025-01-14', value: 143, count: 143 },
            { date: '2025-01-21', value: 167, count: 167 },
            { date: '2025-01-28', value: 198, count: 198 }
          ],
          severity_trends: {},
          category_trends: {}
        },
        recent_scans: [
          { scan_id: 'scan_001', repository: frontendRepositories[0]?.name || 'No repos', status: 'completed', timestamp: '2025-01-28T10:30:00Z', findings_count: 12 },
          { scan_id: 'scan_002', repository: frontendRepositories[1]?.name || 'No repos', status: 'running', timestamp: '2025-01-28T11:15:00Z', findings_count: 0 },
          { scan_id: 'scan_003', repository: frontendRepositories[2]?.name || 'No repos', status: 'completed', timestamp: '2025-01-28T09:45:00Z', findings_count: 8 }
        ],
        recent_findings: [
          { rule_id: 'unused-variable', severity: 'warning', message: 'Variable "tempData" is declared but never used', timestamp: '2025-01-28T10:30:00Z', scan_id: 'scan_001' },
          { rule_id: 'potential-sql-injection', severity: 'error', message: 'Potential SQL injection vulnerability detected in user input handling', timestamp: '2025-01-28T10:28:00Z', scan_id: 'scan_001' }
        ],
        system_health: {
          status: 'healthy',
          scan_success_rate: 94.2,
          avg_response_time: '245ms',
          error_rate: 2.1,
          uptime: '15d 4h 23m',
          last_updated: new Date().toISOString()
        }
      };

      setDashboardData(mockDashboardData);
      setRepositories(frontendRepositories);
      setError(null);
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setError('Không thể tải dữ liệu dashboard. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData(selectedTimeRange);
  }, [selectedTimeRange]);

  const handleTimeRangeChange = (newTimeRange: string) => {
    setSelectedTimeRange(newTimeRange);
  };



  const formatPercentage = (num: number): string => {
    return num.toFixed(1) + '%';
  };

  const getHealthScoreColor = (score: number): string => {
    if (score >= 90) return 'var(--soft-success)';
    if (score >= 75) return 'var(--soft-warning)';
    return 'var(--soft-danger)';
  };

  const getLanguageIcon = (language: string): string => {
    const icons: Record<string, string> = {
      'TypeScript': '🔷',
      'JavaScript': '🟨',
      'Python': '🐍',
      'Java': '☕',
      'Go': '🚀',
      'Rust': '🦀',
      'C++': '⚡',
      'C#': '🔵',
      'PHP': '🐘',
      'Ruby': '💎',
      'Swift': '🦉',
      'Kotlin': '🎯',
      'React': '⚛️'
    };
    return icons[language] || '📝';
  };

  // Repository CRUD functions

  const handleDelete = async (id: string) => {
    if (deleteConfirm !== id) {
      setDeleteConfirm(id);
      return;
    }

    try {
      setRepositories(prev => prev.filter(repo => repo.id !== id));
      setDeleteConfirm(null);
      
      // Update dashboard metrics
      if (dashboardData) {
        setDashboardData(prev => prev ? {
          ...prev,
          repository_metrics: {
            ...prev.repository_metrics,
            total_repositories: prev.repository_metrics.total_repositories - 1
          }
        } : null);
      }
    } catch (error) {
      console.error('Error deleting repository:', error);
    }
  };



  // Navigation handlers for repository actions
  const handleViewRepository = (repo: Repository) => {
    window.location.href = `/repositories/${repo.id}`;
  };

  const handleEditRepository = (repo: Repository) => {
    window.location.href = `/repositories/${repo.id}/edit`;
  };

  const handleAddRepository = () => {
    setShowAddRepositoryModal(true);
  };

  const handleRepositoryAdded = async (newRepo: any) => {
    console.log(`✅ Repository added successfully: ${newRepo.name}`);
    
    // Refetch repositories to ensure we have the latest data
    try {
      const repositoriesResponse = await apiService.getRepositories();
      
      if (repositoriesResponse.error) {
        console.error('❌ Failed to refetch repositories:', repositoriesResponse.error);
        return;
      }

      const repositoriesData = repositoriesResponse.data;
      
      // Convert API response to frontend Repository format
      const frontendRepositories: Repository[] = repositoriesData.repositories.map((repo: any) => ({
        id: repo.id.toString(),
        name: repo.name,
        url: repo.url,
        description: repo.description,
        language: repo.language || 'Unknown',
        stars: repo.stars || 0,
        forks: repo.forks || 0,
        last_scan: repo.last_synced_at,
        scan_count: 0,
        health_score: 85,
        issues_count: 0,
        status: repo.is_private ? 'private' : 'active'
      }));

      setRepositories(frontendRepositories);
      
      // Update dashboard metrics
      if (dashboardData) {
        setDashboardData(prev => prev ? {
          ...prev,
          repository_metrics: {
            ...prev.repository_metrics,
            total_repositories: repositoriesData.total_count,
            languages_analyzed: repositoriesData.summary.languages || {}
          }
        } : null);
      }
      
      console.log(`📊 Updated repository list with ${frontendRepositories.length} repositories`);
    } catch (error) {
      console.error('❌ Error refetching repositories:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center min-h-[60vh]">
            <motion.div 
              className="card-soft p-8 text-center"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
            >
              <div className="loading-spinner mx-auto mb-4"></div>
              <p className="text-gray-600">Đang tải dashboard...</p>
            </motion.div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center min-h-[60vh]">
            <motion.div 
              className="card-soft p-8 text-center max-w-md"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <AlertCircle className="text-red-500 mx-auto mb-4" size={48} />
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Lỗi tải Dashboard</h2>
              <p className="text-gray-600 mb-6">{error}</p>
              <button 
                onClick={() => window.location.reload()} 
                className="btn-soft btn-soft-primary"
              >
                <Activity size={16} />
                Thử lại
              </button>
            </motion.div>
          </div>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return null;
  }

  return (
    <Layout showFloatingButton={false}>
      <div className="bg-gray-50 min-h-screen">
        <div className="p-6">
          {/* Simplified Header */}
          <motion.div 
            className="mb-8"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="flex justify-between items-center mb-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2 soft-gradient-text">
                  Dashboard
                </h1>
                <p className="text-gray-600">Welcome to your AI Code Reviewer dashboard</p>
              </div>
              
              <div className="flex items-center gap-3">
                <select
                  value={selectedTimeRange}
                  onChange={(e) => handleTimeRangeChange(e.target.value)}
                  className="form-soft form-input rounded-lg border-0 bg-white shadow-md"
                >
                  {timeRangeOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </motion.div>

          {/* Statistics Cards */}
          <motion.div 
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-16"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <SoftStatCard
              title="Tổng số Scans"
              value={dashboardData.scan_metrics.total_scans}
              subtitle={`${dashboardData.scan_metrics.completed_scans} hoàn thành`}
              icon={<Activity size={20} />}
              color="primary"
              trend={{
                value: `${dashboardData.scan_metrics.active_scans} đang chạy`,
                type: 'neutral'
              }}
            />
            
            <SoftStatCard
              title="Tổng Issues"
              value={dashboardData.findings_metrics.total_findings}
              subtitle={`${dashboardData.findings_metrics.avg_findings_per_scan} trung bình/scan`}
              icon={<Bug size={20} />}
              color="warning"
              trend={{
                value: "Theo dõi xu hướng",
                type: 'neutral'
              }}
            />
            
            <SoftStatCard
              title="Repositories"
              value={repositories.length}
              subtitle={`Health: ${formatPercentage(dashboardData.repository_metrics.avg_repository_health)}`}
              icon={<Folder size={20} />}
              color="info"
              trend={{
                value: "Tình trạng tốt",
                type: 'positive'
              }}
            />
            
            <SoftStatCard
              title="XAI Confidence"
              value={formatPercentage(dashboardData.xai_metrics.avg_confidence_score)}
              subtitle={`${dashboardData.xai_metrics.total_xai_analyses} analyses`}
              icon={<Brain size={20} />}
              color="success"
              trend={{
                value: "Độ tin cậy cao",
                type: 'positive'
              }}
            />
          </motion.div>

          {/* Spacer để tạo khoảng cách */}
          <div className="h-8 w-full"></div>

          {/* Repositories List */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="pt-8"
          >
            <div className="bg-transparent shadow-none rounded-xl overflow-hidden" style={{ border: 'none' }}>
              <div className="card-soft-header flex justify-between items-center">
                <h4 className="text-lg font-semibold text-gray-900">📁 Repositories</h4>
                <span className="text-sm text-gray-500">{repositories.length} repositories</span>
              </div>
              <div className="card-soft-body">
                <div className="">
                  {repositories.map(repo => (
                    <motion.div 
                      key={repo.id} 
                      className="flex items-center justify-between p-6 border border-gray-100 rounded-xl hover:border-gray-200 hover:shadow-lg transition-all duration-300 bg-white/50"
                      style={{ marginBottom: '10px' }}
                      whileHover={{ y: -2 }}
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="text-xl">{getLanguageIcon(repo.language)}</span>
                          <h5 className="font-semibold text-gray-900 truncate">{repo.name}</h5>
                          <span className={`badge-soft text-xs ${
                            repo.status === 'active' ? 'badge-soft-success' : 
                            repo.status === 'archived' ? 'badge-soft-warning' : 
                            'badge-soft-info'
                          }`}>
                            {repo.status}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3 truncate">{repo.description}</p>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span className="flex items-center gap-1">
                            <Star size={12} />
                            {repo.stars}
                          </span>
                          <span className="flex items-center gap-1">
                            <GitBranch size={12} />
                            {repo.forks}
                          </span>
                          <span className="flex items-center gap-1">
                            <Activity size={12} />
                            {repo.scan_count} scans
                          </span>
                          <span>
                            Cập nhật: {new Date(repo.last_scan || '').toLocaleDateString('vi-VN')}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-4 flex-shrink-0">
                        <div className="text-center">
                          <div className="text-sm font-semibold text-gray-900">{repo.health_score}/100</div>
                          <div className="text-xs text-gray-500">Health</div>
                          <div className="w-20 h-2 bg-gray-100 rounded-full mt-1">
                            <div 
                              className="h-full rounded-full"
                              style={{ 
                                width: `${repo.health_score}%`,
                                backgroundColor: getHealthScoreColor(repo.health_score)
                              }}
                            />
                          </div>
                        </div>
                        <div className="text-center">
                          <div className="text-sm font-semibold text-gray-900">{repo.issues_count}</div>
                          <div className="text-xs text-gray-500">Issues</div>
                        </div>
                        <div className="flex items-center gap-2">
                          <motion.button
                            className="p-2 text-gray-400 hover:text-blue-600 transition-colors duration-200"
                            onClick={() => handleViewRepository(repo)}
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                            title="Xem repository"
                          >
                            <Eye size={20} />
                          </motion.button>
                          <motion.button
                            className="p-2 text-gray-400 hover:text-emerald-600 transition-colors duration-200"
                            onClick={() => handleEditRepository(repo)}
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                            title="Chỉnh sửa repository"
                          >
                            <Edit size={20} />
                          </motion.button>
                          <motion.button
                            className={`p-2 transition-colors duration-200 ${
                              deleteConfirm === repo.id 
                                ? 'text-red-600' 
                                : 'text-gray-400 hover:text-red-600'
                            }`}
                            onClick={() => handleDelete(repo.id)}
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                            title={deleteConfirm === repo.id ? 'Xác nhận xoá' : 'Xoá repository'}
                          >
                            <Trash2 size={20} />
                          </motion.button>
                          {deleteConfirm === repo.id && (
                            <motion.button
                              className="p-2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
                              onClick={() => setDeleteConfirm(null)}
                              initial={{ opacity: 0, scale: 0.8, x: -10 }}
                              animate={{ opacity: 1, scale: 1, x: 0 }}
                              title="Huỷ xoá"
                            >
                              <X size={20} />
                            </motion.button>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>

          {/* Floating Add Repository Button */}
          <motion.button
            className="floating-add-repo-button"
            onClick={handleAddRepository}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'linear-gradient(135deg, #80AF81 0%, #1A5319 100%)';
              e.currentTarget.style.boxShadow = '0 20px 48px rgba(26,83,25, 0.5), 0 8px 16px rgba(26,83,25, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'linear-gradient(135deg, #80AF81 0%, #508D4E 100%)';
              e.currentTarget.style.boxShadow = '0 12px 32px rgba(26,83,25, 0.4), 0 2px 6px rgba(26,83,25, 0.2)';
            }}
            whileHover={{ 
              scale: 1.1,
              y: -4,
              transition: { duration: 0.2, ease: "easeOut" }
            }}
            whileTap={{ scale: 1.05 }}
            initial={{ 
              opacity: 0, 
              scale: 0.8,
              y: 20
            }}
            animate={{ 
              opacity: 1, 
              scale: 1,
              y: 0
            }}
            transition={{ 
              duration: 0.6,
              delay: 0.8,
              type: "spring",
              stiffness: 260,
              damping: 20
            }}
            title="Thêm repository mới"
            style={{
              position: 'fixed',
              bottom: '2rem',
              right: '2rem',
              zIndex: 9999,
              background: 'linear-gradient(135deg, #80AF81 0%, #508D4E 100%)',
              border: 'none',
              width: '72px',
              height: '72px',
              borderRadius: '50%',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '28px',
              fontWeight: 'bold',
              boxShadow: '0 12px 32px rgba(26,83,25, 0.4), 0 2px 6px rgba(26,83,25, 0.2)',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
            }}
          >
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
            }}>
              <Plus size={28} strokeWidth={2.5} />
            </div>
          </motion.button>

          {/* Test: Simple modal without framer-motion */}
          {false && (
            <div style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0,0,0,0.8)',
              zIndex: 9997,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <div style={{
                background: 'white',
                padding: '30px',
                borderRadius: '10px',
                maxWidth: '500px',
                width: '90%'
              }}>
                <h2 style={{ margin: '0 0 20px 0', color: '#000' }}>🧪 Simple React Modal Test</h2>
                <p style={{ color: '#666', marginBottom: '20px' }}>
                  Nếu bạn thấy modal này, nghĩa là React component rendering hoạt động bình thường.
                </p>
                <p style={{ color: '#666', marginBottom: '20px' }}>
                  Vấn đề có thể là với AddRepositoryModal component hoặc framer-motion.
                </p>
                <button 
                  onClick={() => window.location.reload()}
                  style={{
                    background: '#ef4444',
                    color: 'white',
                    padding: '10px 20px',
                    border: 'none',
                    borderRadius: '5px',
                    cursor: 'pointer'
                  }}
                >
                  Reload để tắt test này
                </button>
              </div>
            </div>
          )}

          {/* Test: Always render modal for debug */}
          {false && (
            <AddRepositoryModal
              isOpen={true}
              onClose={() => {
                console.log('🔴 Test modal close requested');
              }}
              onSuccess={handleRepositoryAdded}
            />
          )}

          {showAddRepositoryModal && (
            <AddRepositoryModal
              isOpen={showAddRepositoryModal}
              onClose={() => setShowAddRepositoryModal(false)}
              onSuccess={handleRepositoryAdded}
            />
          )}

        </div>
      </div>
    </Layout>
  );
};

export default Dashboard; 