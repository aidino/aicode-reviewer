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
      <div className={`create-scan ${className}`} style={{ padding: '20px' }}>
        <div style={{
          maxWidth: '600px',
          margin: '0 auto',
          backgroundColor: 'white',
          padding: '32px',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          textAlign: 'center',
        }}>
          {/* Success Icon */}
          <div style={{
            width: '80px',
            height: '80px',
            backgroundColor: '#4caf50',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 24px',
            color: 'white',
            fontSize: '40px',
          }}>
            ✓
          </div>

          <h2 style={{
            color: '#333',
            marginBottom: '16px',
          }}>
            Scan Initiated Successfully!
          </h2>

          <p style={{
            color: '#666',
            marginBottom: '24px',
            lineHeight: '1.5',
          }}>
            Your {initiatedScan.scan_type === 'pr' ? 'Pull Request' : 'Project'} scan has been started.
            <br />
            <strong>Scan ID:</strong> {initiatedScan.scan_id}
            <br />
            <strong>Job ID:</strong> {initiatedScan.job_id}
          </p>

          {/* Scan Details */}
          <div style={{
            backgroundColor: '#f5f5f5',
            padding: '16px',
            borderRadius: '4px',
            marginBottom: '24px',
            textAlign: 'left',
          }}>
            <h4 style={{ marginBottom: '12px', color: '#333' }}>Scan Details:</h4>
            <div style={{ fontSize: '14px', color: '#666', lineHeight: '1.4' }}>
              <div><strong>Repository:</strong> {initiatedScan.repository}</div>
              <div><strong>Type:</strong> {initiatedScan.scan_type === 'pr' ? 'Pull Request Scan' : 'Full Project Scan'}</div>
              <div><strong>Status:</strong> {initiatedScan.status}</div>
              {initiatedScan.estimated_duration && (
                <div><strong>Estimated Duration:</strong> {Math.ceil(initiatedScan.estimated_duration / 60)} minutes</div>
              )}
            </div>
          </div>

          {/* Status Message */}
          <div style={{
            backgroundColor: '#e3f2fd',
            border: '1px solid #2196f3',
            borderRadius: '4px',
            padding: '12px',
            marginBottom: '24px',
            color: '#1565c0',
            fontSize: '14px',
          }}>
            <strong>Note:</strong> The scan is running in the background. 
            You can check the progress in the scan list or view the report once it's completed.
          </div>

          {/* Action Buttons */}
          <div style={{
            display: 'flex',
            gap: '12px',
            justifyContent: 'center',
          }}>
            <button
              onClick={handleViewScans}
              style={{
                padding: '10px 20px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                backgroundColor: 'white',
                color: '#666',
                cursor: 'pointer',
                fontSize: '14px',
              }}
            >
              View All Scans
            </button>
            <button
              onClick={handleViewScan}
              style={{
                padding: '10px 20px',
                border: 'none',
                borderRadius: '4px',
                backgroundColor: '#1976d2',
                color: 'white',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
              }}
            >
              View Scan Progress
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show form for creating new scan
  return (
    <div className={`create-scan ${className}`} style={{ padding: '20px' }}>
      {/* Header */}
      <div style={{
        marginBottom: '24px',
        textAlign: 'center',
      }}>
        <h1 style={{ marginBottom: '8px' }}>Create New Scan</h1>
        <p style={{ 
          color: '#666',
          margin: 0,
          fontSize: '16px',
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