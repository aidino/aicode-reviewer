/**
 * Authentication Modal Component.
 * 
 * Modal component kết hợp LoginForm và RegisterForm với switching capability.
 * Sử dụng Soft UI design và modern animations.
 */

import React, { useState, useEffect } from 'react';
import { LoginForm } from './LoginForm';
import { RegisterForm } from './RegisterForm';
import { useAuth } from '../../contexts/AuthContext';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: 'login' | 'register';
  onSuccess?: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  initialMode = 'login',
  onSuccess,
}) => {
  const { loading } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);

  // Reset mode when modal opens
  useEffect(() => {
    if (isOpen) {
      setMode(initialMode);
    }
  }, [isOpen, initialMode]);

  // Handle form success
  const handleSuccess = () => {
    onSuccess?.();
    onClose();
  };

  // Handle ESC key
  useEffect(() => {
    const handleEsc = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !loading) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose, loading]);

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity duration-300"
        onClick={!loading ? onClose : undefined}
      />

      {/* Modal Container */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div 
          className={`
            relative bg-gray-50 rounded-3xl shadow-soft-3xl max-w-md w-full
            transform transition-all duration-300
            ${isOpen ? 'scale-100 opacity-100' : 'scale-95 opacity-0'}
          `}
        >
          {/* Close Button */}
          {!loading && (
            <button
              onClick={onClose}
              className="absolute top-4 right-4 z-10 p-2 rounded-full hover:bg-gray-200 transition-colors"
              aria-label="Đóng"
            >
              <i className="fas fa-times text-gray-500 hover:text-gray-700"></i>
            </button>
          )}

          {/* Mode Tabs */}
          <div className="p-6 pb-0">
            <div className="flex bg-gray-200 rounded-2xl p-1 mb-6">
              <button
                onClick={() => setMode('login')}
                disabled={loading}
                className={`
                  flex-1 py-2 px-4 rounded-xl text-sm font-medium transition-all duration-300
                  ${mode === 'login'
                    ? 'bg-white text-gray-900 shadow-soft-xl'
                    : 'text-gray-500 hover:text-gray-700'
                  }
                `}
              >
                Đăng nhập
              </button>
              <button
                onClick={() => setMode('register')}
                disabled={loading}
                className={`
                  flex-1 py-2 px-4 rounded-xl text-sm font-medium transition-all duration-300
                  ${mode === 'register'
                    ? 'bg-white text-gray-900 shadow-soft-xl'
                    : 'text-gray-500 hover:text-gray-700'
                  }
                `}
              >
                Đăng ký
              </button>
            </div>
          </div>

          {/* Form Content */}
          <div className="px-6 pb-6">
            {mode === 'login' ? (
              <LoginForm
                onSuccess={handleSuccess}
                onSwitchToRegister={() => setMode('register')}
                className="shadow-none p-0 bg-transparent"
              />
            ) : (
              <RegisterForm
                onSuccess={handleSuccess}
                onSwitchToLogin={() => setMode('login')}
                className="shadow-none p-0 bg-transparent"
              />
            )}
          </div>

          {/* Loading Overlay */}
          {loading && (
            <div className="absolute inset-0 bg-white bg-opacity-80 rounded-3xl flex items-center justify-center">
              <div className="flex flex-col items-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                <p className="text-gray-600 font-medium">
                  {mode === 'login' ? 'Đang đăng nhập...' : 'Đang đăng ký...'}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}; 