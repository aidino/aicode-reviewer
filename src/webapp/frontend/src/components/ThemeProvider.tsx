/**
 * Theme Provider for managing light/dark mode and theme preferences.
 * 
 * This component provides theme context throughout the application
 * and persists theme preferences in localStorage.
 */

import React, { createContext, useContext, useEffect, useState } from 'react';

export type Theme = 'light' | 'dark' | 'auto';

interface ThemeContextType {
  theme: Theme;
  actualTheme: 'light' | 'dark';
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

/**
 * Hook to access theme context.
 * 
 * Returns:
 *   ThemeContextType: Theme context with current theme and setter functions
 * 
 * Throws:
 *   Error: If used outside of ThemeProvider
 */
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

/**
 * Get system preference for color scheme.
 * 
 * Returns:
 *   'light' | 'dark': System color scheme preference
 */
const getSystemTheme = (): 'light' | 'dark' => {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

/**
 * Get stored theme preference from localStorage.
 * 
 * Returns:
 *   Theme: Stored theme preference or 'auto' as default
 */
const getStoredTheme = (): Theme => {
  if (typeof window === 'undefined') return 'auto';
  const stored = localStorage.getItem('theme') as Theme;
  return stored || 'auto';
};

/**
 * Calculate the actual theme to apply based on preference and system setting.
 * 
 * Args:
 *   theme: User's theme preference
 * 
 * Returns:
 *   'light' | 'dark': Actual theme to apply
 */
const getActualTheme = (theme: Theme): 'light' | 'dark' => {
  if (theme === 'auto') {
    return getSystemTheme();
  }
  return theme;
};

interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
}

/**
 * Theme Provider component that manages theme state and applies theme to document.
 * 
 * Args:
 *   children: Child components to wrap with theme context
 *   defaultTheme: Default theme preference (defaults to stored or 'auto')
 * 
 * Returns:
 *   JSX.Element: Rendered theme provider
 */
export const ThemeProvider: React.FC<ThemeProviderProps> = ({ 
  children, 
  defaultTheme 
}) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    return defaultTheme || getStoredTheme();
  });

  const [actualTheme, setActualTheme] = useState<'light' | 'dark'>(() => {
    return getActualTheme(theme);
  });

  /**
   * Set theme preference and persist to localStorage.
   * 
   * Args:
   *   newTheme: New theme preference to set
   */
  const setTheme = (newTheme: Theme): void => {
    setThemeState(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  /**
   * Toggle between light and dark themes.
   * If current theme is 'auto', toggle to opposite of system preference.
   */
  const toggleTheme = (): void => {
    if (theme === 'auto') {
      const systemTheme = getSystemTheme();
      setTheme(systemTheme === 'light' ? 'dark' : 'light');
    } else {
      setTheme(theme === 'light' ? 'dark' : 'light');
    }
  };

  // Update actual theme when theme preference changes
  useEffect(() => {
    const newActualTheme = getActualTheme(theme);
    setActualTheme(newActualTheme);

    // Apply theme to document
    document.documentElement.setAttribute('data-theme', newActualTheme);
    
    // Update meta theme-color for mobile browsers
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute(
        'content', 
        newActualTheme === 'dark' ? '#181A20' : '#ffffff'
      );
    }
  }, [theme]);

  // Listen for system theme changes when using 'auto'
  useEffect(() => {
    if (theme !== 'auto') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent): void => {
      const newActualTheme = e.matches ? 'dark' : 'light';
      setActualTheme(newActualTheme);
      document.documentElement.setAttribute('data-theme', newActualTheme);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  const value: ThemeContextType = {
    theme,
    actualTheme,
    setTheme,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}; 