/**
 * Protected Route Component.
 * 
 * Component để bảo vệ các routes cần authentication.
 * Redirect về login nếu user chưa authenticated.
 */

import React, { useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { AuthModal } from './AuthModal';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  showModal?: boolean;
  redirectPath?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  fallback,
  showModal = false,
  redirectPath = '/login',
}) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600 font-medium">Đang kiểm tra đăng nhập...</p>
        </div>
      </div>
    );
  }

  // If authenticated, render children
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // If not authenticated, show fallback or modal
  if (fallback) {
    return <>{fallback}</>;
  }

  if (showModal) {
    return (
      <>
        {/* Default unauthorized content */}
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
          <div className="max-w-md w-full text-center">
            <div className="bg-white rounded-3xl shadow-soft-xl p-8">
              <div className="mb-6">
                <i className="fas fa-lock text-6xl text-gray-400 mb-4"></i>
                <h1 className="text-2xl font-bold text-gray-900 mb-2">
                  Cần đăng nhập
                </h1>
                <p className="text-gray-600">
                  Bạn cần đăng nhập để truy cập trang này
                </p>
              </div>
              
              <button
                onClick={() => setShowAuthModal(true)}
                className="w-full py-3 px-4 rounded-xl font-medium bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white transform hover:scale-105 active:scale-95 transition-all duration-300 shadow-soft-2xl hover:shadow-soft-3xl"
              >
                Đăng nhập ngay
              </button>
            </div>
          </div>
        </div>

        {/* Auth Modal */}
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          initialMode="login"
          onSuccess={() => setShowAuthModal(false)}
        />
      </>
    );
  }

  // Redirect to login page using React Router
  return <Navigate to={redirectPath} state={{ from: location }} replace />;
};

/**
 * Higher-order component version của ProtectedRoute.
 * 
 * Usage:
 *   const ProtectedComponent = withAuth(MyComponent);
 */
export const withAuth = <P extends object>(
  Component: React.ComponentType<P>,
  options: Omit<ProtectedRouteProps, 'children'> = {}
) => {
  return (props: P) => (
    <ProtectedRoute {...options}>
      <Component {...props} />
    </ProtectedRoute>
  );
}; 