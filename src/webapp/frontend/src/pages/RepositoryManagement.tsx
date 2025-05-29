import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Save, 
  Settings, 
  GitBranch, 
  Eye, 
  Edit, 
  Trash2, 
  Plus, 
  Brain,
  Shield,
  Zap,
  Bell,
  Code,
  Database,
  RefreshCw
} from 'lucide-react';
import Layout from '../components/Layout';
import { apiService } from '../services/api';

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
  // New fields from API
  avatar_url?: string;
  default_branch?: string;
  is_private: boolean;
  owner_id: number;
  created_at: string;
  updated_at: string;
  last_synced_at?: string;
  cached_path?: string;
  last_commit_hash?: string;
  cache_expires_at?: string;
  cache_size_mb?: number;
  auto_sync_enabled?: boolean;
  // Configuration settings
  config: {
    llm_model: string;
    scan_frequency: string;
    auto_fix: boolean;
    notification_enabled: boolean;
    security_scan: boolean;
    code_quality_check: boolean;
    dependency_scan: boolean;
    custom_rules: string[];
  };
}

const RepositoryManagement: React.FC = () => {
  const { id, action } = useParams<{ id: string; action?: string }>();
  const navigate = useNavigate();
  const [repository, setRepository] = useState<Repository | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  
  const isNewRepo = id === 'new';
  const isViewMode = action === undefined && !isNewRepo;
  const isEditMode = action === 'edit' || isNewRepo;

  useEffect(() => {
    if (isNewRepo) {
      setRepository({
        id: '',
        name: '',
        url: '',
        description: '',
        language: 'JavaScript',
        stars: 0,
        forks: 0,
        scan_count: 0,
        health_score: 0,
        issues_count: 0,
        status: 'active',
        is_private: false,
        owner_id: 0,
        created_at: '',
        updated_at: '',
        config: {
          llm_model: 'gpt-4',
          scan_frequency: 'daily',
          auto_fix: false,
          notification_enabled: true,
          security_scan: true,
          code_quality_check: true,
          dependency_scan: true,
          custom_rules: []
        }
      });
      setLoading(false);
    } else {
      fetchRepositoryDetail();
    }
  }, [id, isNewRepo]);

  const fetchRepositoryDetail = async () => {
    if (!id) return;
    
    setLoading(true);
    setError(null);
    
    try {
      console.log(`🔍 Fetching repository detail for ID: ${id}`);
      const response = await apiService.getRepositoryDetail(id);
      
      if (response.error) {
        console.error('❌ Failed to fetch repository detail:', response.error);
        setError(response.error.detail || 'Không thể tải thông tin repository');
        setRepository(null);
      } else {
        console.log('✅ Repository detail fetched:', response.data);
        
        // Convert API response to frontend Repository format
        const apiRepo = response.data;
        const frontendRepo: Repository = {
          id: apiRepo.id.toString(),
          name: apiRepo.name,
          url: apiRepo.url,
          description: apiRepo.description,
          language: apiRepo.language || 'Unknown',
          stars: apiRepo.stars || 0,
          forks: apiRepo.forks || 0,
          last_scan: apiRepo.last_synced_at,
          scan_count: 0, // TODO: Calculate from actual scans
          health_score: 85, // TODO: Calculate from actual metrics
          issues_count: 0, // TODO: Calculate from actual findings
          status: apiRepo.is_private ? 'private' : 'active',
          // API fields
          avatar_url: apiRepo.avatar_url,
          default_branch: apiRepo.default_branch,
          is_private: apiRepo.is_private,
          owner_id: apiRepo.owner_id,
          created_at: apiRepo.created_at,
          updated_at: apiRepo.updated_at,
          last_synced_at: apiRepo.last_synced_at,
          cached_path: apiRepo.cached_path,
          last_commit_hash: apiRepo.last_commit_hash,
          cache_expires_at: apiRepo.cache_expires_at,
          cache_size_mb: apiRepo.cache_size_mb,
          auto_sync_enabled: apiRepo.auto_sync_enabled,
          config: {
            llm_model: 'gpt-4',
            scan_frequency: 'daily',
            auto_fix: false,
            notification_enabled: true,
            security_scan: true,
            code_quality_check: true,
            dependency_scan: true,
            custom_rules: []
          }
        };
        
        setRepository(frontendRepo);
      }
    } catch (err) {
      console.error('💥 Error fetching repository detail:', err);
      setError('Lỗi không mong đợi khi tải thông tin repository');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateLatest = async () => {
    if (!repository || !id) return;
    
    setUpdating(true);
    setError(null);
    
    try {
      console.log(`🔄 Updating latest for repository ID: ${id}`);
      const response = await apiService.updateRepositoryLatest(id);
      
      if (response.error) {
        console.error('❌ Failed to update repository:', response.error);
        setError(response.error.detail || 'Không thể cập nhật repository');
      } else {
        console.log('✅ Repository updated successfully:', response.data);
        
        // Refresh the repository data
        await fetchRepositoryDetail();
      }
    } catch (err) {
      console.error('💥 Error updating repository:', err);
      setError('Lỗi không mong đợi khi cập nhật repository');
    } finally {
      setUpdating(false);
    }
  };

  const handleSave = async () => {
    if (!repository) return;
    setSaving(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (isNewRepo) {
        navigate('/dashboard');
      } else {
        setIsEditing(false);
      }
    } catch (error) {
      console.error('Error saving repository:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    if (!repository) return;
    
    if (field.startsWith('config.')) {
      const configField = field.replace('config.', '');
      setRepository(prev => prev ? {
        ...prev,
        config: {
          ...prev.config,
          [configField]: value
        }
      } : null);
    } else {
      setRepository(prev => prev ? {
        ...prev,
        [field]: value
      } : null);
    }
  };

  const languages = [
    'JavaScript',
    'TypeScript', 
    'Python',
    'Java',
    'Go',
    'Rust',
    'C++',
    'C#',
    'PHP',
    'Ruby',
    'Swift',
    'Kotlin'
  ];

  const llmModels = [
    'gpt-4',
    'gpt-3.5-turbo',
    'claude-3-opus',
    'claude-3-sonnet',
    'gemini-pro'
  ];

  const scanFrequencies = [
    { value: 'hourly', label: 'Mỗi giờ' },
    { value: 'daily', label: 'Hàng ngày' },
    { value: 'weekly', label: 'Hàng tuần' },
    { value: 'monthly', label: 'Hàng tháng' },
    { value: 'manual', label: 'Thủ công' }
  ];

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
      'Kotlin': '🎯'
    };
    return icons[language] || '📝';
  };

  if (loading) {
    return (
      <Layout showFloatingButton={false}>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <motion.div
            className="card-soft p-8 text-center"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <div className="loading-spinner mx-auto mb-4"></div>
            <p className="text-gray-600">Đang tải thông tin repository...</p>
          </motion.div>
        </div>
      </Layout>
    );
  }

  if (!repository) {
    return (
      <Layout showFloatingButton={false}>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <motion.div
            className="card-soft p-8 text-center max-w-md"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h2 className="text-xl font-semibold text-gray-900 mb-3">
              {error ? 'Lỗi tải Repository' : 'Repository không tìm thấy'}
            </h2>
            {error && (
              <p className="text-red-600 mb-4">{error}</p>
            )}
            <div className="flex gap-3 justify-center">
              <button 
                onClick={() => navigate('/dashboard')}
                className="btn-soft btn-soft-outline"
              >
                <ArrowLeft size={16} />
                Quay lại Dashboard
              </button>
              {error && (
                <button 
                  onClick={() => fetchRepositoryDetail()}
                  className="btn-soft btn-soft-primary"
                >
                  <RefreshCw size={16} />
                  Thử lại
                </button>
              )}
            </div>
          </motion.div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout showFloatingButton={false}>
      <div className="min-h-screen bg-gray-50">
        <div className="p-6">
          {/* Error Banner */}
          {error && (
            <motion.div
              className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="text-red-600">⚠️</div>
                  <span className="text-red-800">{error}</span>
                </div>
                <button
                  onClick={() => setError(null)}
                  className="text-red-600 hover:text-red-800"
                >
                  ✕
                </button>
              </div>
            </motion.div>
          )}

          {/* Header */}
          <motion.div
            className="mb-8"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => navigate('/dashboard')}
                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <ArrowLeft size={24} />
                </button>
                
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-2 soft-gradient-text">
                    {isNewRepo ? '➕ Thêm Repository Mới' : 
                     isEditMode ? '✏️ Chỉnh sửa Repository' : 
                     '👁️ Thông tin Repository'}
                  </h1>
                  <p className="text-gray-600">
                    {isNewRepo ? 'Thiết lập repository mới cho AI Code Reviewer' :
                     isEditMode ? 'Cập nhật thông tin và cấu hình' :
                     'Xem thông tin chi tiết và cấu hình'}
                  </p>
                  {/* Repository sync info */}
                  {!isNewRepo && repository.last_synced_at && (
                    <p className="text-sm text-gray-500 mt-1">
                      🔄 Cập nhật lần cuối: {new Date(repository.last_synced_at).toLocaleString('vi-VN')}
                      {repository.cached_path && ` • 📁 Cached (${repository.cache_size_mb?.toFixed(1) || 0}MB)`}
                    </p>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-3">
                {!isNewRepo && isViewMode && (
                  <>
                    <button
                      onClick={handleUpdateLatest}
                      disabled={updating}
                      className="btn-soft btn-soft-success flex items-center gap-2"
                    >
                      {updating ? (
                        <>
                          <div className="loading-spinner w-4 h-4"></div>
                          Đang cập nhật...
                        </>
                      ) : (
                        <>
                          <RefreshCw size={16} />
                          Update Latest
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => navigate(`/repositories/${id}/edit`)}
                      className="btn-soft btn-soft-outline"
                    >
                      <Edit size={16} />
                      Chỉnh sửa
                    </button>
                  </>
                )}
                
                {isEditMode && (
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="btn-soft btn-soft-primary flex items-center gap-2"
                  >
                    {saving ? (
                      <>
                        <div className="loading-spinner w-4 h-4"></div>
                        Đang lưu...
                      </>
                    ) : (
                      <>
                        <Save size={16} />
                        {isNewRepo ? 'Tạo Repository' : 'Lưu thay đổi'}
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Information */}
            <div className="lg:col-span-2 space-y-6">
              {/* Repository Statistics - Only show in view mode */}
              {isViewMode && (
                <motion.div
                  className="grid grid-cols-1 md:grid-cols-4 gap-4"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.1 }}
                >
                  <div className="card-soft text-center">
                    <div className="card-soft-body py-4">
                      <div className="text-2xl font-bold text-blue-600">{repository.health_score}/100</div>
                      <div className="text-sm text-gray-600">Health Score</div>
                    </div>
                  </div>
                  <div className="card-soft text-center">
                    <div className="card-soft-body py-4">
                      <div className="text-2xl font-bold text-green-600">{repository.scan_count}</div>
                      <div className="text-sm text-gray-600">Total Scans</div>
                    </div>
                  </div>
                  <div className="card-soft text-center">
                    <div className="card-soft-body py-4">
                      <div className="text-2xl font-bold text-orange-600">{repository.issues_count}</div>
                      <div className="text-sm text-gray-600">Open Issues</div>
                    </div>
                  </div>
                  <div className="card-soft text-center">
                    <div className="card-soft-body py-4">
                      <div className="text-2xl font-bold text-purple-600">{repository.stars}</div>
                      <div className="text-sm text-gray-600">GitHub Stars</div>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Basic Information */}
              <motion.div
                className="card-soft"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                <div className="card-soft-header">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <GitBranch size={20} />
                    Thông tin cơ bản
                  </h3>
                </div>
                <div className="card-soft-body space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Tên Repository *
                      </label>
                      {isEditMode ? (
                        <input
                          type="text"
                          value={repository.name}
                          onChange={(e) => handleInputChange('name', e.target.value)}
                          className="form-soft form-input w-full"
                          placeholder="e.g., acme/frontend-app"
                        />
                      ) : (
                        <div className="flex items-center gap-2">
                          <span className="text-xl">{getLanguageIcon(repository.language)}</span>
                          <span className="text-lg font-semibold text-gray-900">{repository.name}</span>
                        </div>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        URL Repository *
                      </label>
                      {isEditMode ? (
                        <input
                          type="url"
                          value={repository.url}
                          onChange={(e) => handleInputChange('url', e.target.value)}
                          className="form-soft form-input w-full"
                          placeholder="https://github.com/acme/frontend-app"
                        />
                      ) : (
                        <a 
                          href={repository.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 transition-colors"
                        >
                          {repository.url}
                        </a>
                      )}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Mô tả
                    </label>
                    {isEditMode ? (
                      <textarea
                        value={repository.description || ''}
                        onChange={(e) => handleInputChange('description', e.target.value)}
                        className="form-soft form-input w-full h-20 resize-none"
                        placeholder="Mô tả ngắn gọn về repository..."
                      />
                    ) : (
                      <p className="text-gray-600">{repository.description || 'Chưa có mô tả'}</p>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Ngôn ngữ chính *
                      </label>
                      {isEditMode ? (
                        <select
                          value={repository.language}
                          onChange={(e) => handleInputChange('language', e.target.value)}
                          className="form-soft form-input w-full"
                        >
                          {languages.map(lang => (
                            <option key={lang} value={lang}>
                              {getLanguageIcon(lang)} {lang}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{getLanguageIcon(repository.language)}</span>
                          <span className="text-gray-900">{repository.language}</span>
                        </div>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Trạng thái
                      </label>
                      {isEditMode ? (
                        <select
                          value={repository.status}
                          onChange={(e) => handleInputChange('status', e.target.value)}
                          className="form-soft form-input w-full"
                        >
                          <option value="active">🟢 Active</option>
                          <option value="archived">🟡 Archived</option>
                          <option value="private">🔒 Private</option>
                        </select>
                      ) : (
                        <span className={`badge-soft text-xs ${
                          repository.status === 'active' ? 'badge-soft-success' : 
                          repository.status === 'archived' ? 'badge-soft-warning' : 
                          'badge-soft-info'
                        }`}>
                          {repository.status === 'active' ? '🟢 Active' :
                           repository.status === 'archived' ? '🟡 Archived' : '🔒 Private'}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Additional Repository Information - Only show in view mode */}
                  {isViewMode && (
                    <div className="space-y-4 border-t border-gray-200 pt-6">
                      <h4 className="font-medium text-gray-900">📊 Repository Statistics</h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">Default Branch</span>
                          <span className="text-sm font-medium text-gray-900">
                            {repository.default_branch || 'main'}
                          </span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">Stars</span>
                          <span className="text-sm font-medium text-gray-900">
                            ⭐ {repository.stars.toLocaleString()}
                          </span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">Forks</span>
                          <span className="text-sm font-medium text-gray-900">
                            🍴 {repository.forks.toLocaleString()}
                          </span>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">Visibility</span>
                          <span className={`text-sm font-medium ${repository.is_private ? 'text-orange-600' : 'text-green-600'}`}>
                            {repository.is_private ? '🔒 Private' : '🌍 Public'}
                          </span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">Auto Sync</span>
                          <span className={`text-sm font-medium ${repository.auto_sync_enabled ? 'text-green-600' : 'text-gray-600'}`}>
                            {repository.auto_sync_enabled ? '✅ Enabled' : '⏸️ Disabled'}
                          </span>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-3 bg-gray-50 rounded-lg">
                          <div className="text-sm text-gray-600 mb-1">Tạo lúc</div>
                          <div className="text-sm font-medium text-gray-900">
                            📅 {new Date(repository.created_at).toLocaleString('vi-VN')}
                          </div>
                        </div>
                        <div className="p-3 bg-gray-50 rounded-lg">
                          <div className="text-sm text-gray-600 mb-1">Cập nhật lần cuối</div>
                          <div className="text-sm font-medium text-gray-900">
                            🔄 {new Date(repository.updated_at).toLocaleString('vi-VN')}
                          </div>
                        </div>
                      </div>

                      {repository.cached_path && (
                        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                          <div className="text-sm text-blue-600 mb-1">📁 Smart Cache Information</div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-blue-800">
                            <div>Cache Size: {repository.cache_size_mb?.toFixed(1) || 0}MB</div>
                            <div>Last Commit: {repository.last_commit_hash?.substring(0, 7) || 'N/A'}</div>
                            {repository.cache_expires_at && (
                              <div className="md:col-span-2">
                                Expires: {new Date(repository.cache_expires_at).toLocaleString('vi-VN')}
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </motion.div>

              {/* AI & Scan Configuration */}
              <motion.div
                className="card-soft"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <div className="card-soft-header">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <Brain size={20} />
                    Cấu hình AI & Scan
                  </h3>
                </div>
                <div className="card-soft-body space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        LLM Model
                      </label>
                      {isEditMode ? (
                        <select
                          value={repository.config.llm_model}
                          onChange={(e) => handleInputChange('config.llm_model', e.target.value)}
                          className="form-soft form-input w-full"
                        >
                          {llmModels.map(model => (
                            <option key={model} value={model}>{model}</option>
                          ))}
                        </select>
                      ) : (
                        <div className="flex items-center gap-2">
                          <Zap size={16} className="text-purple-500" />
                          <span className="text-gray-900">{repository.config.llm_model}</span>
                        </div>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Tần suất Scan
                      </label>
                      {isEditMode ? (
                        <select
                          value={repository.config.scan_frequency}
                          onChange={(e) => handleInputChange('config.scan_frequency', e.target.value)}
                          className="form-soft form-input w-full"
                        >
                          {scanFrequencies.map(freq => (
                            <option key={freq.value} value={freq.value}>{freq.label}</option>
                          ))}
                        </select>
                      ) : (
                        <span className="text-gray-900">
                          {scanFrequencies.find(f => f.value === repository.config.scan_frequency)?.label}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Feature Toggles */}
                  <div className="space-y-4">
                    <h4 className="font-medium text-gray-900">Tính năng</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {[
                        { key: 'security_scan', label: 'Security Scan', icon: Shield },
                        { key: 'code_quality_check', label: 'Code Quality Check', icon: Code },
                        { key: 'dependency_scan', label: 'Dependency Scan', icon: Database },
                        { key: 'notification_enabled', label: 'Notifications', icon: Bell }
                      ].map(({ key, label, icon: Icon }) => (
                        <div key={key} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                          <div className="flex items-center gap-2">
                            <Icon size={16} className="text-gray-500" />
                            <span className="text-sm font-medium text-gray-900">{label}</span>
                          </div>
                          {isEditMode ? (
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={repository.config[key as keyof typeof repository.config] as boolean}
                                onChange={(e) => handleInputChange(`config.${key}`, e.target.checked)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                            </label>
                          ) : (
                            <span className={`badge-soft text-xs ${
                              repository.config[key as keyof typeof repository.config] 
                                ? 'badge-soft-success' 
                                : 'badge-soft-secondary'
                            }`}>
                              {repository.config[key as keyof typeof repository.config] ? 'Enabled' : 'Disabled'}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Stats Sidebar */}
            {!isNewRepo && (
              <div className="space-y-6">
                <motion.div
                  className="card-soft"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.3 }}
                >
                  <div className="card-soft-header">
                    <h3 className="text-lg font-semibold text-gray-900">📊 Thống kê</h3>
                  </div>
                  <div className="card-soft-body space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Health Score</span>
                      <span className="text-lg font-semibold text-gray-900">{repository.health_score}/100</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Total Scans</span>
                      <span className="text-lg font-semibold text-gray-900">{repository.scan_count}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Issues Found</span>
                      <span className="text-lg font-semibold text-gray-900">{repository.issues_count}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Stars</span>
                      <span className="text-lg font-semibold text-gray-900">{repository.stars}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Forks</span>
                      <span className="text-lg font-semibold text-gray-900">{repository.forks}</span>
                    </div>
                  </div>
                </motion.div>

                {/* Recent Scans - Only show in view mode */}
                {isViewMode && (
                  <motion.div
                    className="card-soft"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: 0.4 }}
                  >
                    <div className="card-soft-header">
                      <h3 className="text-lg font-semibold text-gray-900">🔍 Recent Scans</h3>
                    </div>
                    <div className="card-soft-body space-y-3">
                      {/* Mock scan data */}
                      {[
                        { id: '1', date: '2025-01-29', status: 'completed', issues: 5, duration: '2m 30s' },
                        { id: '2', date: '2025-01-28', status: 'completed', issues: 8, duration: '1m 45s' },
                        { id: '3', date: '2025-01-27', status: 'failed', issues: 0, duration: '0m 15s' },
                        { id: '4', date: '2025-01-26', status: 'completed', issues: 3, duration: '2m 10s' },
                      ].map((scan) => (
                        <div key={scan.id} className="flex items-center justify-between p-3 border border-gray-100 rounded-lg hover:bg-gray-50 transition-colors">
                          <div className="flex items-center gap-3">
                            <div className={`w-3 h-3 rounded-full ${
                              scan.status === 'completed' ? 'bg-green-500' :
                              scan.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500'
                            }`}></div>
                            <div>
                              <div className="text-sm font-medium text-gray-900">{scan.date}</div>
                              <div className="text-xs text-gray-500">{scan.duration}</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm font-medium text-gray-900">
                              {scan.status === 'completed' ? `${scan.issues} issues` : 
                               scan.status === 'failed' ? 'Failed' : 'Running'}
                            </div>
                            <div className={`text-xs capitalize ${
                              scan.status === 'completed' ? 'text-green-600' :
                              scan.status === 'failed' ? 'text-red-600' : 'text-yellow-600'
                            }`}>
                              {scan.status}
                            </div>
                          </div>
                        </div>
                      ))}
                      
                      {/* View All Scans Button */}
                      <button className="w-full text-center py-2 text-sm text-blue-600 hover:text-blue-800 transition-colors">
                        View All Scans →
                      </button>
                    </div>
                  </motion.div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default RepositoryManagement; 