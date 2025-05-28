/**
 * Main App component with routing for AI Code Reviewer frontend.
 * 
 * This component sets up the main application structure with React Router
 * for navigation between different pages and views using the new Layout system.
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BarChart3, List } from 'lucide-react';
import ScanList from './pages/ScanList';
import ReportView from './pages/ReportView';
import CreateScan from './pages/CreateScan';
import TestPage from './pages/TestPage';
import Dashboard from './pages/Dashboard';
import AgentWorkflowPage from './pages/AgentWorkflowPage';
import AgentWorkflowDemo from './pages/AgentWorkflowDemo';
import { LoginPageBackup } from './pages/LoginPageBackup';
// import { LoginPage } from './pages/LoginPage';
import { LoginPageSimple } from './pages/LoginPageSimple';
import { RegisterPageSimple } from './pages/RegisterPageSimple';
import SoftUIDashboard from './components/SoftUIDashboard';
import RepositoryManagement from './pages/RepositoryManagement';
import Layout from './components/Layout';
import { ThemeProvider } from './components/ThemeProvider';
import { ToastProvider } from './components/Toast';
import { SidebarProvider } from './contexts/SidebarContext';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute, UserProfile, AuthModal } from './components/auth';
import './styles/theme.css';
import './styles/components.css';
import './styles/globals.css';

interface AppProps {
  className?: string;
}

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
            className="card-soft p-8"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <motion.div
              className="text-8xl font-bold soft-gradient-text mb-4"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.4, type: "spring" }}
            >
              404
            </motion.div>
            
            <motion.h2 
              className="text-2xl font-semibold text-gray-900 mb-3"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.5 }}
            >
              Page Not Found
            </motion.h2>
            
            <motion.p 
              className="text-gray-600 mb-6"
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
              <a href="/dashboard" className="btn-soft btn-soft-primary">
                <BarChart3 size={16} />
                Dashboard
              </a>
              <a href="/scans" className="btn-soft btn-soft-outline">
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
  console.log('App component rendering with Layout system...');
  
  return (
    <ThemeProvider>
      <ToastProvider>
        <AuthProvider>
          <SidebarProvider>
            <div className={`app ${className}`}>
              <Router>
                <Routes>
                  {/* Home route - redirects to dashboard */}
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  
                  {/* Dashboard route - Protected */}
                  <Route 
                    path="/dashboard" 
                    element={
                      <ProtectedRoute>
                        <Dashboard />
                      </ProtectedRoute>
                    } 
                  />
                  
                  {/* User Profile route - Protected */}
                  <Route 
                    path="/profile" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <UserProfile />
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                  
                  {/* Repository Management routes - Protected */}
                  <Route 
                    path="/repositories/new" 
                    element={
                      <ProtectedRoute>
                        <RepositoryManagement />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/repositories/:id" 
                    element={
                      <ProtectedRoute>
                        <RepositoryManagement />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/repositories/:id/edit" 
                    element={
                      <ProtectedRoute>
                        <RepositoryManagement />
                      </ProtectedRoute>
                    } 
                  />
                  
                  {/* Soft UI Dashboard demo route (without sidebar) */}
                  <Route 
                    path="/soft-ui" 
                    element={
                      <Layout showFloatingButton={false}>
                        <SoftUIDashboard />
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
                  
                  {/* Scans list route - Protected */}
                  <Route 
                    path="/scans" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <ScanList />
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                  
                  {/* Create scan route - Protected */}
                  <Route 
                    path="/create-scan" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <CreateScan />
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                  
                  {/* Report view route - Protected */}
                  <Route 
                    path="/reports/:scanId" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <ReportView />
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                  
                  {/* Agent Workflow Visualization routes - Protected */}
                  <Route 
                    path="/workflow/:scanId" 
                    element={
                      <ProtectedRoute>
                        <AgentWorkflowPage />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/workflow" 
                    element={
                      <ProtectedRoute>
                        <AgentWorkflowPage />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/workflow-demo" 
                    element={
                      <ProtectedRoute>
                        <AgentWorkflowDemo />
                      </ProtectedRoute>
                    } 
                  />
                  
                  {/* Legacy route support */}
                  <Route path="/report/:scanId" element={<Navigate to="/reports/:scanId" replace />} />
                  
                  {/* Test route for debugging */}
                  <Route 
                    path="/debug" 
                    element={<div style={{padding: '50px', fontSize: '24px', textAlign: 'center'}}>🧪 Debug Route Working!</div>} 
                  />
                  
                  {/* Login route - Public */}
                  <Route 
                    path="/login" 
                    element={<LoginPageSimple />} 
                  />
                  
                  {/* Register route - Public */}
                  <Route 
                    path="/register" 
                    element={<RegisterPageSimple />} 
                  />
                  
                  {/* Not found route */}
                  <Route path="*" element={<NotFoundPage />} />
                </Routes>
              </Router>
              
              {/* Authentication Modal */}
              <AuthModal />
            </div>
          </SidebarProvider>
        </AuthProvider>
      </ToastProvider>
    </ThemeProvider>
  );
};

export default App; 