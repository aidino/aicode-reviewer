/**
 * Unit tests for ThemeProvider component.
 * 
 * Tests theme management, persistence, and system theme detection.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { ThemeProvider, useTheme, type Theme } from '../ThemeProvider';

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
});

// Mock matchMedia
const mockMatchMedia = vi.fn();
Object.defineProperty(window, 'matchMedia', {
  value: mockMatchMedia,
  writable: true,
});

// Test component that uses theme context
const TestComponent: React.FC = () => {
  const { theme, actualTheme, setTheme, toggleTheme } = useTheme();
  
  return (
    <div>
      <div data-testid="current-theme">{theme}</div>
      <div data-testid="actual-theme">{actualTheme}</div>
      <button data-testid="toggle-theme" onClick={toggleTheme}>
        Toggle Theme
      </button>
      <button data-testid="set-light" onClick={() => setTheme('light')}>
        Set Light
      </button>
      <button data-testid="set-dark" onClick={() => setTheme('dark')}>
        Set Dark
      </button>
      <button data-testid="set-auto" onClick={() => setTheme('auto')}>
        Set Auto
      </button>
    </div>
  );
};

describe('ThemeProvider', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
    mockMatchMedia.mockReturnValue({
      matches: false,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    });
    // Remove any existing data-theme attribute
    document.documentElement.removeAttribute('data-theme');
  });

  describe('Expected Use Cases', () => {
    it('should provide theme context with default auto theme', () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      expect(screen.getByTestId('current-theme')).toHaveTextContent('auto');
      expect(screen.getByTestId('actual-theme')).toHaveTextContent('light');
    });

    it('should apply theme to document element', () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    });

    it('should persist theme changes to localStorage', () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      fireEvent.click(screen.getByTestId('set-dark'));

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('theme', 'dark');
      expect(screen.getByTestId('current-theme')).toHaveTextContent('dark');
      expect(screen.getByTestId('actual-theme')).toHaveTextContent('dark');
    });

    it('should toggle between light and dark themes', () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Start with light theme (auto -> light by default)
      fireEvent.click(screen.getByTestId('set-light'));
      expect(screen.getByTestId('current-theme')).toHaveTextContent('light');

      // Toggle to dark
      fireEvent.click(screen.getByTestId('toggle-theme'));
      expect(screen.getByTestId('current-theme')).toHaveTextContent('dark');

      // Toggle back to light
      fireEvent.click(screen.getByTestId('toggle-theme'));
      expect(screen.getByTestId('current-theme')).toHaveTextContent('light');
    });

    it('should load stored theme from localStorage', () => {
      mockLocalStorage.getItem.mockReturnValue('dark');

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      expect(screen.getByTestId('current-theme')).toHaveTextContent('dark');
      expect(screen.getByTestId('actual-theme')).toHaveTextContent('dark');
    });

    it('should respect system dark mode preference when using auto', () => {
      mockMatchMedia.mockReturnValue({
        matches: true, // System prefers dark mode
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      });

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      expect(screen.getByTestId('current-theme')).toHaveTextContent('auto');
      expect(screen.getByTestId('actual-theme')).toHaveTextContent('dark');
    });
  });

  describe('Edge Cases', () => {
    it('should handle invalid stored theme gracefully', () => {
      mockLocalStorage.getItem.mockReturnValue('invalid-theme');

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Should fall back to auto theme
      expect(screen.getByTestId('current-theme')).toHaveTextContent('auto');
    });

    it('should use default theme when provided', () => {
      render(
        <ThemeProvider defaultTheme="dark">
          <TestComponent />
        </ThemeProvider>
      );

      expect(screen.getByTestId('current-theme')).toHaveTextContent('dark');
      expect(screen.getByTestId('actual-theme')).toHaveTextContent('dark');
    });

    it('should handle toggle from auto theme correctly', () => {
      // System prefers light mode
      mockMatchMedia.mockReturnValue({
        matches: false,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      });

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Start with auto (which resolves to light)
      expect(screen.getByTestId('current-theme')).toHaveTextContent('auto');
      expect(screen.getByTestId('actual-theme')).toHaveTextContent('light');

      // Toggle should switch to dark (opposite of system preference)
      fireEvent.click(screen.getByTestId('toggle-theme'));
      expect(screen.getByTestId('current-theme')).toHaveTextContent('dark');
    });

    it('should handle system theme change when using auto', async () => {
      const mockAddEventListener = jest.fn();
      const mockRemoveEventListener = jest.fn();
      
      mockMatchMedia.mockReturnValue({
        matches: false,
        addEventListener: mockAddEventListener,
        removeEventListener: mockRemoveEventListener,
      });

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Verify listener was added
      expect(mockAddEventListener).toHaveBeenCalledWith('change', expect.any(Function));

      // Simulate system theme change
      const changeHandler = mockAddEventListener.mock.calls[0][1];
      changeHandler({ matches: true }); // System switched to dark mode

      await waitFor(() => {
        expect(screen.getByTestId('actual-theme')).toHaveTextContent('dark');
      });
    });

    it('should clean up system theme listener on unmount', () => {
      const mockAddEventListener = jest.fn();
      const mockRemoveEventListener = jest.fn();
      
      mockMatchMedia.mockReturnValue({
        matches: false,
        addEventListener: mockAddEventListener,
        removeEventListener: mockRemoveEventListener,
      });

      const { unmount } = render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      unmount();

      expect(mockRemoveEventListener).toHaveBeenCalledWith('change', expect.any(Function));
    });
  });

  describe('Failure Cases', () => {
    it('should throw error when useTheme is used outside provider', () => {
      // Mock console.error to avoid cluttering test output
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => {
        render(<TestComponent />);
      }).toThrow('useTheme must be used within a ThemeProvider');

      consoleSpy.mockRestore();
    });

    it('should handle missing localStorage gracefully', () => {
      // Mock localStorage to be undefined
      Object.defineProperty(window, 'localStorage', {
        value: undefined,
        writable: true,
      });

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Should still work with default theme
      expect(screen.getByTestId('current-theme')).toHaveTextContent('auto');

      // Restore localStorage
      Object.defineProperty(window, 'localStorage', {
        value: mockLocalStorage,
        writable: true,
      });
    });

    it('should handle missing matchMedia gracefully', () => {
      // Mock matchMedia to be undefined
      Object.defineProperty(window, 'matchMedia', {
        value: undefined,
        writable: true,
      });

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Should still work with default light theme
      expect(screen.getByTestId('current-theme')).toHaveTextContent('auto');
      expect(screen.getByTestId('actual-theme')).toHaveTextContent('light');

      // Restore matchMedia
      Object.defineProperty(window, 'matchMedia', {
        value: mockMatchMedia,
        writable: true,
      });
    });

    it('should handle localStorage errors gracefully', () => {
      mockLocalStorage.setItem.mockImplementation(() => {
        throw new Error('Storage quota exceeded');
      });

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Should not crash when trying to set theme
      expect(() => {
        fireEvent.click(screen.getByTestId('set-dark'));
      }).not.toThrow();
    });
  });
}); 