/**
 * ScanList page component for displaying a list of scans.
 * 
 * This component fetches and displays scans in a table format with
 * navigation to individual report views and basic scan management.
 */

import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useScans, useDeleteScan } from '../hooks/useApi';
import { ScanListItem, ScanType, ScanStatus } from '../types';

interface ScanListProps {
  className?: string;
}

/**
 * Component to display list of scans with navigation and basic actions.
 * 
 * Args:
 *   className: Additional CSS classes
 * 
 * Returns:
 *   JSX.Element: Rendered scan list page
 */
const ScanList: React.FC<ScanListProps> = ({ className = '' }) => {
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const pageSize = 20;
  
  // API hooks
  const { data: scans, loading, error, refetch } = useScans(pageSize, page * pageSize);
  const { deleteScan, loading: deleting } = useDeleteScan();

  // Status badge styles
  const getStatusBadgeStyle = (status: ScanStatus): React.CSSProperties => {
    const baseStyle: React.CSSProperties = {
      padding: '4px 8px',
      borderRadius: '12px',
      fontSize: '0.8em',
      fontWeight: 'bold',
      textTransform: 'uppercase',
    };

    switch (status) {
      case 'completed':
        return { ...baseStyle, backgroundColor: '#e8f5e8', color: '#2e7d32' };
      case 'running':
        return { ...baseStyle, backgroundColor: '#fff3cd', color: '#856404' };
      case 'pending':
        return { ...baseStyle, backgroundColor: '#cce7ff', color: '#0066cc' };
      case 'failed':
        return { ...baseStyle, backgroundColor: '#ffebee', color: '#c62828' };
      default:
        return { ...baseStyle, backgroundColor: '#f5f5f5', color: '#666' };
    }
  };

  // Type badge styles
  const getTypeBadgeStyle = (type: ScanType): React.CSSProperties => {
    const baseStyle: React.CSSProperties = {
      padding: '2px 6px',
      borderRadius: '8px',
      fontSize: '0.75em',
      fontWeight: 'bold',
      textTransform: 'uppercase',
    };

    switch (type) {
      case 'pr':
        return { ...baseStyle, backgroundColor: '#e3f2fd', color: '#1565c0' };
      case 'project':
        return { ...baseStyle, backgroundColor: '#f3e5f5', color: '#7b1fa2' };
      default:
        return { ...baseStyle, backgroundColor: '#f5f5f5', color: '#666' };
    }
  };

  // Handle scan navigation
  const handleViewReport = useCallback((scanId: string) => {
    navigate(`/reports/${scanId}`);
  }, [navigate]);

  // Handle scan deletion
  const handleDeleteScan = useCallback(async (scanId: string) => {
    if (window.confirm('Are you sure you want to delete this scan?')) {
      const success = await deleteScan(scanId);
      if (success) {
        // Refresh the list
        refetch();
      }
    }
  }, [deleteScan, refetch]);

  // Format date
  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch {
      return dateString;
    }
  };

  // Pagination handlers
  const handlePreviousPage = () => {
    setPage(prev => Math.max(0, prev - 1));
  };

  const handleNextPage = () => {
    setPage(prev => prev + 1);
  };

  // Loading state
  if (loading && !scans) {
    return (
      <div className={`scan-list ${className}`} style={{ padding: '20px' }}>
        <h1>Code Review Scans</h1>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <div>Loading scans...</div>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !scans) {
    return (
      <div className={`scan-list ${className}`} style={{ padding: '20px' }}>
        <h1>Code Review Scans</h1>
        <div style={{
          padding: '20px',
          backgroundColor: '#ffebee',
          border: '1px solid #f44336',
          borderRadius: '4px',
          color: '#c62828',
        }}>
          <strong>Error loading scans:</strong> {error.detail}
          <button
            onClick={refetch}
            style={{
              marginLeft: '12px',
              padding: '6px 12px',
              backgroundColor: '#f44336',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`scan-list ${className}`} style={{ padding: '20px' }}>
      {/* Header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '24px' 
      }}>
        <h1>Code Review Scans</h1>
        <button
          onClick={() => navigate('/create-scan')}
          style={{
            padding: '8px 16px',
            backgroundColor: '#1976d2',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          New Scan
        </button>
      </div>

      {/* Statistics */}
      {scans && scans.length > 0 && (
        <div style={{ marginBottom: '24px' }}>
          <div style={{
            backgroundColor: '#f5f5f5',
            padding: '12px 16px',
            borderRadius: '4px',
            fontSize: '14px',
            color: '#666',
          }}>
            Showing {scans.length} scan{scans.length !== 1 ? 's' : ''} (Page {page + 1})
          </div>
        </div>
      )}

      {/* Scans Table */}
      {scans && scans.length > 0 ? (
        <div style={{ overflow: 'auto' }}>
          <table style={{ 
            width: '100%', 
            borderCollapse: 'collapse',
            backgroundColor: 'white',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          }}>
            <thead>
              <tr style={{ backgroundColor: '#f8f9fa' }}>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>
                  Scan ID
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>
                  Type
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>
                  Repository
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>
                  Status
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>
                  Findings
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>
                  Created
                </th>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {scans.map((scan) => (
                <tr key={scan.scan_id} data-testid="scan-list-item" style={{ borderBottom: '1px solid #dee2e6' }}>
                  <td style={{ padding: '12px' }}>
                    <button
                      onClick={() => handleViewReport(scan.scan_id)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#1976d2',
                        textDecoration: 'underline',
                        cursor: 'pointer',
                        padding: 0,
                        fontSize: 'inherit',
                      }}
                    >
                      {scan.scan_id}
                    </button>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span style={getTypeBadgeStyle(scan.scan_type)}>
                      {scan.scan_type}
                    </span>
                    {scan.pr_id && (
                      <div style={{ fontSize: '0.8em', color: '#666', marginTop: '2px' }}>
                        PR #{scan.pr_id}
                      </div>
                    )}
                  </td>
                  <td style={{ padding: '12px' }}>
                    <div style={{ fontFamily: 'monospace', fontSize: '0.9em' }}>
                      {scan.repository}
                    </div>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span style={getStatusBadgeStyle(scan.status)}>
                      {scan.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>
                    {scan.total_findings > 0 ? (
                      <span style={{
                        fontWeight: 'bold',
                        color: scan.total_findings > 10 ? '#f44336' : 
                               scan.total_findings > 5 ? '#ff9800' : '#4caf50'
                      }}>
                        {scan.total_findings}
                      </span>
                    ) : (
                      <span style={{ color: '#666' }}>0</span>
                    )}
                  </td>
                  <td style={{ padding: '12px', fontSize: '0.9em', color: '#666' }}>
                    {formatDate(scan.created_at)}
                  </td>
                  <td style={{ padding: '12px' }}>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={() => handleViewReport(scan.scan_id)}
                        style={{
                          padding: '4px 8px',
                          backgroundColor: '#1976d2',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '0.8em',
                        }}
                      >
                        View
                      </button>
                      <button
                        onClick={() => handleDeleteScan(scan.scan_id)}
                        disabled={deleting}
                        style={{
                          padding: '4px 8px',
                          backgroundColor: '#f44336',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: deleting ? 'not-allowed' : 'pointer',
                          fontSize: '0.8em',
                          opacity: deleting ? 0.6 : 1,
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{
          textAlign: 'center',
          padding: '40px',
          backgroundColor: '#f8f9fa',
          borderRadius: '4px',
        }}>
          <h3>No scans found</h3>
          <p>Create your first scan to get started with code analysis.</p>
          <button
            onClick={() => navigate('/create-scan')}
            style={{
              padding: '8px 16px',
              backgroundColor: '#1976d2',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              marginTop: '12px',
            }}
          >
            Create Scan
          </button>
        </div>
      )}

      {/* Pagination */}
      {scans && scans.length > 0 && (
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginTop: '24px',
          padding: '12px',
          backgroundColor: '#f8f9fa',
          borderRadius: '4px',
        }}>
          <button
            onClick={handlePreviousPage}
            disabled={page === 0 || loading}
            style={{
              padding: '8px 16px',
              backgroundColor: page === 0 ? '#e0e0e0' : '#1976d2',
              color: page === 0 ? '#666' : 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: page === 0 ? 'not-allowed' : 'pointer',
            }}
          >
            Previous
          </button>
          
          <span style={{ fontSize: '14px', color: '#666' }}>
            Page {page + 1}
          </span>
          
          <button
            onClick={handleNextPage}
            disabled={!scans || scans.length < pageSize || loading}
            style={{
              padding: '8px 16px',
              backgroundColor: (!scans || scans.length < pageSize) ? '#e0e0e0' : '#1976d2',
              color: (!scans || scans.length < pageSize) ? '#666' : 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: (!scans || scans.length < pageSize) ? 'not-allowed' : 'pointer',
            }}
          >
            Next
          </button>
        </div>
      )}

      {/* Loading overlay */}
      {loading && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '4px',
            boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
          }}>
            Loading...
          </div>
        </div>
      )}
    </div>
  );
};

export default ScanList; 