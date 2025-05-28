/**
 * Trang đăng ký cho AI Code Reviewer
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { RegisterRequest } from '../types';

interface RegisterFormData extends RegisterRequest {
  confirmPassword: string;
}

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { register, loading, isAuthenticated } = useAuth();

  // Form state
  const [formData, setFormData] = useState<RegisterFormData>({
    username: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });

  const [errors, setErrors] = useState<Partial<Record<keyof RegisterFormData, string>>>({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const redirectTo = (location.state as any)?.from?.pathname || '/dashboard';
      navigate(redirectTo, { replace: true });
    }
  }, [isAuthenticated, navigate, location]);

  // Handle input changes
  const handleInputChange = (field: keyof RegisterFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof RegisterFormData, string>> = {};
    
    // Full name validation
    if (!formData.full_name?.trim()) {
      newErrors.full_name = 'Vui lòng nhập họ và tên';
    } else if (formData.full_name.trim().length < 2) {
      newErrors.full_name = 'Họ và tên phải có ít nhất 2 ký tự';
    }
    
    // Email validation
    if (!formData.username.trim()) {
      newErrors.username = 'Vui lòng nhập email';
    } else if (!/\S+@\S+\.\S+/.test(formData.username)) {
      newErrors.username = 'Email không hợp lệ';
    }
    
    // Password validation
    if (!formData.password) {
      newErrors.password = 'Vui lòng nhập mật khẩu';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Mật khẩu phải có ít nhất 8 ký tự';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/.test(formData.password)) {
      newErrors.password = 'Mật khẩu phải chứa ít nhất 1 chữ hoa, 1 chữ thường, 1 số và 1 ký tự đặc biệt';
    }
    
    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Vui lòng xác nhận mật khẩu';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Mật khẩu xác nhận không khớp';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      // Extract register data (without confirmPassword)
      const registerData: RegisterRequest = {
        username: formData.username,
        password: formData.password,
        full_name: formData.full_name,
      };
      
      await register(registerData);
      // Navigation is handled by the useEffect above
    } catch (error) {
      console.error('Registration failed:', error);
      setErrors({ username: 'Đăng ký thất bại. Email có thể đã được sử dụng.' });
    }
  };

  // Calculate password strength
  const getPasswordStrength = (password: string) => {
    let score = 0;
    if (password.length >= 8) score += 1;
    if (/[a-z]/.test(password)) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/\d/.test(password)) score += 1;
    if (/[@$!%*?&]/.test(password)) score += 1;
    
    if (score < 2) return { level: 'weak', color: '#ef4444', text: 'Yếu' };
    if (score < 4) return { level: 'medium', color: '#f59e0b', text: 'Trung bình' };
    return { level: 'strong', color: '#10b981', text: 'Mạnh' };
  };

  const passwordStrength = getPasswordStrength(formData.password);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Main Card */}
        <div className="card-soft">
          <div className="card-soft-body p-8">
            {/* Header */}
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-r from-emerald-600 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
              </div>
              
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Đăng ký
              </h1>
              
              <p className="text-gray-600 text-sm">
                Tạo tài khoản mới để sử dụng AI Code Reviewer
              </p>
            </div>

            {/* Form */}
            <form
              onSubmit={handleSubmit}
              className="space-y-5"
              noValidate
            >
              {/* Full Name Field */}
              <div className="space-y-2">
                <label htmlFor="full_name" className="block text-sm font-semibold text-gray-800">
                  Họ và tên
                </label>
                <input
                  id="full_name"
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => handleInputChange('full_name', e.target.value)}
                  className={`
                    form-input w-full h-12 px-4 rounded-xl border-2 transition-all duration-200
                    bg-white text-gray-900 placeholder-gray-500
                    focus:ring-0 focus:outline-none
                    ${errors.full_name 
                      ? 'border-red-300 focus:border-red-500 bg-red-50' 
                      : 'border-gray-200 focus:border-emerald-500 hover:border-gray-300'
                    }
                  `}
                  placeholder="Nhập họ và tên của bạn"
                  disabled={loading}
                  autoComplete="name"
                  required
                  aria-describedby={errors.full_name ? 'full-name-error' : undefined}
                />
                {errors.full_name && (
                  <p
                    id="full-name-error"
                    className="text-sm text-red-600 font-medium"
                    role="alert"
                  >
                    {errors.full_name}
                  </p>
                )}
              </div>

              {/* Email Field */}
              <div className="space-y-2">
                <label htmlFor="username" className="block text-sm font-semibold text-gray-800">
                  Email
                </label>
                <input
                  id="username"
                  type="email"
                  value={formData.username}
                  onChange={(e) => handleInputChange('username', e.target.value)}
                  className={`
                    form-input w-full h-12 px-4 rounded-xl border-2 transition-all duration-200
                    bg-white text-gray-900 placeholder-gray-500
                    focus:ring-0 focus:outline-none
                    ${errors.username 
                      ? 'border-red-300 focus:border-red-500 bg-red-50' 
                      : 'border-gray-200 focus:border-emerald-500 hover:border-gray-300'
                    }
                  `}
                  placeholder="Nhập email của bạn"
                  disabled={loading}
                  autoComplete="email"
                  required
                  aria-describedby={errors.username ? 'username-error' : undefined}
                />
                {errors.username && (
                  <p
                    id="username-error"
                    className="text-sm text-red-600 font-medium"
                    role="alert"
                  >
                    {errors.username}
                  </p>
                )}
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <label htmlFor="password" className="block text-sm font-semibold text-gray-800">
                  Mật khẩu
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    className={`
                      form-input w-full h-12 px-4 pr-12 rounded-xl border-2 transition-all duration-200
                      bg-white text-gray-900 placeholder-gray-500
                      focus:ring-0 focus:outline-none
                      ${errors.password 
                        ? 'border-red-300 focus:border-red-500 bg-red-50' 
                        : 'border-gray-200 focus:border-emerald-500 hover:border-gray-300'
                      }
                    `}
                    placeholder="Nhập mật khẩu"
                    disabled={loading}
                    autoComplete="new-password"
                    required
                    aria-describedby={errors.password ? 'password-error' : 'password-strength'}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-gray-700 transition-colors"
                    disabled={loading}
                    tabIndex={-1}
                    aria-label={showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}
                  >
                    {showPassword ? (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L8.464 8.464M9.878 9.878A3 3 0 0012 9c.612 0 1.176.171 1.663.471m-.547 4.773A3 3 0 0112 15c-.612 0-1.176-.171-1.663-.471M9.878 9.878a3 3 0 104.243 4.243m4.243-4.243A3 3 0 0112 9c-.612 0 1.176.171 1.663.471m-.547 4.773a3 3 0 01-1.663-.471M9.878 9.878L8.464 8.464 2.05 2.05M9.878 9.878L14.12 14.12M9.878 9.878A3 3 0 0012 9c.612 0 1.176.171 1.663.471m-.547 4.773A3 3 0 0112 15c-.612 0-1.176-.171-1.663-.471" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
                
                {/* Password Strength Indicator */}
                {formData.password && (
                  <div id="password-strength" className="mt-2">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-gray-600">Độ mạnh mật khẩu:</span>
                      <span style={{ color: passwordStrength.color }} className="font-medium">
                        {passwordStrength.text}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="h-2 rounded-full transition-all duration-300"
                        style={{
                          backgroundColor: passwordStrength.color,
                          width: passwordStrength.level === 'weak' ? '33%' : 
                                 passwordStrength.level === 'medium' ? '66%' : '100%'
                        }}
                      />
                    </div>
                  </div>
                )}
                
                {errors.password && (
                  <p
                    id="password-error"
                    className="text-sm text-red-600 font-medium"
                    role="alert"
                  >
                    {errors.password}
                  </p>
                )}
              </div>

              {/* Confirm Password Field */}
              <div className="space-y-2">
                <label htmlFor="confirmPassword" className="block text-sm font-semibold text-gray-800">
                  Xác nhận mật khẩu
                </label>
                <div className="relative">
                  <input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={formData.confirmPassword}
                    onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                    className={`
                      form-input w-full h-12 px-4 pr-12 rounded-xl border-2 transition-all duration-200
                      bg-white text-gray-900 placeholder-gray-500
                      focus:ring-0 focus:outline-none
                      ${errors.confirmPassword 
                        ? 'border-red-300 focus:border-red-500 bg-red-50' 
                        : 'border-gray-200 focus:border-emerald-500 hover:border-gray-300'
                      }
                    `}
                    placeholder="Nhập lại mật khẩu"
                    disabled={loading}
                    autoComplete="new-password"
                    required
                    aria-describedby={errors.confirmPassword ? 'confirm-password-error' : undefined}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-gray-700 transition-colors"
                    disabled={loading}
                    tabIndex={-1}
                    aria-label={showConfirmPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}
                  >
                    {showConfirmPassword ? (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L8.464 8.464M9.878 9.878A3 3 0 0012 9c.612 0 1.176.171 1.663.471m-.547 4.773A3 3 0 0112 15c-.612 0-1.176-.171-1.663-.471M9.878 9.878a3 3 0 104.243 4.243m4.243-4.243A3 3 0 0112 9c-.612 0 1.176.171 1.663.471m-.547 4.773a3 3 0 01-1.663-.471M9.878 9.878L8.464 8.464 2.05 2.05M9.878 9.878L14.12 14.12M9.878 9.878A3 3 0 0012 9c.612 0 1.176.171 1.663.471m-.547 4.773A3 3 0 0112 15c-.612 0-1.176-.171-1.663-.471" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
                {errors.confirmPassword && (
                  <p
                    id="confirm-password-error"
                    className="text-sm text-red-600 font-medium"
                    role="alert"
                  >
                    {errors.confirmPassword}
                  </p>
                )}
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="btn-soft btn-soft-secondary w-full h-12 text-base font-semibold relative overflow-hidden mt-6"
              >
                {loading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <svg className="animate-spin w-5 h-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Đang đăng ký...</span>
                  </div>
                ) : (
                  'Tạo tài khoản'
                )}
              </button>
            </form>

            {/* Footer */}
            <div className="mt-8 text-center">
              <p className="text-sm text-gray-600">
                Đã có tài khoản?{' '}
                <Link
                  to="/login"
                  className="font-semibold text-emerald-600 hover:text-emerald-700 transition-colors"
                >
                  Đăng nhập ngay
                </Link>
              </p>
            </div>
          </div>
        </div>
        
        {/* Terms Notice */}
        <div className="mt-6 text-center text-xs text-gray-500">
          Bằng việc đăng ký, bạn đồng ý với{' '}
          <a href="#" className="text-emerald-600 hover:text-emerald-700 underline">
            Điều khoản dịch vụ
          </a>{' '}
          và{' '}
          <a href="#" className="text-emerald-600 hover:text-emerald-700 underline">
            Chính sách bảo mật
          </a>{' '}
          của chúng tôi.
        </div>
      </div>
    </div>
  );
}; 