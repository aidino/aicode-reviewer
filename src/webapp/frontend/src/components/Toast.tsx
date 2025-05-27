/**
 * Modern Toast notification system with animations and glassmorphism.
 * 
 * Provides toast notifications for user feedback with multiple types
 * and smooth animations.
 */

import React, { createContext, useContext, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

/**
 * Hook to access toast context.
 * 
 * Returns:
 *   ToastContextType: Toast context with functions to manage toasts
 * 
 * Throws:
 *   Error: If used outside of ToastProvider
 */
export const useToast = (): ToastContextType => {
  const context = useContext(ToastContext);
  if (context === undefined) {
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
      return <CheckCircle {...iconProps} className="text-success-600" />;
    case 'error':
      return <AlertCircle {...iconProps} className="text-error-600" />;
    case 'warning':
      return <AlertTriangle {...iconProps} className="text-warning-600" />;
    case 'info':
      return <Info {...iconProps} className="text-accent-600" />;
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
      return `${baseClasses} border-success-500 bg-success-50 dark:bg-success-900/20`;
    case 'error':
      return `${baseClasses} border-error-500 bg-error-50 dark:bg-error-900/20`;
    case 'warning':
      return `${baseClasses} border-warning-500 bg-warning-50 dark:bg-warning-900/20`;
    case 'info':
      return `${baseClasses} border-accent-500 bg-accent-50 dark:bg-accent-900/20`;
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
  const { id, type, title, message, duration = 5000, action } = toast;

  // Auto-remove toast after duration
  React.useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onRemove(id);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [id, duration, onRemove]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -50, scale: 0.9 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={`
        relative overflow-hidden rounded-xl shadow-lg
        backdrop-filter backdrop-blur-sm
        ${getToastClasses(type)}
      `}
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          {/* Icon */}
          <div className="flex-shrink-0 mt-0.5">
            {getToastIcon(type)}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h4 className="font-medium text-primary text-sm">
                  {title}
                </h4>
                {message && (
                  <p className="mt-1 text-sm text-secondary line-clamp-2">
                    {message}
                  </p>
                )}
              </div>

              {/* Close Button */}
              <button
                onClick={() => onRemove(id)}
                className="flex-shrink-0 ml-3 p-1 rounded-md hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
                aria-label="Close notification"
              >
                <X size={16} className="text-muted" />
              </button>
            </div>

            {/* Action Button */}
            {action && (
              <div className="mt-3">
                <button
                  onClick={() => {
                    action.onClick();
                    onRemove(id);
                  }}
                  className="text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors"
                >
                  {action.label}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      {duration > 0 && (
        <motion.div
          className="absolute bottom-0 left-0 h-1 bg-current opacity-30"
          initial={{ width: '100%' }}
          animate={{ width: '0%' }}
          transition={{ duration: duration / 1000, ease: "linear" }}
        />
      )}
    </motion.div>
  );
};

interface ToastProviderProps {
  children: React.ReactNode;
  maxToasts?: number;
}

/**
 * Toast Provider component that manages toast state and provides context.
 * 
 * Args:
 *   children: Child components to wrap with toast context
 *   maxToasts: Maximum number of toasts to show simultaneously
 * 
 * Returns:
 *   JSX.Element: Rendered toast provider with toast container
 */
export const ToastProvider: React.FC<ToastProviderProps> = ({ 
  children, 
  maxToasts = 5 
}) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((toastData: Omit<Toast, 'id'>): string => {
    const id = generateId();
    const newToast: Toast = { ...toastData, id };

    setToasts(prev => {
      const updated = [newToast, ...prev];
      // Limit number of toasts
      return updated.slice(0, maxToasts);
    });

    return id;
  }, [maxToasts]);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const clearToasts = useCallback(() => {
    setToasts([]);
  }, []);

  const value: ToastContextType = {
    toasts,
    addToast,
    removeToast,
    clearToasts,
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      
      {/* Toast Container */}
      <div className="fixed top-4 right-4 z-50 space-y-3 max-w-sm w-full pointer-events-none">
        <AnimatePresence mode="popLayout">
          {toasts.map(toast => (
            <div key={toast.id} className="pointer-events-auto">
              <ToastItem toast={toast} onRemove={removeToast} />
            </div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}; 