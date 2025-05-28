/**
 * LoginPageSimple - Version thật sự với API calls và logging
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export const LoginPageSimple: React.FC = () => {
  const navigate = useNavigate();
  const { login, loading, error } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log('🚀 [Frontend] Login form submitted');
    console.log('📧 [Frontend] Email:', formData.email);
    console.log('🔐 [Frontend] Password length:', formData.password.length);
    console.log('🌐 [Frontend] API Base URL:', (import.meta as any).env?.VITE_API_BASE_URL || 'undefined');
    
    try {
      console.log('📨 [Frontend] Calling login API...');
      await login({
        username: formData.email, 
        password: formData.password
      });
      
      console.log('✅ [Frontend] Login successful, navigating to dashboard...');
      navigate('/dashboard');
      
    } catch (error) {
      console.error('❌ [Frontend] Login error:', error);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f8fafc',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        width: '100%',
        maxWidth: '400px'
      }}>
        <h1 style={{
          fontSize: '2rem',
          fontWeight: 'bold',
          marginBottom: '0.5rem',
          textAlign: 'center',
          color: '#1f2937'
        }}>
          🔐 Đăng nhập
        </h1>
        
        <p style={{
          color: '#6b7280',
          textAlign: 'center',
          marginBottom: '2rem',
          fontSize: '14px'
        }}>
          Chào mừng bạn quay lại với AI Code Reviewer
        </p>

        {error && (
          <div style={{
            marginBottom: '1rem',
            padding: '0.75rem',
            backgroundColor: '#fee2e2',
            borderRadius: '8px',
            border: '1px solid #fecaca',
            color: '#b91c1c',
            fontSize: '14px'
          }}>
            ❌ {error.detail}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontWeight: '600',
              color: '#374151',
              fontSize: '14px'
            }}>
              Email:
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              placeholder="Nhập email của bạn"
              style={{
                width: '100%',
                height: '48px',
                padding: '0 16px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '16px',
                backgroundColor: 'white',
                boxSizing: 'border-box'
              }}
              required
              disabled={loading}
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontWeight: '600',
              color: '#374151',
              fontSize: '14px'
            }}>
              Mật khẩu:
            </label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
              placeholder="Nhập mật khẩu"
              style={{
                width: '100%',
                height: '48px',
                padding: '0 16px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '16px',
                backgroundColor: 'white',
                boxSizing: 'border-box'
              }}
              required
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              height: '48px',
              backgroundColor: loading ? '#9ca3af' : '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => {
              if (!loading) e.currentTarget.style.backgroundColor = '#1d4ed8';
            }}
            onMouseLeave={(e) => {
              if (!loading) e.currentTarget.style.backgroundColor = '#2563eb';
            }}
          >
            {loading ? '⏳ Đang đăng nhập...' : 'Đăng nhập'}
          </button>
        </form>

        <div style={{
          marginTop: '1.5rem',
          textAlign: 'center'
        }}>
          <p style={{
            fontSize: '14px',
            color: '#6b7280'
          }}>
            Chưa có tài khoản?{' '}
            <a
              href="/register"
              style={{
                color: '#2563eb',
                textDecoration: 'none',
                fontWeight: '600'
              }}
            >
              Đăng ký ngay
            </a>
          </p>
        </div>

        <div style={{
          marginTop: '1rem',
          padding: '1rem',
          backgroundColor: '#f3f4f6',
          borderRadius: '8px',
          fontSize: '12px',
          color: '#6b7280'
        }}>
          <strong>Debug Info:</strong><br/>
          Email: {formData.email}<br/>
          Password: {formData.password ? '••••••••' : '(empty)'}<br/>
          Loading: {loading ? 'Yes' : 'No'}<br/>
          Error: {error?.detail || 'None'}<br/>
          API URL: {(import.meta as any).env?.VITE_API_BASE_URL || 'undefined'}
        </div>
      </div>
    </div>
  );
}; 