import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiService } from "../services/api";
import { repositoryApi } from "../services/repositoryApi";
import ScanDialog from "../components/ScanDialog";

// Định nghĩa kiểu dữ liệu
interface Repository {
  id: string;
  name: string;
  description: string;
  url: string;
  owner: {
    name: string;
    avatar_url: string;
  };
  language: string;
  stars: number;
  forks: number;
  issues: number;
  created_at: string;
  updated_at: string;
  default_branch: string;
  is_private: boolean;
  languages: Record<string, number>;
  cached_path?: string;
  last_commit_hash?: string;
  cache_expires_at?: string;
  cache_size_mb?: number;
}

interface Scan {
  id: string;
  created_at: string;
  scan_type: 'full' | 'pr';
  branch: string;
  pr_number?: string;
  status: 'completed' | 'in-progress' | 'failed';
}

const RepositoryDetail = () => {
  const { id } = useParams<{ id: string }>();
  const [repository, setRepository] = useState<Repository | null>(null);
  const [recentScans, setRecentScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Cài đặt AI/Scan
  const [aiModel, setAiModel] = useState('openai');
  const [modelName, setModelName] = useState('gpt-4o');
  const [apiKey, setApiKey] = useState('');
  
  // Trạng thái UI
  const [isUpdating, setIsUpdating] = useState(false);
  const [isScanDialogOpen, setIsScanDialogOpen] = useState(false);
  
  // Lấy thông tin repository
  useEffect(() => {
    const fetchRepositoryDetails = async () => {
      if (!id) return;
      
      setLoading(true);
      try {
        const response = await apiService.getRepositoryDetail(id);
        setRepository(response.data);
        
        // Lấy danh sách scan gần đây
        const scansResponse = await repositoryApi.getRecentScans(id);
        setRecentScans(scansResponse.data || []);
        
        // Lấy cài đặt AI nếu có
        const aiSettingsResponse = await repositoryApi.getRepositoryAISettings(id);
        if (aiSettingsResponse.data) {
          setAiModel(aiSettingsResponse.data.model || 'openai');
          setModelName(aiSettingsResponse.data.modelName || 'gpt-4o');
          setApiKey(aiSettingsResponse.data.apiKey || '');
        }
        
        setError(null);
      } catch (err) {
        setError('Không thể tải thông tin repository. Vui lòng thử lại sau.');
        console.error('Error fetching repository details:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchRepositoryDetails();
  }, [id]);
  
  // Xử lý cập nhật thông tin repository
  const handleUpdateRepository = async () => {
    if (!id) return;
    
    setIsUpdating(true);
    try {
      await apiService.updateRepositoryLatest(id);
      
      // Lấy lại thông tin mới nhất
      const response = await apiService.getRepositoryDetail(id);
      setRepository(response.data);
      
      alert("Cập nhật thành công. Thông tin repository đã được cập nhật mới nhất.");
      
      setError(null);
    } catch (err) {
      setError('Không thể cập nhật thông tin repository. Vui lòng thử lại sau.');
      console.error('Error updating repository:', err);
      
      alert("Cập nhật thất bại. Không thể cập nhật thông tin repository.");
    } finally {
      setIsUpdating(false);
    }
  };
  
  // Xử lý việc bắt đầu scan mới
  const handleStartScan = async (scanData: any) => {
    try {
      // Kết hợp thông tin scan với cấu hình AI
      const fullScanData = {
        ...scanData,
        aiSettings: {
          model: aiModel,
          modelName: modelName,
          apiKey: apiKey,
        }
      };
      
      await repositoryApi.startRepositoryScan(fullScanData);
      
      // Thông báo thành công
      alert(`Đã bắt đầu scan ${scanData.scanType === 'full' ? `toàn bộ branch ${scanData.branch}` : `PR #${scanData.prNumber}`}`);
      
      // Đóng dialog
      setIsScanDialogOpen(false);
      
      // Làm mới danh sách scan
      const scansResponse = await repositoryApi.getRecentScans(id || '');
      setRecentScans(scansResponse.data || []);
    } catch (error) {
      console.error('Error starting scan:', error);
      alert("Không thể bắt đầu scan. Đã có lỗi xảy ra.");
    }
  };
  
  // Lưu cài đặt AI
  const handleSaveAISettings = async () => {
    try {
      if (!id) return;
      
      await repositoryApi.saveRepositoryAISettings(id, {
        model: aiModel,
        modelName: modelName,
        apiKey: apiKey
      });
      
      alert("Lưu cài đặt thành công. Cài đặt AI đã được cập nhật.");
    } catch (error) {
      console.error('Error saving AI settings:', error);
      alert("Không thể lưu cài đặt. Đã có lỗi xảy ra.");
    }
  };
  
  // Hiển thị skeleton loading
  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="animate-pulse">
          <div className="h-10 bg-gray-200 rounded mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="h-60 bg-gray-200 rounded"></div>
            <div className="h-60 bg-gray-200 rounded"></div>
          </div>
          <div className="h-80 bg-gray-200 rounded mt-6"></div>
        </div>
      </div>
    );
  }
  
  // Hiển thị lỗi nếu có
  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="border border-red-300 bg-red-50 rounded-md">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-red-700">Có lỗi xảy ra</h2>
                <p className="text-red-600 mt-2">{error}</p>
              </div>
              <button onClick={() => window.location.reload()} className="px-4 py-2 bg-white border border-gray-300 rounded-md">
                Thử lại
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  // Nếu không có dữ liệu
  if (!repository) {
    return (
      <div className="container mx-auto p-6">
        <div className="border border-gray-200 rounded-md">
          <div className="p-6 text-center">
            <h2 className="text-xl font-semibold">Không tìm thấy thông tin repository</h2>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">{repository.name}</h1>
        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {repository.is_private ? 'Private' : 'Public'}
          </span>
          <span className="text-sm text-gray-500">
            Cập nhật lần cuối: {new Date(repository.updated_at).toLocaleString('vi-VN')}
          </span>
        </div>
      </div>
      
      {/* Thông tin cơ bản Repository */}
      <div className="mb-6 overflow-hidden border-none shadow-md rounded-lg bg-gradient-to-br from-blue-900 to-blue-600 text-white">
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="flex items-center mb-4">
                {repository.owner.avatar_url && (
                  <img 
                    src={repository.owner.avatar_url} 
                    alt="Owner avatar" 
                    className="w-12 h-12 rounded-full mr-4 border-2 border-white"
                  />
                )}
                <div>
                  <h3 className="text-xl font-semibold">{repository.name}</h3>
                  <p className="text-blue-100">by {repository.owner.name}</p>
                </div>
              </div>
              <p className="mb-4 text-blue-50">{repository.description || 'Không có mô tả'}</p>
              <div className="flex items-center space-x-4">
                <button 
                  onClick={handleUpdateRepository} 
                  disabled={isUpdating} 
                  className="px-4 py-2 bg-white text-blue-800 rounded-md text-sm font-medium"
                >
                  {isUpdating ? 'Đang cập nhật...' : 'Cập nhật thông tin mới nhất'}
                </button>
                <a 
                  href={repository.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-100 hover:text-white text-sm underline"
                >
                  Xem trên GitHub
                </a>
              </div>
            </div>
            <div>
              <div className="grid grid-cols-3 gap-2 mb-4">
                <div className="bg-white/10 p-3 rounded-lg text-center">
                  <div className="text-2xl font-bold">{repository.stars}</div>
                  <div className="text-xs text-blue-100">Stars</div>
                </div>
                <div className="bg-white/10 p-3 rounded-lg text-center">
                  <div className="text-2xl font-bold">{repository.forks}</div>
                  <div className="text-xs text-blue-100">Forks</div>
                </div>
                <div className="bg-white/10 p-3 rounded-lg text-center">
                  <div className="text-2xl font-bold">{repository.issues}</div>
                  <div className="text-xs text-blue-100">Issues</div>
                </div>
              </div>
              <div className="bg-white/10 p-3 rounded-lg">
                <h4 className="text-sm font-semibold mb-2">Phân bố ngôn ngữ</h4>
                <div className="flex h-4 rounded-full overflow-hidden">
                  {repository.languages && Object.entries(repository.languages).map(([lang, percent], index) => (
                    <div 
                      key={lang} 
                      className={`h-full ${getLanguageColor(lang)}`} 
                      style={{ width: `${percent}%` }}
                      title={`${lang}: ${percent}%`}
                    />
                  ))}
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {repository.languages && Object.keys(repository.languages).map(lang => (
                    <span key={lang} className="text-xs bg-white/20 px-2 py-1 rounded-full">
                      {lang}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Cấu hình AI/Scan */}
      <div className="mb-6 backdrop-blur-lg border border-gray-200 shadow-md bg-white/80 rounded-lg">
        <div className="flex flex-row items-center justify-between p-4 border-b">
          <h3 className="text-xl font-semibold">Cấu hình AI/Scan</h3>
          <button 
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm"
            onClick={handleSaveAISettings}
          >
            Lưu cài đặt
          </button>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div>
              <label className="text-sm font-medium mb-2 block">LLM Model</label>
              <select
                value={aiModel}
                onChange={(e) => setAiModel(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="openai">OpenAI</option>
                <option value="gemini">Gemini</option>
                <option value="ollama">Ollama (local)</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Tên Model</label>
              <input
                type="text"
                value={modelName}
                onChange={(e) => setModelName(e.target.value)}
                placeholder="Ví dụ: gpt-4o, claude-3-opus"
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            {(aiModel === 'openai' || aiModel === 'gemini') && (
              <div>
                <label className="text-sm font-medium mb-2 block">API Key</label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Nhập API key của bạn"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Recent Scans */}
      <div className="mb-6 border border-gray-200 rounded-lg shadow-md bg-white">
        <div className="p-4 border-b">
          <h3 className="text-xl font-semibold">Lịch sử scan gần đây</h3>
        </div>
        <div className="p-6">
          {recentScans.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ngày</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Loại scan</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Branch</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trạng thái</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Thao tác</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {recentScans.map((scan) => (
                    <tr key={scan.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(scan.created_at).toLocaleDateString('vi-VN')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {scan.scan_type === 'full' ? 'Toàn bộ project' : `PR #${scan.pr_number}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {scan.branch}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status={scan.status} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button className="px-4 py-2 border border-gray-300 rounded-md text-sm">
                          Xem chi tiết
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center p-6">
              <p className="text-gray-500">Chưa có scan nào được thực hiện</p>
            </div>
          )}
        </div>
      </div>
      
      {/* New Scan Button - Floating Action Button */}
      <div className="fixed bottom-6 right-6">
        <button 
          className="h-14 w-14 rounded-full shadow-xl bg-emerald-600 hover:bg-emerald-700 text-white flex items-center justify-center"
          onClick={() => setIsScanDialogOpen(true)}
        >
          <span className="text-2xl">+</span>
        </button>
      </div>

      {/* Scan Dialog */}
      {isScanDialogOpen && id && (
        <ScanDialog
          repositoryId={id}
          onScanCreated={(scan) => {
            setRecentScans([scan, ...recentScans]);
            setIsScanDialogOpen(false);
          }}
          onClose={() => setIsScanDialogOpen(false)}
        />
      )}
    </div>
  );
};

// Helper components
const StatusBadge = ({ status }: { status: string }) => {
  let bgColor = '';
  let textColor = '';
  let statusText = '';

  switch (status) {
    case 'completed':
      bgColor = 'bg-green-100';
      textColor = 'text-green-800';
      statusText = 'Hoàn thành';
      break;
    case 'in-progress':
      bgColor = 'bg-orange-100';
      textColor = 'text-orange-800';
      statusText = 'Đang xử lý';
      break;
    case 'failed':
      bgColor = 'bg-red-100';
      textColor = 'text-red-800';
      statusText = 'Thất bại';
      break;
    default:
      bgColor = 'bg-gray-100';
      textColor = 'text-gray-800';
      statusText = 'Không xác định';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${bgColor} ${textColor}`}>
      {statusText}
    </span>
  );
};

// Helper function to get language color
const getLanguageColor = (language: string): string => {
  const colors: Record<string, string> = {
    JavaScript: 'bg-yellow-400',
    TypeScript: 'bg-blue-400',
    Python: 'bg-green-400',
    Java: 'bg-red-400',
    PHP: 'bg-purple-400',
    HTML: 'bg-orange-400',
    CSS: 'bg-pink-400',
    Ruby: 'bg-red-600',
    Go: 'bg-blue-300',
    Rust: 'bg-orange-600',
    // Thêm các ngôn ngữ khác nếu cần
  };
  
  return colors[language] || 'bg-gray-400';
};

export default RepositoryDetail; 