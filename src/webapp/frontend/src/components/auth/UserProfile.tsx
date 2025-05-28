/**
 * User Profile Component.
 * 
 * Component để hiển thị và quản lý thông tin profile người dùng.
 * Bao gồm cập nhật thông tin cá nhân, đổi mật khẩu, và quản lý sessions.
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useAuthValidation, useUserSessions } from '../../hooks/useAuth';
import { UpdateProfileRequest, ChangePasswordRequest, UserSession } from '../../types';

interface UserProfileProps {
  className?: string;
}

export const UserProfile: React.FC<UserProfileProps> = ({ className = '' }) => {
  const { user, updateProfile, changePassword, logout } = useAuth();
  const { validateEmail, validateFullName, validatePassword, validatePasswordConfirm } = useAuthValidation();
  const { data: sessions, loading: sessionsLoading, fetchSessions, revokeSession, revokeAllSessions } = useUserSessions();

  // State
  const [activeTab, setActiveTab] = useState<'profile' | 'password' | 'sessions'>('profile');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Profile form state
  const [profileData, setProfileData] = useState<UpdateProfileRequest>({
    full_name: '',
    avatar_url: '',
    timezone: 'Asia/Ho_Chi_Minh',
    preferences: {},
  });

  const [profileErrors, setProfileErrors] = useState<Partial<Record<keyof UpdateProfileRequest, string>>>({});

  // Password form state
  const [passwordData, setPasswordData] = useState<ChangePasswordRequest & { confirmPassword: string }>({
    current_password: '',
    new_password: '',
    confirmPassword: '',
  });

  const [passwordErrors, setPasswordErrors] = useState<Partial<Record<keyof (ChangePasswordRequest & { confirmPassword: string }), string>>>({});

  // Initialize profile data from user
  useEffect(() => {
    if (user) {
      setProfileData({
        full_name: user.profile?.full_name || '',
        avatar_url: user.profile?.avatar_url || '',
        timezone: user.profile?.timezone || 'Asia/Ho_Chi_Minh',
        preferences: user.profile?.preferences || {},
      });
    }
  }, [user]);

  // Fetch sessions when sessions tab is active
  useEffect(() => {
    if (activeTab === 'sessions') {
      fetchSessions();
    }
  }, [activeTab, fetchSessions]);

  // Clear message after 5 seconds
  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => setMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  // Handle profile update
  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    // Validate
    const errors: Partial<Record<keyof UpdateProfileRequest, string>> = {};
    
    if (profileData.full_name) {
      const fullNameError = validateFullName(profileData.full_name);
      if (fullNameError) errors.full_name = fullNameError;
    }

    if (Object.keys(errors).length > 0) {
      setProfileErrors(errors);
      setLoading(false);
      return;
    }

    try {
      await updateProfile(profileData);
      setMessage({ type: 'success', text: 'Cập nhật thông tin thành công!' });
      setProfileErrors({});
    } catch (error) {
      setMessage({ type: 'error', text: 'Có lỗi xảy ra khi cập nhật thông tin' });
    } finally {
      setLoading(false);
    }
  };

  // Handle password change
  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    // Validate
    const errors: Partial<Record<keyof (ChangePasswordRequest & { confirmPassword: string }), string>> = {};
    
    if (!passwordData.current_password) {
      errors.current_password = 'Mật khẩu hiện tại là bắt buộc';
    }

    const newPasswordError = validatePassword(passwordData.new_password);
    if (newPasswordError) errors.new_password = newPasswordError;

    const confirmPasswordError = validatePasswordConfirm(passwordData.new_password, passwordData.confirmPassword);
    if (confirmPasswordError) errors.confirmPassword = confirmPasswordError;

    if (Object.keys(errors).length > 0) {
      setPasswordErrors(errors);
      setLoading(false);
      return;
    }

    try {
      await changePassword({
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      });
      setMessage({ type: 'success', text: 'Đổi mật khẩu thành công!' });
      setPasswordData({ current_password: '', new_password: '', confirmPassword: '' });
      setPasswordErrors({});
    } catch (error) {
      setMessage({ type: 'error', text: 'Có lỗi xảy ra khi đổi mật khẩu' });
    } finally {
      setLoading(false);
    }
  };

  // Handle session revoke
  const handleRevokeSession = async (sessionId: string) => {
    const success = await revokeSession(sessionId);
    if (success) {
      setMessage({ type: 'success', text: 'Đã thu hồi phiên đăng nhập' });
    }
  };

  // Handle revoke all sessions
  const handleRevokeAllSessions = async () => {
    if (!window.confirm('Bạn có chắc muốn thu hồi tất cả phiên đăng nhập? Bạn sẽ cần đăng nhập lại.')) {
      return;
    }

    const success = await revokeAllSessions();
    if (success) {
      setMessage({ type: 'success', text: 'Đã thu hồi tất cả phiên đăng nhập' });
      // Logout current session
      setTimeout(() => logout(), 2000);
    }
  };

  if (!user) {
    return null;
  }

  return (
    <div className={`bg-white rounded-3xl shadow-soft-xl ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-center">
          <div className="h-16 w-16 rounded-full bg-gradient-to-r from-blue-600 to-blue-700 flex items-center justify-center text-white text-xl font-bold mr-4">
            {user.profile?.full_name ? user.profile.full_name.charAt(0).toUpperCase() : user.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {user.profile?.full_name || user.username}
            </h1>
            <p className="text-gray-600">{user.email}</p>
            <p className="text-sm text-gray-500">
              Tham gia: {new Date(user.created_at).toLocaleDateString('vi-VN')}
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-6 py-4 border-b border-gray-100">
        <div className="flex space-x-8">
          {['profile', 'password', 'sessions'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`pb-2 border-b-2 transition-colors ${
                activeTab === tab
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab === 'profile' && 'Thông tin cá nhân'}
              {tab === 'password' && 'Đổi mật khẩu'}
              {tab === 'sessions' && 'Phiên đăng nhập'}
            </button>
          ))}
        </div>
      </div>

      {/* Message */}
      {message && (
        <div className={`mx-6 mt-6 p-4 rounded-xl ${
          message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
        }`}>
          {message.text}
        </div>
      )}

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'profile' && (
          <form onSubmit={handleProfileUpdate} className="space-y-6">
            <div>
              <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-2">
                Họ và tên
              </label>
              <input
                id="full_name"
                type="text"
                value={profileData.full_name}
                onChange={(e) => setProfileData(prev => ({ ...prev, full_name: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
                placeholder="Nhập họ và tên"
              />
              {profileErrors.full_name && (
                <p className="mt-1 text-sm text-red-600">{profileErrors.full_name}</p>
              )}
            </div>

            <div>
              <label htmlFor="timezone" className="block text-sm font-medium text-gray-700 mb-2">
                Múi giờ
              </label>
              <select
                id="timezone"
                value={profileData.timezone}
                onChange={(e) => setProfileData(prev => ({ ...prev, timezone: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
              >
                <option value="Asia/Ho_Chi_Minh">Việt Nam (UTC+7)</option>
                <option value="UTC">UTC</option>
                <option value="America/New_York">New York (UTC-5)</option>
                <option value="Europe/London">London (UTC+0)</option>
                <option value="Asia/Tokyo">Tokyo (UTC+9)</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 rounded-xl font-medium bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white transform hover:scale-105 active:scale-95 transition-all duration-300 shadow-soft-2xl hover:shadow-soft-3xl disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Đang cập nhật...' : 'Cập nhật thông tin'}
            </button>
          </form>
        )}

        {activeTab === 'password' && (
          <form onSubmit={handlePasswordChange} className="space-y-6">
            <div>
              <label htmlFor="current_password" className="block text-sm font-medium text-gray-700 mb-2">
                Mật khẩu hiện tại
              </label>
              <input
                id="current_password"
                type="password"
                value={passwordData.current_password}
                onChange={(e) => setPasswordData(prev => ({ ...prev, current_password: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
                placeholder="Nhập mật khẩu hiện tại"
              />
              {passwordErrors.current_password && (
                <p className="mt-1 text-sm text-red-600">{passwordErrors.current_password}</p>
              )}
            </div>

            <div>
              <label htmlFor="new_password" className="block text-sm font-medium text-gray-700 mb-2">
                Mật khẩu mới
              </label>
              <input
                id="new_password"
                type="password"
                value={passwordData.new_password}
                onChange={(e) => setPasswordData(prev => ({ ...prev, new_password: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
                placeholder="Nhập mật khẩu mới"
              />
              {passwordErrors.new_password && (
                <p className="mt-1 text-sm text-red-600">{passwordErrors.new_password}</p>
              )}
            </div>

            <div>
              <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 mb-2">
                Xác nhận mật khẩu mới
              </label>
              <input
                id="confirm_password"
                type="password"
                value={passwordData.confirmPassword}
                onChange={(e) => setPasswordData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
                placeholder="Nhập lại mật khẩu mới"
              />
              {passwordErrors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">{passwordErrors.confirmPassword}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 rounded-xl font-medium bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 text-white transform hover:scale-105 active:scale-95 transition-all duration-300 shadow-soft-2xl hover:shadow-soft-3xl disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Đang đổi mật khẩu...' : 'Đổi mật khẩu'}
            </button>
          </form>
        )}

        {activeTab === 'sessions' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900">Phiên đăng nhập</h3>
              <button
                onClick={handleRevokeAllSessions}
                className="px-4 py-2 text-sm text-red-600 hover:text-red-800 border border-red-200 hover:border-red-300 rounded-xl transition-colors"
              >
                Thu hồi tất cả
              </button>
            </div>

            {sessionsLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              </div>
            ) : (
              <div className="space-y-4">
                {sessions?.map((session: UserSession) => (
                  <div key={session.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-xl">
                    <div>
                      <p className="font-medium text-gray-900">
                        {session.user_agent?.includes('Chrome') && 'Chrome'}
                        {session.user_agent?.includes('Firefox') && 'Firefox'}
                        {session.user_agent?.includes('Safari') && 'Safari'}
                        {!session.user_agent && 'Trình duyệt không xác định'}
                      </p>
                      <p className="text-sm text-gray-500">
                        IP: {session.ip_address || 'Không xác định'}
                      </p>
                      <p className="text-sm text-gray-500">
                        Lần cuối: {new Date(session.last_used_at).toLocaleString('vi-VN')}
                      </p>
                    </div>
                    <button
                      onClick={() => handleRevokeSession(session.id)}
                      className="px-3 py-1 text-sm text-red-600 hover:text-red-800 border border-red-200 hover:border-red-300 rounded-lg transition-colors"
                    >
                      Thu hồi
                    </button>
                  </div>
                )) || []}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}; 