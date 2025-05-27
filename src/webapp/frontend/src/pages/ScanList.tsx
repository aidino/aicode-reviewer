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

  // Status badge styles using CSS classes
  const getStatusBadgeClass = (status: ScanStatus): string => {
    switch (status) {
      case 'completed':
        return 'badge badge-success';
      case 'running':
        return 'badge badge-warning';
      case 'pending':
        return 'badge badge-info';
      case 'failed':
        return 'badge badge-error';
      default:
        return 'badge';
    }
  };

  // Type badge styles using CSS classes
  const getTypeBadgeClass = (type: ScanType): string => {
    switch (type) {
      case 'pr':
        return 'badge badge-info';
      case 'project':
        return 'badge badge-success';
      default:
        return 'badge';
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
      <div className={`scan-list-container ${className}`}>
        <div className="scan-list-header">
          <h1 className="scan-list-title">Code Review Scans</h1>
        </div>
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div className="loading-text">Loading scans...</div>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !scans) {
    return (
      <div className={`scan-list-container ${className}`}>
        <div className="scan-list-header">
          <h1 className="scan-list-title">Code Review Scans</h1>
        </div>
        <div className="error-container">
          <div className="error-title">Error loading scans:</div>
          <div className="error-message">{error.detail}</div>
          <button onClick={refetch} className="btn btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`scan-list-container ${className}`}>
      {/* Header */}
      <div className="scan-list-header">
        <h1 className="scan-list-title">Code Review Scans</h1>
        <div className="scan-list-actions">
          <button
            onClick={() => navigate('/create-scan')}
            className="btn btn-primary"
          >
            ➕ New Scan
          </button>
        </div>
      </div>

      {/* Statistics */}
      {scans && scans.length > 0 && (
        <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
          <div className="text-secondary" style={{ fontSize: 'var(--font-size-sm)' }}>
            Showing {scans.length} scan{scans.length !== 1 ? 's' : ''} (Page {page + 1})
          </div>
        </div>
      )}

      {/* Scans Table */}
      {scans && scans.length > 0 ? (
        <div style={{ overflow: 'auto' }}>
          <table className="scan-table">
            <thead>
              <tr>
                <th>Scan ID</th>
                <th>Type</th>
                <th>Repository</th>
                <th>Status</th>
                <th>Findings</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {scans.map((scan) => (
                <tr key={scan.scan_id} data-testid="scan-list-item">
                  <td>
                    <button
                      onClick={() => handleViewReport(scan.scan_id)}
                      className="btn btn-ghost"
                      style={{ padding: 0, textDecoration: 'underline' }}
                    >
                      {scan.scan_id}
                    </button>
                  </td>
                  <td>
                    <span className={getTypeBadgeClass(scan.scan_type)}>
                      {scan.scan_type}
                    </span>
                    {scan.pr_id && (
                      <div className="text-muted" style={{ 
                        fontSize: 'var(--font-size-xs)', 
                        marginTop: 'var(--spacing-xs)' 
                      }}>
                        PR #{scan.pr_id}
                      </div>
                    )}
                  </td>
                  <td>
                    <div style={{ 
                      fontFamily: 'monospace', 
                      fontSize: 'var(--font-size-sm)' 
                    }}>
                      {scan.repository}
                    </div>
                  </td>
                  <td>
                    <span className={getStatusBadgeClass(scan.status)}>
                      {scan.status}
                    </span>
                  </td>
                  <td>
                    {scan.total_findings > 0 ? (
                      <span className="font-semibold" style={{
                        color: scan.total_findings > 10 ? 'var(--color-error)' : 
                               scan.total_findings > 5 ? 'var(--color-warning)' : 'var(--color-success)'
                      }}>
                        {scan.total_findings}
                      </span>
                    ) : (
                      <span className="text-muted">0</span>
                    )}
                  </td>
                  <td className="text-secondary" style={{ fontSize: 'var(--font-size-sm)' }}>
                    {formatDate(scan.created_at)}
                  </td>
                  <td>
                    <div className="flex gap-sm">
                      <button
                        onClick={() => handleViewReport(scan.scan_id)}
                        className="btn btn-primary"
                        style={{ fontSize: 'var(--font-size-xs)' }}
                      >
                        View
                      </button>
                      <button
                        onClick={() => handleDeleteScan(scan.scan_id)}
                        disabled={deleting}
                        className="btn btn-outline"
                        style={{ 
                          fontSize: 'var(--font-size-xs)',
                          borderColor: 'var(--color-error)',
                          color: 'var(--color-error)'
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
        <div className="card text-center" style={{ padding: 'var(--spacing-2xl)' }}>
          <h3 className="text-primary">No scans found</h3>
          <p className="text-secondary">Create your first scan to get started with code analysis.</p>
          <button
            onClick={() => navigate('/create-scan')}
            className="btn btn-primary"
            style={{ marginTop: 'var(--spacing-md)' }}
          >
            ➕ Create Scan
          </button>
        </div>
      )}

      {/* Pagination */}
      {scans && scans.length > 0 && (
        <div className="pagination">
          <button
            onClick={handlePreviousPage}
            disabled={page === 0 || loading}
            className={`pagination-button ${page === 0 ? '' : 'active'}`}
          >
            ← Previous
          </button>
          
          <span className="pagination-info">
            Page {page + 1}
          </span>
          
          <button
            onClick={handleNextPage}
            disabled={!scans || scans.length < pageSize || loading}
            className={`pagination-button ${(!scans || scans.length < pageSize) ? '' : 'active'}`}
          >
            Next →
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
          <div className="card" style={{ padding: 'var(--spacing-lg)' }}>
            <div className="loading-spinner"></div>
            <div className="loading-text">Loading...</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScanList; 