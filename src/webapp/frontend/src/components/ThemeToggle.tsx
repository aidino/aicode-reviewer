/**
 * Theme Toggle component with smooth animations and modern design.
 * 
 * Provides a toggle button to switch between light/dark themes
 * with animated transitions and accessible design.
 */

import React from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme, type Theme } from './ThemeProvider';

interface ThemeToggleProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  variant?: 'button' | 'dropdown';
}

/**
 * Theme toggle button component.
 * 
 * Args:
 *   className: Additional CSS classes
 *   size: Size variant for the toggle
 *   showLabel: Whether to show theme labels
 *   variant: Display variant (button or dropdown)
 * 
 * Returns:
 *   JSX.Element: Rendered theme toggle component
 */
export const ThemeToggle: React.FC<ThemeToggleProps> = ({
  className = '',
  size = 'md',
  showLabel = false,
  variant = 'button'
}) => {
  const { theme, actualTheme, setTheme, toggleTheme } = useTheme();

  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12'
  };

  const iconSizes = {
    sm: 16,
    md: 20,
    lg: 24
  };

  const getThemeIcon = (themeType: Theme | 'current') => {
    const iconSize = iconSizes[size];
    
    switch (themeType) {
      case 'light':
        return <Sun size={iconSize} />;
      case 'dark':
        return <Moon size={iconSize} />;
      case 'auto':
        return <Monitor size={iconSize} />;
      case 'current':
        return actualTheme === 'light' ? <Sun size={iconSize} /> : <Moon size={iconSize} />;
      default:
        return <Sun size={iconSize} />;
    }
  };

  const getThemeLabel = (themeType: Theme) => {
    switch (themeType) {
      case 'light':
        return 'Light';
      case 'dark':
        return 'Dark';
      case 'auto':
        return 'Auto';
      default:
        return 'Light';
    }
  };

  if (variant === 'dropdown') {
    return (
      <div className={`relative ${className}`}>
        <div className="glass-overlay rounded-xl p-2">
          <div className="grid grid-cols-3 gap-1">
            {(['light', 'dark', 'auto'] as Theme[]).map((themeOption) => (
              <button
                key={themeOption}
                onClick={() => setTheme(themeOption)}
                className={`
                  relative flex flex-col items-center gap-2 p-3 rounded-lg
                  transition-all duration-200 ease-out
                  ${theme === themeOption 
                    ? 'bg-primary-600 text-white shadow-lg' 
                    : 'hover:bg-surface-hover text-text-secondary hover:text-text-primary'
                  }
                `}
                aria-label={`Switch to ${getThemeLabel(themeOption)} theme`}
              >
                <div className="transition-transform duration-200 hover:scale-110">
                  {getThemeIcon(themeOption)}
                </div>
                {showLabel && (
                  <span className="text-xs font-medium">
                    {getThemeLabel(themeOption)}
                  </span>
                )}
                {theme === themeOption && (
                  <div className="absolute inset-0 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg opacity-20" />
                )}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <button
      onClick={toggleTheme}
      className={`
        ${sizeClasses[size]}
        relative flex items-center justify-center
        glass-overlay rounded-xl
        transition-all duration-300 ease-out
        hover:scale-105 hover:shadow-lg
        active:scale-95
        focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
        group
        ${className}
      `}
      aria-label={`Switch to ${actualTheme === 'light' ? 'dark' : 'light'} theme`}
      title={`Current: ${getThemeLabel(theme)} • Click to toggle`}
    >
      {/* Background Gradient Animation */}
      <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-primary-500/10 to-accent-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      
      {/* Icon Container with Rotation Animation */}
      <div className="relative transition-transform duration-500 ease-out group-hover:rotate-12">
        {getThemeIcon('current')}
      </div>

      {/* Ripple Effect on Click */}
      <div className="absolute inset-0 rounded-xl overflow-hidden">
        <div className="absolute inset-0 bg-white/20 scale-0 rounded-xl group-active:scale-100 transition-transform duration-200" />
      </div>

      {/* Theme Indicator Ring */}
      <div className={`
        absolute inset-0 rounded-xl border-2 transition-all duration-300
        ${actualTheme === 'light' 
          ? 'border-yellow-400/30 group-hover:border-yellow-400/60' 
          : 'border-blue-400/30 group-hover:border-blue-400/60'
        }
      `} />
    </button>
  );
};

/**
 * Compact theme toggle for use in navigation bars.
 * 
 * Args:
 *   className: Additional CSS classes
 * 
 * Returns:
 *   JSX.Element: Rendered compact theme toggle
 */
export const CompactThemeToggle: React.FC<{ className?: string }> = ({ 
  className = '' 
}) => {
  return (
    <ThemeToggle 
      size="sm" 
      className={className}
      variant="button"
    />
  );
};

/**
 * Theme selector dropdown with all options.
 * 
 * Args:
 *   className: Additional CSS classes
 *   showLabels: Whether to show theme option labels
 * 
 * Returns:
 *   JSX.Element: Rendered theme selector dropdown
 */
export const ThemeSelector: React.FC<{ 
  className?: string;
  showLabels?: boolean;
}> = ({ 
  className = '',
  showLabels = true
}) => {
  return (
    <ThemeToggle 
      size="md"
      className={className}
      variant="dropdown"
      showLabel={showLabels}
    />
  );
};

export default ThemeToggle; 