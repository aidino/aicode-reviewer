import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { apiService } from '../services/api';
// Removed Lucide imports to avoid dependency issues: { X, Github, GitBranch, HelpCircle, Eye, EyeOff }

interface AddRepositoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (repo: any) => void;
}

const AddRepositoryModal: React.FC<AddRepositoryModalProps> = ({
  isOpen,
  onClose,
  onSuccess
}) => {
  const [formData, setFormData] = useState({
    repo_url: '',
    access_token: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showToken, setShowToken] = useState(false);

  if (!isOpen) return null;

  // Add CSS animation for spinner
  const spinKeyframes = `
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
  `;

  // Inject CSS if not already present
  if (typeof document !== 'undefined' && !document.getElementById('modal-spinner-css')) {
    const style = document.createElement('style');
    style.id = 'modal-spinner-css';
    style.textContent = spinKeyframes;
    document.head.appendChild(style);
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await apiService.addRepository(
        formData.repo_url,
        formData.access_token || undefined
      );

      if (response.error) {
        throw new Error(response.error.detail || 'Có lỗi xảy ra');
      }

      onSuccess(response.data);
      onClose();
      
      // Reset form
      setFormData({ repo_url: '', access_token: '' });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (error) setError(''); // Clear error when user types
  };

  const isValidUrl = (url: string) => {
    try {
      new URL(url);
      return url.includes('github.com') || url.includes('gitlab.com') || url.includes('bitbucket.org');
    } catch {
      return false;
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.7)',
      zIndex: 9998,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      {/* Stable modal with inline styles */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '0',
        maxWidth: '500px',
        width: '90%',
        maxHeight: '90vh',
        overflowY: 'auto',
        boxShadow: '0 25px 50px rgba(0,0,0,0.3)'
      }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '24px',
          borderBottom: '1px solid #e5e7eb'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '24px', color: '#2563eb' }}>📁</span>
            <h2 style={{ margin: 0, color: '#1f2937', fontSize: '20px', fontWeight: '600' }}>
              Thêm Repository
            </h2>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '24px',
              color: '#6b7280',
              cursor: 'pointer',
              padding: '8px',
              borderRadius: '50%',
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f3f4f6'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            ×
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Repository URL */}
          <div>
            <label style={{ 
              display: 'block', 
              fontSize: '14px', 
              fontWeight: '500', 
              color: '#374151', 
              marginBottom: '8px' 
            }}>
              Repository URL <span style={{ color: '#ef4444' }}>*</span>
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type="url"
                value={formData.repo_url}
                onChange={(e) => handleInputChange('repo_url', e.target.value)}
                placeholder="https://github.com/username/repository"
                style={{
                  width: '100%',
                  padding: '12px 40px 12px 16px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '16px',
                  boxSizing: 'border-box',
                  transition: 'border-color 0.2s',
                  outline: 'none'
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = '#2563eb'}
                onBlur={(e) => e.currentTarget.style.borderColor = '#d1d5db'}
                required
              />
              <span style={{
                position: 'absolute',
                right: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                fontSize: '20px',
                color: '#6b7280'
              }}>🔗</span>
            </div>
            <p style={{ fontSize: '12px', color: '#6b7280', margin: '4px 0 0 0' }}>
              Hỗ trợ GitHub, GitLab, Bitbucket
            </p>
          </div>

          {/* Personal Access Token */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <label style={{ 
                fontSize: '14px', 
                fontWeight: '500', 
                color: '#374151'
              }}>
                Personal Access Token (tùy chọn)
              </label>
              <span 
                title="Cần thiết cho private repositories"
                style={{
                  fontSize: '16px',
                  color: '#6b7280',
                  cursor: 'help'
                }}
              >
                ❓
              </span>
            </div>
            <div style={{ position: 'relative' }}>
              <input
                type={showToken ? "text" : "password"}
                value={formData.access_token}
                onChange={(e) => handleInputChange('access_token', e.target.value)}
                placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                style={{
                  width: '100%',
                  padding: '12px 40px 12px 16px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '16px',
                  boxSizing: 'border-box',
                  transition: 'border-color 0.2s',
                  outline: 'none'
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = '#2563eb'}
                onBlur={(e) => e.currentTarget.style.borderColor = '#d1d5db'}
              />
              <button
                type="button"
                onClick={() => setShowToken(!showToken)}
                style={{
                  position: 'absolute',
                  right: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  fontSize: '16px',
                  color: '#6b7280',
                  cursor: 'pointer'
                }}
              >
                {showToken ? '🙈' : '👁️'}
              </button>
            </div>
            <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '8px' }}>
              <p style={{ margin: '2px 0' }}>• Cần thiết cho repositories private</p>
              <p style={{ margin: '2px 0' }}>• Token không được lưu trữ, chỉ dùng để clone</p>
              <p style={{ margin: '2px 0', color: '#dc2626', fontWeight: '500' }}>
                • <strong>Private repos cần scope "repo"</strong> (không chỉ "public_repo")
              </p>
              <p style={{ margin: '2px 0' }}>
                • <a 
                    href="https://github.com/settings/tokens/new" 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    style={{ color: '#2563eb', textDecoration: 'none' }}
                    onMouseEnter={(e) => e.currentTarget.style.textDecoration = 'underline'}
                    onMouseLeave={(e) => e.currentTarget.style.textDecoration = 'none'}
                  >
                    Tạo GitHub Token với scope "repo" →
                  </a>
              </p>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div style={{
              background: '#fef2f2',
              border: '1px solid #fecaca',
              borderRadius: '8px',
              padding: '12px'
            }}>
              <p style={{ color: '#dc2626', fontSize: '14px', margin: 0 }}>❌ {error}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                flex: 1,
                padding: '12px 16px',
                border: '1px solid #d1d5db',
                color: '#374151',
                borderRadius: '8px',
                background: 'white',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
              disabled={loading}
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={loading || !formData.repo_url || !isValidUrl(formData.repo_url)}
              style={{
                flex: 1,
                padding: '12px 16px',
                background: loading || !formData.repo_url || !isValidUrl(formData.repo_url) ? '#d1d5db' : '#2563eb',
                color: 'white',
                borderRadius: '8px',
                border: 'none',
                cursor: loading || !formData.repo_url || !isValidUrl(formData.repo_url) ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                fontSize: '14px',
                fontWeight: '500',
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={(e) => {
                if (!e.currentTarget.disabled) {
                  e.currentTarget.style.backgroundColor = '#1d4ed8';
                }
              }}
              onMouseLeave={(e) => {
                if (!e.currentTarget.disabled) {
                  e.currentTarget.style.backgroundColor = '#2563eb';
                }
              }}
            >
              {loading ? (
                <>
                  <div style={{
                    width: '16px',
                    height: '16px',
                    border: '2px solid white',
                    borderTopColor: 'transparent',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                  }}></div>
                  Đang thêm...
                </>
              ) : (
                <>
                  <span>➕</span> Thêm Repository
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddRepositoryModal; 