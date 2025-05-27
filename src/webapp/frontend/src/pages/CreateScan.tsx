/**
 * CreateScan page component for initiating new code scans.
 * 
 * This page provides an interface for users to create new code scans
 * with form validation and progress tracking.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ScanForm from '../components/ScanForm';
import { ScanInitiateResponse } from '../types';

interface CreateScanProps {
  className?: string;
}

/**
 * Page component for creating new scans.
 * 
 * Args:
 *   className: Additional CSS classes
 * 
 * Returns:
 *   JSX.Element: Rendered create scan page
 */
const CreateScan: React.FC<CreateScanProps> = ({ className = '' }) => {
  const navigate = useNavigate();
  const [initiatedScan, setInitiatedScan] = useState<ScanInitiateResponse | null>(null);

  // Handle successful scan initiation
  const handleScanInitiated = (response: ScanInitiateResponse) => {
    setInitiatedScan(response);
  };

  // Handle cancel action
  const handleCancel = () => {
    navigate('/scans');
  };

  // Handle navigation after scan initiated
  const handleViewScan = () => {
    if (initiatedScan) {
      navigate(`/reports/${initiatedScan.scan_id}`);
    }
  };

  const handleViewScans = () => {
    navigate('/scans');
  };

  // Show success message after scan is initiated
  if (initiatedScan) {
    return (
      <div className={`create-scan-container ${className}`}>
        <div className="success-container text-center" style={{
          maxWidth: '600px',
          margin: '0 auto',
          padding: 'var(--spacing-2xl)',
        }}>
          {/* Success Icon */}
          <div style={{
            width: '80px',
            height: '80px',
            backgroundColor: 'var(--color-success)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto var(--spacing-xl)',
            color: 'var(--color-text-inverse)',
            fontSize: 'var(--font-size-4xl)',
          }}>
            ✓
          </div>

          <h2 className="text-primary" style={{ marginBottom: 'var(--spacing-md)' }}>
            Scan Initiated Successfully!
          </h2>

          <p className="text-secondary" style={{
            marginBottom: 'var(--spacing-xl)',
            lineHeight: '1.5',
          }}>
            Your {initiatedScan.scan_type === 'pr' ? 'Pull Request' : 'Project'} scan has been started.
            <br />
            <strong>Scan ID:</strong> {initiatedScan.scan_id}
            <br />
            <strong>Job ID:</strong> {initiatedScan.job_id}
          </p>

          {/* Scan Details */}
          <div className="card" style={{
            marginBottom: 'var(--spacing-xl)',
            textAlign: 'left',
          }}>
            <h4 className="text-primary" style={{ marginBottom: 'var(--spacing-md)' }}>Scan Details:</h4>
            <div className="text-secondary" style={{ 
              fontSize: 'var(--font-size-sm)', 
              lineHeight: '1.4' 
            }}>
              <div><strong>Repository:</strong> {initiatedScan.repository}</div>
              <div><strong>Type:</strong> {initiatedScan.scan_type === 'pr' ? 'Pull Request Scan' : 'Full Project Scan'}</div>
              <div><strong>Status:</strong> {initiatedScan.status}</div>
              {initiatedScan.estimated_duration && (
                <div><strong>Estimated Duration:</strong> {Math.ceil(initiatedScan.estimated_duration / 60)} minutes</div>
              )}
            </div>
          </div>

          {/* Status Message */}
          <div className="badge badge-info" style={{
            display: 'block',
            padding: 'var(--spacing-md)',
            marginBottom: 'var(--spacing-xl)',
            fontSize: 'var(--font-size-sm)',
          }}>
            <strong>Note:</strong> The scan is running in the background. 
            You can check the progress in the scan list or view the report once it's completed.
          </div>

          {/* Action Buttons */}
          <div className="flex gap-md justify-center">
            <button onClick={handleViewScans} className="btn btn-outline">
              📋 View All Scans
            </button>
            <button onClick={handleViewScan} className="btn btn-primary">
              👁️ View Scan Progress
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show form for creating new scan
  return (
    <div className={`create-scan-container ${className}`}>
      {/* Header */}
      <div className="text-center" style={{ marginBottom: 'var(--spacing-xl)' }}>
        <h1 className="text-primary" style={{ marginBottom: 'var(--spacing-sm)' }}>
          ➕ Create New Scan
        </h1>
        <p className="text-secondary" style={{ 
          margin: 0,
          fontSize: 'var(--font-size-lg)',
        }}>
          Initiate a new code analysis scan for your repository
        </p>
      </div>

      {/* Scan Form */}
      <ScanForm
        onScanInitiated={handleScanInitiated}
        onCancel={handleCancel}
      />

      {/* Help Section */}
      <div style={{
        maxWidth: '600px',
        margin: '32px auto 0',
        backgroundColor: '#f8f9fa',
        padding: '20px',
        borderRadius: '8px',
        border: '1px solid #e9ecef',
      }}>
        <h3 style={{ marginBottom: '16px', color: '#333' }}>What happens next?</h3>
        <div style={{ fontSize: '14px', color: '#666', lineHeight: '1.5' }}>
          <div style={{ marginBottom: '12px' }}>
            <strong>1. Scan Initiation:</strong> Your scan request will be queued and processed asynchronously.
          </div>
          <div style={{ marginBottom: '12px' }}>
            <strong>2. Code Analysis:</strong> Our multi-agent system will analyze your code using static analysis and AI insights.
          </div>
          <div style={{ marginBottom: '12px' }}>
            <strong>3. Report Generation:</strong> A comprehensive report with findings, suggestions, and diagrams will be generated.
          </div>
          <div>
            <strong>4. Notification:</strong> You can monitor progress and view results in the scan list.
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateScan; 