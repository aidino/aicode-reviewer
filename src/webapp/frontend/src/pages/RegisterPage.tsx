/**
 * Trang đăng ký cho AI Code Reviewer với inline styles nhất quán
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
    email: '',
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
    
    // Username validation
    if (!formData.username.trim()) {
      newErrors.username = 'Vui lòng nhập tên người dùng';
    } else if (formData.username.trim().length < 3) {
      newErrors.username = 'Tên người dùng phải có ít nhất 3 ký tự';
    }
    
    // Email validation  
    if (!formData.email.trim()) {
      newErrors.email = 'Vui lòng nhập email';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email không hợp lệ';
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
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
      };
      
      await register(registerData);
      // Navigation is handled by the useEffect above
    } catch (error) {
      console.error('Registration failed:', error);
      setErrors({ email: 'Đăng ký thất bại. Email có thể đã được sử dụng.' });
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
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f8fafc',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        width: '100%',
        maxWidth: '450px'
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{
            fontSize: '2rem',
            fontWeight: 'bold',
            color: '#1e293b',
            marginBottom: '0.5rem'
          }}>
            📝 Đăng ký
          </h1>
          <p style={{
            color: '#64748b',
            fontSize: '0.875rem'
          }}>
            Tạo tài khoản mới để sử dụng AI Code Reviewer
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          {/* Full Name Field */}
          <div style={{ marginBottom: '1rem' }}>
            <label style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '0.5rem'
            }}>
              Họ và tên:
            </label>
            <input
              type="text"
              value={formData.full_name}
              onChange={(e) => handleInputChange('full_name', e.target.value)}
              placeholder="Nhập họ và tên của bạn"
              disabled={loading}
              style={{
                width: '100%',
                padding: '0.75rem',
                border: `2px solid ${errors.full_name ? '#fecaca' : '#e5e7eb'}`,
                borderRadius: '8px',
                fontSize: '1rem',
                outline: 'none',
                transition: 'border-color 0.2s',
                backgroundColor: loading ? '#f9fafb' : (errors.full_name ? '#fef2f2' : 'white')
              }}
              onFocus={(e) => e.target.style.borderColor = errors.full_name ? '#ef4444' : '#10b981'}
              onBlur={(e) => e.target.style.borderColor = errors.full_name ? '#fecaca' : '#e5e7eb'}
              required
            />
            {errors.full_name && (
              <p style={{
                color: '#dc2626',
                fontSize: '0.875rem',
                margin: '0.25rem 0 0 0',
                fontWeight: '500'
              }}>
                {errors.full_name}
              </p>
            )}
          </div>

          {/* Username Field */}
          <div style={{ marginBottom: '1rem' }}>
            <label style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '0.5rem'
            }}>
              Tên người dùng:
            </label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => handleInputChange('username', e.target.value)}
              placeholder="Nhập tên người dùng"
              disabled={loading}
              style={{
                width: '100%',
                padding: '0.75rem',
                border: `2px solid ${errors.username ? '#fecaca' : '#e5e7eb'}`,
                borderRadius: '8px',
                fontSize: '1rem',
                outline: 'none',
                transition: 'border-color 0.2s',
                backgroundColor: loading ? '#f9fafb' : (errors.username ? '#fef2f2' : 'white')
              }}
              onFocus={(e) => e.target.style.borderColor = errors.username ? '#ef4444' : '#10b981'}
              onBlur={(e) => e.target.style.borderColor = errors.username ? '#fecaca' : '#e5e7eb'}
              required
            />
            {errors.username && (
              <p style={{
                color: '#dc2626',
                fontSize: '0.875rem',
                margin: '0.25rem 0 0 0',
                fontWeight: '500'
              }}>
                {errors.username}
              </p>
            )}
          </div>

          {/* Email Field */}
          <div style={{ marginBottom: '1rem' }}>
            <label style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '0.5rem'
            }}>
              Email:
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              placeholder="your@email.com"
              disabled={loading}
              style={{
                width: '100%',
                padding: '0.75rem',
                border: `2px solid ${errors.email ? '#fecaca' : '#e5e7eb'}`,
                borderRadius: '8px',
                fontSize: '1rem',
                outline: 'none',
                transition: 'border-color 0.2s',
                backgroundColor: loading ? '#f9fafb' : (errors.email ? '#fef2f2' : 'white')
              }}
              onFocus={(e) => e.target.style.borderColor = errors.email ? '#ef4444' : '#10b981'}
              onBlur={(e) => e.target.style.borderColor = errors.email ? '#fecaca' : '#e5e7eb'}
              required
            />
            {errors.email && (
              <p style={{
                color: '#dc2626',
                fontSize: '0.875rem',
                margin: '0.25rem 0 0 0',
                fontWeight: '500'
              }}>
                {errors.email}
              </p>
            )}
          </div>

          {/* Password Field */}
          <div style={{ marginBottom: '1rem' }}>
            <label style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '0.5rem'
            }}>
              Mật khẩu:
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                placeholder="Nhập mật khẩu"
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  paddingRight: '3rem',
                  border: `2px solid ${errors.password ? '#fecaca' : '#e5e7eb'}`,
                  borderRadius: '8px',
                  fontSize: '1rem',
                  outline: 'none',
                  transition: 'border-color 0.2s',
                  backgroundColor: loading ? '#f9fafb' : (errors.password ? '#fef2f2' : 'white')
                }}
                onFocus={(e) => e.target.style.borderColor = errors.password ? '#ef4444' : '#10b981'}
                onBlur={(e) => e.target.style.borderColor = errors.password ? '#fecaca' : '#e5e7eb'}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                disabled={loading}
                style={{
                  position: 'absolute',
                  right: '0.75rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: '#6b7280',
                  fontSize: '1.2rem'
                }}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
            
            {/* Password Strength Indicator */}
            {formData.password && (
              <div style={{ marginTop: '0.5rem' }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  fontSize: '0.75rem',
                  marginBottom: '0.25rem'
                }}>
                  <span style={{ color: '#6b7280' }}>Độ mạnh mật khẩu:</span>
                  <span style={{ color: passwordStrength.color, fontWeight: '500' }}>
                    {passwordStrength.text}
                  </span>
                </div>
                <div style={{
                  width: '100%',
                  height: '4px',
                  backgroundColor: '#e5e7eb',
                  borderRadius: '2px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    height: '100%',
                    backgroundColor: passwordStrength.color,
                    width: passwordStrength.level === 'weak' ? '33%' : 
                           passwordStrength.level === 'medium' ? '66%' : '100%',
                    transition: 'width 0.3s ease'
                  }} />
                </div>
              </div>
            )}
            
            {errors.password && (
              <p style={{
                color: '#dc2626',
                fontSize: '0.875rem',
                margin: '0.25rem 0 0 0',
                fontWeight: '500'
              }}>
                {errors.password}
              </p>
            )}
          </div>

          {/* Confirm Password Field */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '0.5rem'
            }}>
              Xác nhận mật khẩu:
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                placeholder="Nhập lại mật khẩu"
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  paddingRight: '3rem',
                  border: `2px solid ${errors.confirmPassword ? '#fecaca' : '#e5e7eb'}`,
                  borderRadius: '8px',
                  fontSize: '1rem',
                  outline: 'none',
                  transition: 'border-color 0.2s',
                  backgroundColor: loading ? '#f9fafb' : (errors.confirmPassword ? '#fef2f2' : 'white')
                }}
                onFocus={(e) => e.target.style.borderColor = errors.confirmPassword ? '#ef4444' : '#10b981'}
                onBlur={(e) => e.target.style.borderColor = errors.confirmPassword ? '#fecaca' : '#e5e7eb'}
                required
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                disabled={loading}
                style={{
                  position: 'absolute',
                  right: '0.75rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: '#6b7280',
                  fontSize: '1.2rem'
                }}
              >
                {showConfirmPassword ? '🙈' : '👁️'}
              </button>
            </div>
            {errors.confirmPassword && (
              <p style={{
                color: '#dc2626',
                fontSize: '0.875rem',
                margin: '0.25rem 0 0 0',
                fontWeight: '500'
              }}>
                {errors.confirmPassword}
              </p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '0.75rem',
              backgroundColor: loading ? '#9ca3af' : '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.2s',
              marginBottom: '1rem'
            }}
            onMouseOver={(e) => {
              if (!loading) e.target.style.backgroundColor = '#059669';
            }}
            onMouseOut={(e) => {
              if (!loading) e.target.style.backgroundColor = '#10b981';
            }}
          >
            {loading ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid transparent',
                  borderTop: '2px solid #ffffff',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }} />
                Đang xử lý...
              </div>
            ) : (
              'Đăng ký'
            )}
          </button>

          {/* Login Link */}
          <div style={{ textAlign: 'center' }}>
            <p style={{
              color: '#64748b',
              fontSize: '0.875rem'
            }}>
              Đã có tài khoản?{' '}
              <Link 
                to="/login" 
                style={{
                  color: '#10b981',
                  textDecoration: 'none',
                  fontWeight: '600'
                }}
                onMouseOver={(e) => e.target.style.textDecoration = 'underline'}
                onMouseOut={(e) => e.target.style.textDecoration = 'none'}
              >
                Đăng nhập ngay
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}; 