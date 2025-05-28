/**
 * Register Form Component.
 * 
 * Modern registration form với Soft UI design theo quy định trong PLANNING.md.
 * Hỗ trợ validation, loading states, và error handling.
 */

import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useAuthValidation } from '../../hooks/useAuth';
import { RegisterRequest } from '../../types';

interface RegisterFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
  className?: string;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({
  onSuccess,
  onSwitchToLogin,
  className = '',
}) => {
  const { register, loading } = useAuth();
  const { validateRegisterForm, validatePasswordConfirm } = useAuthValidation();

  // Form state
  const [formData, setFormData] = useState<RegisterRequest & { confirmPassword: string }>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });

  const [errors, setErrors] = useState<Partial<Record<keyof (RegisterRequest & { confirmPassword: string }), string>>>({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);

  // Handle input changes
  const handleInputChange = (field: keyof (RegisterRequest & { confirmPassword: string }), value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }

    // Clear confirm password error when password changes
    if (field === 'password' && errors.confirmPassword) {
      setErrors(prev => ({ ...prev, confirmPassword: undefined }));
    }
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate form
    const { confirmPassword, ...registerData } = formData;
    const validation = validateRegisterForm(registerData);
    let formErrors = { ...validation.errors };

    // Validate password confirmation
    const confirmPasswordError = validatePasswordConfirm(formData.password, confirmPassword);
    if (confirmPasswordError) {
      formErrors.confirmPassword = confirmPasswordError;
    }

    // Check terms acceptance
    if (!acceptTerms) {
      formErrors.acceptTerms = 'Bạn phải đồng ý với điều khoản sử dụng';
    }

    if (Object.keys(formErrors).length > 0) {
      setErrors(formErrors);
      return;
    }

    try {
      await register(registerData);
      onSuccess?.();
    } catch (error) {
      // Error handling is done in AuthContext
      console.error('Registration failed:', error);
    }
  };

  return (
    <div className={`bg-white rounded-3xl shadow-soft-xl p-8 ${className}`}>
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Tạo tài khoản mới
        </h1>
        <p className="text-gray-600">
          Đăng ký để bắt đầu sử dụng AI Code Reviewer
        </p>
      </div>

      {/* Registration Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Full Name Field */}
        <div>
          <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-2">
            Họ và tên <span className="text-gray-400">(Không bắt buộc)</span>
          </label>
          <div className="relative">
            <input
              id="full_name"
              type="text"
              value={formData.full_name}
              onChange={(e) => handleInputChange('full_name', e.target.value)}
              className={`
                w-full px-4 py-3 pl-10 border rounded-xl transition-all duration-300
                bg-gray-50 border-gray-200 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-200
                ${errors.full_name ? 'border-red-500 focus:border-red-500 focus:ring-red-200' : ''}
              `}
              placeholder="Nhập họ và tên"
              disabled={loading}
              autoComplete="name"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <i className="fas fa-user-circle text-gray-400"></i>
            </div>
          </div>
          {errors.full_name && (
            <p className="mt-1 text-sm text-red-600">{errors.full_name}</p>
          )}
        </div>

        {/* Username Field */}
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
            Tên đăng nhập <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <input
              id="username"
              type="text"
              value={formData.username}
              onChange={(e) => handleInputChange('username', e.target.value)}
              className={`
                w-full px-4 py-3 pl-10 border rounded-xl transition-all duration-300
                bg-gray-50 border-gray-200 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-200
                ${errors.username ? 'border-red-500 focus:border-red-500 focus:ring-red-200' : ''}
              `}
              placeholder="Nhập tên đăng nhập"
              disabled={loading}
              autoComplete="username"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <i className="fas fa-user text-gray-400"></i>
            </div>
          </div>
          {errors.username && (
            <p className="mt-1 text-sm text-red-600">{errors.username}</p>
          )}
        </div>

        {/* Email Field */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
            Email <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              className={`
                w-full px-4 py-3 pl-10 border rounded-xl transition-all duration-300
                bg-gray-50 border-gray-200 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-200
                ${errors.email ? 'border-red-500 focus:border-red-500 focus:ring-red-200' : ''}
              `}
              placeholder="Nhập địa chỉ email"
              disabled={loading}
              autoComplete="email"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <i className="fas fa-envelope text-gray-400"></i>
            </div>
          </div>
          {errors.email && (
            <p className="mt-1 text-sm text-red-600">{errors.email}</p>
          )}
        </div>

        {/* Password Field */}
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
            Mật khẩu <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              value={formData.password}
              onChange={(e) => handleInputChange('password', e.target.value)}
              className={`
                w-full px-4 py-3 pl-10 pr-12 border rounded-xl transition-all duration-300
                bg-gray-50 border-gray-200 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-200
                ${errors.password ? 'border-red-500 focus:border-red-500 focus:ring-red-200' : ''}
              `}
              placeholder="Nhập mật khẩu"
              disabled={loading}
              autoComplete="new-password"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <i className="fas fa-lock text-gray-400"></i>
            </div>
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
              disabled={loading}
            >
              <i className={`fas ${showPassword ? 'fa-eye-slash' : 'fa-eye'} text-gray-400 hover:text-gray-600`}></i>
            </button>
          </div>
          {errors.password && (
            <p className="mt-1 text-sm text-red-600">{errors.password}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ cái và số
          </p>
        </div>

        {/* Confirm Password Field */}
        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
            Xác nhận mật khẩu <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <input
              id="confirmPassword"
              type={showConfirmPassword ? 'text' : 'password'}
              value={formData.confirmPassword}
              onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
              className={`
                w-full px-4 py-3 pl-10 pr-12 border rounded-xl transition-all duration-300
                bg-gray-50 border-gray-200 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-200
                ${errors.confirmPassword ? 'border-red-500 focus:border-red-500 focus:ring-red-200' : ''}
              `}
              placeholder="Nhập lại mật khẩu"
              disabled={loading}
              autoComplete="new-password"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <i className="fas fa-lock text-gray-400"></i>
            </div>
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
              disabled={loading}
            >
              <i className={`fas ${showConfirmPassword ? 'fa-eye-slash' : 'fa-eye'} text-gray-400 hover:text-gray-600`}></i>
            </button>
          </div>
          {errors.confirmPassword && (
            <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>
          )}
        </div>

        {/* Terms & Conditions */}
        <div>
          <label className="flex items-start">
            <input
              type="checkbox"
              checked={acceptTerms}
              onChange={(e) => setAcceptTerms(e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
              disabled={loading}
            />
            <span className="ml-2 text-sm text-gray-600">
              Tôi đồng ý với{' '}
              <button type="button" className="text-blue-600 hover:text-blue-800 font-medium">
                Điều khoản sử dụng
              </button>{' '}
              và{' '}
              <button type="button" className="text-blue-600 hover:text-blue-800 font-medium">
                Chính sách bảo mật
              </button>
            </span>
          </label>
          {errors.acceptTerms && (
            <p className="mt-1 text-sm text-red-600">{errors.acceptTerms}</p>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className={`
            w-full py-3 px-4 rounded-xl font-medium transition-all duration-300
            ${loading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 shadow-soft-2xl hover:shadow-soft-3xl'
            }
            text-white transform hover:scale-105 active:scale-95
          `}
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Đang đăng ký...
            </div>
          ) : (
            'Đăng ký tài khoản'
          )}
        </button>
      </form>

      {/* Social Registration (Optional) */}
      <div className="mt-6">
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">Hoặc đăng ký với</span>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-3">
          <button
            type="button"
            className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-xl shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 transition-colors"
            disabled={loading}
          >
            <i className="fab fa-google text-red-500 mr-2"></i>
            Google
          </button>
          <button
            type="button"
            className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-xl shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 transition-colors"
            disabled={loading}
          >
            <i className="fab fa-github text-gray-900 mr-2"></i>
            GitHub
          </button>
        </div>
      </div>

      {/* Switch to Login */}
      <div className="mt-6 text-center">
        <p className="text-sm text-gray-600">
          Đã có tài khoản?{' '}
          <button
            type="button"
            onClick={onSwitchToLogin}
            className="text-blue-600 hover:text-blue-800 font-medium transition-colors"
            disabled={loading}
          >
            Đăng nhập ngay
          </button>
        </p>
      </div>
    </div>
  );
}; 