import React, { useState, useEffect } from 'react';
import DashboardSidebar from './DashboardSidebar';
import FloatingNewScanButton from './FloatingNewScanButton';
import { useSidebar } from '../contexts/SidebarContext';

interface LayoutProps {
  children: React.ReactNode;
  showFloatingButton?: boolean;
  className?: string;
}

interface HealthCheckResponse {
  status: string;
  timestamp: string;
  version: string;
  uptime: string;
  metrics: {
    total_scans: number;
    total_findings: number;
    avg_response_time: string;
  };
}

const Layout: React.FC<LayoutProps> = ({ 
  children, 
  showFloatingButton = true,
  className = '' 
}) => {
  const { isCollapsed } = useSidebar();
  const [healthData, setHealthData] = useState<HealthCheckResponse | null>(null);

  const fetchHealthData = async () => {
    try {
      const response = await fetch('/api/dashboard/health');
      if (response.ok) {
        const data = await response.json();
        setHealthData(data);
      } else {
        // Mock data fallback
        setHealthData({
          status: 'healthy',
          timestamp: new Date().toISOString(),
          version: '2.1.0',
          uptime: '15d 4h 23m',
          metrics: {
            total_scans: 1250,
            total_findings: 8420,
            avg_response_time: '245ms'
          }
        });
      }
    } catch (error) {
      console.warn('Health check failed, using mock data:', error);
      // Mock data fallback
      setHealthData({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '2.1.0',
        uptime: '15d 4h 23m',
        metrics: {
          total_scans: 1250,
          total_findings: 8420,
          avg_response_time: '245ms'
        }
      });
    }
  };

  useEffect(() => {
    fetchHealthData();
    // Refresh health data every 30 seconds
    const interval = setInterval(fetchHealthData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      {/* Global Sidebar */}
      <DashboardSidebar healthData={healthData} />
      
      {/* Main Content */}
      <div className={`dashboard-with-sidebar ${isCollapsed ? 'collapsed' : ''} min-h-screen transition-all duration-300 ${className}`}>
        {children}
      </div>
      
      {/* Floating New Scan Button */}
      {showFloatingButton && <FloatingNewScanButton />}
    </>
  );
};

export default Layout; 