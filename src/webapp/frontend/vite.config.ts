/**
 * Vite configuration for AI Code Reviewer frontend.
 * 
 * This configuration sets up Vite for React development with TypeScript support,
 * proxy configuration for backend API, build optimizations, and testing setup.
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // Server configuration for development
  server: {
    port: 5173,
    host: true,
    proxy: {
      // Proxy API calls to backend during development
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      },
      // Proxy health endpoint
      '/health': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  
  // Build configuration
  build: {
    outDir: 'dist',
    sourcemap: true,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
      },
    },
    // Rollup options
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          diagrams: ['mermaid'],
        },
      },
    },
  },
  
  // Environment variables
  envPrefix: 'REACT_APP_',
  
  // Define configuration
  define: {
    // Add any global constants here if needed
  },
  
  // Resolve configuration
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  
  // Optimizations
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom'],
  },
  
  // Test configuration
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
    css: true,
  },
}); 