/**
 * Main App component with routing for AI Code Reviewer frontend.
 * 
 * This component sets up the main application structure with React Router
 * for navigation between different pages and views.
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ScanList from './pages/ScanList';
import ReportView from './pages/ReportView';
import CreateScan from './pages/CreateScan';
import TestPage from './pages/TestPage';
import Dashboard from './pages/Dashboard';
import './styles/globals.css';

interface AppProps {
  className?: string;
}

/**
 * Header component for navigation.
 * 
 * Returns:
 *   JSX.Element: Rendered header component
 */
const Header: React.FC = () => {
  return (
    <header className="bg-primary" style={{
      color: 'var(--color-text-inverse)',
      padding: 'var(--spacing-md) var(--spacing-lg)',
      borderBottom: '1px solid var(--color-border)',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        maxWidth: '1200px',
        margin: '0 auto',
      }}>
        <div>
          <h1 style={{ 
            fontSize: 'var(--font-size-xl)', 
            margin: 0,
            fontWeight: 'var(--font-weight-bold)'
          }}>
            AI Code Reviewer
          </h1>
          <div style={{ 
            fontSize: 'var(--font-size-sm)', 
            opacity: 0.9, 
            marginTop: 'var(--spacing-xs)' 
          }}>
            Multi-Agent Code Analysis Platform
          </div>
        </div>
        <nav className="flex gap-sm">
          <a
            href="/dashboard"
            className="btn btn-ghost"
            style={{
              color: 'var(--color-text-inverse)',
              backgroundColor: 'rgba(255,255,255,0.1)',
            }}
          >
            📊 Dashboard
          </a>
          <a
            href="/scans"
            className="btn btn-ghost"
            style={{
              color: 'var(--color-text-inverse)',
              backgroundColor: 'rgba(255,255,255,0.1)',
            }}
          >
            View Scans
          </a>
          <a
            href="/create-scan"
            className="btn btn-secondary"
          >
            New Scan
          </a>
        </nav>
      </div>
    </header>
  );
};

/**
 * Footer component.
 * 
 * Returns:
 *   JSX.Element: Rendered footer component
 */
const Footer: React.FC = () => {
  return (
    <footer className="bg-surface border" style={{
      borderTop: '1px solid var(--color-border)',
      padding: 'var(--spacing-md) var(--spacing-lg)',
      marginTop: 'auto',
      textAlign: 'center',
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div className="text-secondary" style={{ fontSize: 'var(--font-size-sm)' }}>
          AI Code Reviewer - Multi-Agent Code Analysis Platform
        </div>
        <div className="text-muted" style={{ 
          marginTop: 'var(--spacing-xs)', 
          fontSize: 'var(--font-size-xs)' 
        }}>
          Powered by LangGraph, FastAPI, and React
        </div>
      </div>
    </footer>
  );
};

/**
 * Layout component that wraps pages with common elements.
 * 
 * Args:
 *   children: Child components to render
 * 
 * Returns:
 *   JSX.Element: Rendered layout component
 */
const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="flex flex-col" style={{
      minHeight: '100vh',
    }}>
      <Header />
      <main style={{
        flex: 1,
        maxWidth: '1200px',
        margin: '0 auto',
        width: '100%',
        padding: '0 var(--spacing-lg)',
      }}>
        {children}
      </main>
      <Footer />
    </div>
  );
};

/**
 * Home page component that redirects to scans list.
 * 
 * Returns:
 *   JSX.Element: Rendered home page component
 */
const HomePage: React.FC = () => {
  return <Navigate to="/scans" replace />;
};

/**
 * Not found page component.
 * 
 * Returns:
 *   JSX.Element: Rendered 404 page component
 */
const NotFoundPage: React.FC = () => {
  return (
    <Layout>
      <div className="text-center" style={{
        padding: 'var(--spacing-2xl) var(--spacing-lg)',
      }}>
        <h1 className="text-muted" style={{ 
          fontSize: 'var(--font-size-4xl)', 
          marginBottom: 'var(--spacing-md)' 
        }}>
          404
        </h1>
        <h2 className="text-primary" style={{ marginBottom: 'var(--spacing-md)' }}>
          Page Not Found
        </h2>
        <p className="text-secondary" style={{ marginBottom: 'var(--spacing-xl)' }}>
          The page you're looking for doesn't exist.
        </p>
        <a
          href="/scans"
          className="btn btn-primary"
        >
          Go to Scans
        </a>
      </div>
    </Layout>
  );
};

/**
 * Main App component with routing.
 * 
 * Args:
 *   className: Additional CSS classes
 * 
 * Returns:
 *   JSX.Element: Rendered application
 */
const App: React.FC<AppProps> = ({ className = '' }) => {
  console.log('App component rendering...');
  
  return (
    <div className={`app ${className}`}>
      <Router>
        <Routes>
          {/* Home route - redirects to dashboard */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          {/* Dashboard route */}
          <Route 
            path="/dashboard" 
            element={<Dashboard />}
          />
          
          {/* Test page for debugging */}
          <Route 
            path="/test" 
            element={
              <Layout>
                <TestPage />
              </Layout>
            } 
          />
          
          {/* Scans list route */}
          <Route 
            path="/scans" 
            element={
              <Layout>
                <ScanList />
              </Layout>
            } 
          />
          
          {/* Create scan route */}
          <Route 
            path="/create-scan" 
            element={
              <Layout>
                <CreateScan />
              </Layout>
            } 
          />
          
          {/* Report view route */}
          <Route 
            path="/reports/:scanId" 
            element={
              <Layout>
                <ReportView />
              </Layout>
            } 
          />
          
          {/* Legacy route support */}
          <Route path="/report/:scanId" element={<Navigate to="/reports/:scanId" replace />} />
          
          {/* Not found route */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Router>
    </div>
  );
};

export default App; 