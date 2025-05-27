/**
 * Main App component with routing for AI Code Reviewer frontend.
 * 
 * This component sets up the main application structure with React Router
 * for navigation between different pages and views.
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BarChart3, Scan, Plus, List } from 'lucide-react';
import ScanList from './pages/ScanList';
import ReportView from './pages/ReportView';
import CreateScan from './pages/CreateScan';
import TestPage from './pages/TestPage';
import Dashboard from './pages/Dashboard';
import { ThemeProvider } from './components/ThemeProvider';
import { CompactThemeToggle } from './components/ThemeToggle';
import { ToastProvider } from './components/Toast';
import './styles/theme.css';
import './styles/components.css';
import './styles/globals.css';

interface AppProps {
  className?: string;
}

/**
 * Modern navigation header with glassmorphism and micro-interactions.
 * 
 * Returns:
 *   JSX.Element: Rendered header component
 */
const Header: React.FC = () => {
  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { href: '/scans', label: 'Scans', icon: List },
    { href: '/create-scan', label: 'New Scan', icon: Plus, primary: true },
  ];

  return (
    <motion.header 
      className="glass-nav sticky top-0 z-50"
      style={{
        padding: 'var(--spacing-4) 0',
      }}
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      <div className="container flex items-center justify-between">
        {/* Logo and Brand */}
        <motion.div 
          className="flex items-center gap-4"
          initial={{ x: -50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-600 to-accent-500 flex items-center justify-center shadow-lg">
            <Scan size={20} className="text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gradient">
              AI Code Reviewer
            </h1>
            <div className="text-xs text-secondary opacity-80">
              Multi-Agent Analysis Platform
            </div>
          </div>
        </motion.div>

        {/* Navigation */}
        <motion.nav 
          className="flex items-center gap-2"
          initial={{ x: 50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          {navItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <motion.a
                key={item.href}
                href={item.href}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm
                  transition-all duration-200 relative overflow-hidden group
                  ${item.primary 
                    ? 'btn-primary' 
                    : 'btn-outline text-text-secondary hover:text-text-primary'
                  }
                `}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.3, delay: 0.4 + index * 0.1 }}
              >
                <Icon size={16} />
                <span className="hidden sm:inline">{item.label}</span>
                
                {/* Hover effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-500" />
              </motion.a>
            );
          })}
          
          {/* Theme Toggle */}
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3, delay: 0.8 }}
          >
            <CompactThemeToggle className="ml-2" />
          </motion.div>
        </motion.nav>
      </div>
    </motion.header>
  );
};

/**
 * Modern footer with glassmorphism effect.
 * 
 * Returns:
 *   JSX.Element: Rendered footer component
 */
const Footer: React.FC = () => {
  return (
    <motion.footer 
      className="glass-nav mt-auto"
      style={{
        padding: 'var(--spacing-6) 0',
      }}
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut", delay: 0.2 }}
    >
      <div className="container text-center">
        <motion.div 
          className="flex items-center justify-center gap-2 mb-2"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-primary-600 to-accent-500 flex items-center justify-center">
            <Scan size={12} className="text-white" />
          </div>
          <span className="font-semibold text-primary">AI Code Reviewer</span>
        </motion.div>
        
        <motion.div 
          className="text-sm text-secondary mb-1"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          Multi-Agent Code Analysis Platform
        </motion.div>
        
        <motion.div 
          className="text-xs text-muted flex items-center justify-center gap-2"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <span>Powered by</span>
          <span className="px-2 py-1 bg-surface rounded text-xs font-medium border">LangGraph</span>
          <span className="px-2 py-1 bg-surface rounded text-xs font-medium border">FastAPI</span>
          <span className="px-2 py-1 bg-surface rounded text-xs font-medium border">React</span>
        </motion.div>
      </div>
    </motion.footer>
  );
};

/**
 * Modern layout component with glassmorphism background and smooth transitions.
 * 
 * Args:
 *   children: Child components to render
 * 
 * Returns:
 *   JSX.Element: Rendered layout component
 */
const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden">
      {/* Background Gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-primary-50 via-background to-accent-50 opacity-60 dark:from-gray-900 dark:via-background-secondary dark:to-gray-800" />
      
      {/* Floating Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-primary-400/20 to-accent-400/20 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
        />
        <motion.div
          className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-success-400/20 to-warning-400/20 rounded-full blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            rotate: [360, 180, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "linear"
          }}
        />
      </div>

      <div className="relative z-10 flex flex-col min-h-screen">
        <Header />
        
        <motion.main 
          className="flex-1 container py-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          {children}
        </motion.main>
        
        <Footer />
      </div>
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
 * Modern 404 not found page with glassmorphism design.
 * 
 * Returns:
 *   JSX.Element: Rendered 404 page component
 */
const NotFoundPage: React.FC = () => {
  return (
    <Layout>
      <div className="flex items-center justify-center min-h-[60vh]">
        <motion.div 
          className="text-center max-w-md"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          <motion.div 
            className="card p-8"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <motion.div
              className="text-8xl font-bold text-gradient mb-4"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.4, type: "spring" }}
            >
              404
            </motion.div>
            
            <motion.h2 
              className="text-2xl font-semibold text-primary mb-3"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.5 }}
            >
              Page Not Found
            </motion.h2>
            
            <motion.p 
              className="text-secondary mb-6"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.6 }}
            >
              The page you're looking for doesn't exist or has been moved.
            </motion.p>
            
            <motion.div
              className="flex gap-3 justify-center"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.7 }}
            >
              <a href="/dashboard" className="btn btn-primary">
                <BarChart3 size={16} />
                Dashboard
              </a>
              <a href="/scans" className="btn btn-outline">
                <List size={16} />
                View Scans
              </a>
            </motion.div>
          </motion.div>
        </motion.div>
      </div>
    </Layout>
  );
};

/**
 * Main App component with modern theme system and routing.
 * 
 * Args:
 *   className: Additional CSS classes
 * 
 * Returns:
 *   JSX.Element: Rendered application with theme provider
 */
const App: React.FC<AppProps> = ({ className = '' }) => {
  console.log('App component rendering with modern theme system...');
  
  return (
    <ThemeProvider>
      <ToastProvider>
        <div className={`app ${className}`}>
          <Router>
          <Routes>
            {/* Home route - redirects to dashboard */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            {/* Dashboard route */}
            <Route 
              path="/dashboard" 
              element={
                <Layout>
                  <Dashboard />
                </Layout>
              }
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
      </ToastProvider>
    </ThemeProvider>
  );
};

export default App; 