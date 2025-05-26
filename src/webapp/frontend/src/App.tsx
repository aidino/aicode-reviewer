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

// Global styles
const globalStyles = `
  * {
    box-sizing: border-box;
  }
  
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: #f5f5f5;
    color: #333;
  }
  
  code {
    font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New', monospace;
  }
  
  h1, h2, h3, h4, h5, h6 {
    margin: 0;
    font-weight: 600;
  }
  
  button {
    font-family: inherit;
  }
  
  a {
    color: inherit;
    text-decoration: none;
  }
  
  table {
    border-collapse: collapse;
  }
`;

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
    <header style={{
      backgroundColor: '#1976d2',
      color: 'white',
      padding: '16px 20px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        maxWidth: '1200px',
        margin: '0 auto',
      }}>
        <div>
          <h1 style={{ fontSize: '1.5em', margin: 0 }}>
            AI Code Reviewer
          </h1>
          <div style={{ fontSize: '0.9em', opacity: 0.9, marginTop: '4px' }}>
            Multi-Agent Code Analysis Platform
          </div>
        </div>
        <nav style={{ display: 'flex', gap: '12px' }}>
          <a
            href="/scans"
            style={{
              color: 'white',
              textDecoration: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              backgroundColor: 'rgba(255,255,255,0.1)',
              transition: 'background-color 0.2s',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.2)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.1)';
            }}
          >
            View Scans
          </a>
          <a
            href="/create-scan"
            style={{
              color: 'white',
              textDecoration: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              backgroundColor: 'rgba(255,255,255,0.15)',
              transition: 'background-color 0.2s',
              fontWeight: '500',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.25)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.15)';
            }}
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
    <footer style={{
      backgroundColor: '#f8f9fa',
      borderTop: '1px solid #e9ecef',
      padding: '16px 20px',
      marginTop: 'auto',
      textAlign: 'center',
      color: '#666',
      fontSize: '0.9em',
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div>AI Code Reviewer - Multi-Agent Code Analysis Platform</div>
        <div style={{ marginTop: '4px', fontSize: '0.8em' }}>
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
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
    }}>
      <Header />
      <main style={{
        flex: 1,
        maxWidth: '1200px',
        margin: '0 auto',
        width: '100%',
        padding: '0 20px',
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
      <div style={{
        textAlign: 'center',
        padding: '80px 20px',
      }}>
        <h1 style={{ fontSize: '3em', marginBottom: '16px', color: '#666' }}>404</h1>
        <h2 style={{ marginBottom: '16px' }}>Page Not Found</h2>
        <p style={{ color: '#666', marginBottom: '24px' }}>
          The page you're looking for doesn't exist.
        </p>
        <a
          href="/scans"
          style={{
            display: 'inline-block',
            padding: '12px 24px',
            backgroundColor: '#1976d2',
            color: 'white',
            borderRadius: '4px',
            textDecoration: 'none',
            fontWeight: 'bold',
          }}
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
  return (
    <div className={`app ${className}`}>
      {/* Inject global styles */}
      <style>{globalStyles}</style>
      
      <Router>
        <Routes>
          {/* Home route - redirects to scans */}
          <Route path="/" element={<HomePage />} />
          
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