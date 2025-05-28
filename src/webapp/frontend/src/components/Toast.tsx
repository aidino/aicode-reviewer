/**
 * Modern Toast notification system with animations and glassmorphism.
 * 
 * Provides toast notifications for user feedback with multiple types
 * and smooth animations.
 */

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastContextType {
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | null>(null);

/**
 * Hook to access toast context.
 * 
 * Returns:
 *   ToastContextType: Toast context with functions to manage toasts
 * 
 * Throws:
 *   Error: If used outside of ToastProvider
 */
export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

/**
 * Helper hooks for common toast types.
 */
export const useToastHelpers = () => {
  const { addToast } = useToast();

  const success = useCallback((title: string, message?: string, duration?: number) => {
    return addToast({ type: 'success', title, message, duration });
  }, [addToast]);

  const error = useCallback((title: string, message?: string, duration?: number) => {
    return addToast({ type: 'error', title, message, duration });
  }, [addToast]);

  const warning = useCallback((title: string, message?: string, duration?: number) => {
    return addToast({ type: 'warning', title, message, duration });
  }, [addToast]);

  const info = useCallback((title: string, message?: string, duration?: number) => {
    return addToast({ type: 'info', title, message, duration });
  }, [addToast]);

  return { success, error, warning, info };
};

/**
 * Generate unique ID for toasts.
 * 
 * Returns:
 *   string: Unique toast ID
 */
const generateId = (): string => {
  return `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Get icon component for toast type.
 * 
 * Args:
 *   type: Toast type
 * 
 * Returns:
 *   JSX.Element: Icon component
 */
const getToastIcon = (type: ToastType) => {
  const iconProps = { size: 20 };
  
  switch (type) {
    case 'success':
      return <CheckCircle {...iconProps} className="text-green-500" />;
    case 'error':
      return <AlertCircle {...iconProps} className="text-red-500" />;
    case 'warning':
      return <AlertTriangle {...iconProps} className="text-yellow-500" />;
    case 'info':
      return <Info {...iconProps} className="text-blue-500" />;
    default:
      return <Info {...iconProps} />;
  }
};

/**
 * Get CSS classes for toast type.
 * 
 * Args:
 *   type: Toast type
 * 
 * Returns:
 *   string: CSS classes for toast styling
 */
const getToastClasses = (type: ToastType): string => {
  const baseClasses = 'border-l-4';
  
  switch (type) {
    case 'success':
      return `${baseClasses} border-green-500 bg-green-50`;
    case 'error':
      return `${baseClasses} border-red-500 bg-red-50`;
    case 'warning':
      return `${baseClasses} border-yellow-500 bg-yellow-50`;
    case 'info':
      return `${baseClasses} border-blue-500 bg-blue-50`;
    default:
      return baseClasses;
  }
};

interface ToastItemProps {
  toast: Toast;
  onRemove: (id: string) => void;
}

/**
 * Individual toast item component.
 * 
 * Args:
 *   toast: Toast data
 *   onRemove: Function to remove toast
 * 
 * Returns:
 *   JSX.Element: Rendered toast item
 */
const ToastItem: React.FC<ToastItemProps> = ({ toast, onRemove }) => {
  const getIcon = () => {
    switch (toast.type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-[#508D4E]" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      case 'info':
        return <Info className="w-5 h-5 text-[#508D4E]" />;
    }
  };

  const getTypeClasses = () => {
    const baseClasses = "border-l-4";
    switch (toast.type) {
      case 'success':
        return `${baseClasses} border-[#508D4E] bg-[#D6EFD8]`;
      case 'error':
        return `${baseClasses} border-red-600 bg-white`;
      case 'warning':
        return `${baseClasses} border-yellow-600 bg-white`;
      case 'info':
        return `${baseClasses} border-[#508D4E] bg-[#D6EFD8]`;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className={`
        ${getTypeClasses()}
        rounded-lg shadow-lg p-4
        border border-[#80AF81] bg-white
      `}
      style={{ boxShadow: '0 8px 32px rgba(26,83,25,0.13)' }}
    >
      <div className="flex items-start">
        <div className="flex-shrink-0">
          {getIcon()}
        </div>
        
        <div className="ml-3 flex-1 min-w-0">
          <p className="text-sm font-semibold text-[#1A5319]">
            {toast.title}
          </p>
          {toast.message && (
            <p className="mt-1 text-sm text-[#508D4E]">
              {toast.message}
            </p>
          )}
        </div>
        
        <button
          onClick={() => onRemove(toast.id)}
          className="flex-shrink-0 ml-3 p-1 rounded-md hover:bg-[#D6EFD8] transition-colors"
          aria-label="Close notification"
        >
          <X className="w-4 h-4 text-[#508D4E]" />
        </button>
      </div>
    </motion.div>
  );
};

interface ToastProviderProps {
  children: React.ReactNode;
}

/**
 * Toast Provider component that manages toast state and provides context.
 * 
 * Args:
 *   children: Child components to wrap with toast context
 * 
 * Returns:
 *   JSX.Element: Rendered toast provider with toast container
 */
export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast = { ...toast, id };
    setToasts(prev => [...prev, newToast]);

    // Auto remove after duration (default 5 seconds)
    setTimeout(() => {
      removeToast(id);
    }, toast.duration || 5000);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
};

interface ToastContainerProps {
  toasts: Toast[];
  onRemove: (id: string) => void;
}

const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onRemove }) => {
  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm w-full space-y-2">
      <AnimatePresence>
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onRemove={onRemove} />
        ))}
      </AnimatePresence>
    </div>
  );
}; 