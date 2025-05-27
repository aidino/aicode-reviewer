/**
 * ReportView page component for displaying detailed scan reports.
 * 
 * This component fetches and displays comprehensive scan report data including
 * scan information, static analysis findings, LLM insights, and architectural diagrams.
 */

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useReport } from '../hooks/useApi';
import { StaticAnalysisFinding, LLMReview, SeverityLevel } from '../types';
import DiagramDisplay from '../components/DiagramDisplay';
import FeedbackButton from '../components/FeedbackButton';

interface ReportViewProps {
  className?: string;
}

/**
 * Component to display detailed scan report with findings and insights.
 * 
 * Args:
 *   className: Additional CSS classes
 * 
 * Returns:
 *   JSX.Element: Rendered report view page
 */
const ReportView: React.FC<ReportViewProps> = ({ className = '' }) => {
  const { scanId } = useParams<{ scanId: string }>();
  const navigate = useNavigate();
  const { data: report, loading, error, refetch } = useReport(scanId);
  
  // Component state
  const [activeTab, setActiveTab] = useState<'overview' | 'findings' | 'insights' | 'diagrams'>('overview');
  const [findingsFilter, setFindingsFilter] = useState<SeverityLevel | 'all'>('all');

  // Severity level styling using CSS classes
  const getSeverityClass = (severity: SeverityLevel): string => {
    switch (severity) {
      case 'Error':
        return 'badge badge-error';
      case 'Warning':
        return 'badge badge-warning';
      case 'Info':
        return 'badge badge-success';
      default:
        return 'badge';
    }
  };

  // Filter findings by severity
  const filteredFindings = report?.static_analysis_findings.filter(finding =>
    findingsFilter === 'all' || finding.severity === findingsFilter
  ) || [];

  // Format date
  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch {
      return dateString;
    }
  };

  // Render code snippet with syntax highlighting
  const renderCodeSnippet = (snippet: string | undefined, filePath: string) => {
    if (!snippet) return null;

    return (
      <div className="card" style={{
        backgroundColor: 'var(--color-surface)',
        marginTop: 'var(--spacing-sm)',
        fontFamily: 'monospace',
        fontSize: 'var(--font-size-sm)',
        overflow: 'auto',
      }}>
        <div className="text-muted font-medium" style={{
          fontSize: 'var(--font-size-xs)',
          marginBottom: 'var(--spacing-sm)',
        }}>
          {filePath}
        </div>
        <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
          {snippet}
        </pre>
      </div>
    );
  };

  // Loading state
  if (loading) {
    return (
      <div className={`report-container ${className}`}>
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div className="loading-text">Loading report...</div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={`report-container ${className}`}>
        <div className="error-container">
          <div className="error-title">Error loading report:</div>
          <div className="error-message">{error.detail}</div>
          <div className="flex gap-md" style={{ marginTop: 'var(--spacing-md)' }}>
            <button onClick={refetch} className="btn btn-primary">
              🔄 Retry
            </button>
            <button onClick={() => navigate('/scans')} className="btn btn-outline">
              ← Back to Scans
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className={`report-container ${className}`}>
        <div className="card text-center">
          <div className="text-muted">No report data available</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`report-container ${className}`}>
      {/* Header */}
      <div className="report-header">
        <div>
          <h1 className="report-title">Scan Report: {report.scan_info.scan_id}</h1>
          <div className="report-meta">
            <span>📁 {report.scan_info.repository}</span>
            <span>📅 {formatDate(report.scan_info.timestamp)}</span>
          </div>
        </div>
        <button
          onClick={() => navigate('/scans')}
          className="btn btn-outline"
        >
          ← Back to Scans
        </button>
      </div>

      {/* Tabs */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{
          display: 'flex',
          borderBottom: '1px solid #e9ecef',
        }}>
          {[
            { key: 'overview', label: 'Overview' },
            { key: 'findings', label: `Findings (${report.static_analysis_findings.length})` },
            { key: 'insights', label: `LLM Insights (${report.llm_review.has_content ? 1 : 0})` },
            { key: 'diagrams', label: `Diagrams (${report.diagrams.length})` },
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              style={{
                padding: '12px 16px',
                border: 'none',
                backgroundColor: 'transparent',
                borderBottom: activeTab === tab.key ? '2px solid #1976d2' : '2px solid transparent',
                color: activeTab === tab.key ? '#1976d2' : '#666',
                fontWeight: activeTab === tab.key ? 'bold' : 'normal',
                cursor: 'pointer',
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div>
          {/* Scan Summary */}
          <div style={{
            backgroundColor: '#f8f9fa',
            padding: '20px',
            borderRadius: '8px',
            marginBottom: '24px',
          }}>
            <h3 style={{ marginTop: 0, marginBottom: '16px' }}>Scan Summary</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div>
                <div style={{ fontWeight: 'bold', color: '#666', fontSize: '0.9em' }}>Total Findings</div>
                <div style={{ fontSize: '1.5em', fontWeight: 'bold' }}>{report.summary.total_findings}</div>
              </div>
              <div>
                <div style={{ fontWeight: 'bold', color: '#666', fontSize: '0.9em' }}>Error</div>
                <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#c62828' }}>{report.summary.severity_breakdown.Error || 0}</div>
              </div>
              <div>
                <div style={{ fontWeight: 'bold', color: '#666', fontSize: '0.9em' }}>Warning</div>
                <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#ef6c00' }}>{report.summary.severity_breakdown.Warning || 0}</div>
              </div>
              <div>
                <div style={{ fontWeight: 'bold', color: '#666', fontSize: '0.9em' }}>Info</div>
                <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#f57f17' }}>{report.summary.severity_breakdown.Info || 0}</div>
              </div>
              <div>
                <div style={{ fontWeight: 'bold', color: '#666', fontSize: '0.9em' }}>Unknown</div>
                <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#2e7d32' }}>{report.summary.severity_breakdown.Unknown || 0}</div>
              </div>
            </div>
          </div>

          {/* Scan Info */}
          <div style={{
            backgroundColor: 'white',
            border: '1px solid #e9ecef',
            borderRadius: '8px',
            padding: '20px',
            marginBottom: '24px',
          }}>
            <h3 style={{ marginTop: 0, marginBottom: '16px' }}>Scan Information</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
              <div>
                <div style={{ fontWeight: 'bold', color: '#666', fontSize: '0.9em' }}>Scan ID</div>
                <div style={{ fontFamily: 'monospace' }}>{report.scan_info.scan_id}</div>
              </div>
              <div>
                <div style={{ fontWeight: 'bold', color: '#666', fontSize: '0.9em' }}>Type</div>
                <div>{report.scan_info.scan_type}</div>
              </div>
              <div>
                <div style={{ fontWeight: 'bold', color: '#666', fontSize: '0.9em' }}>Repository</div>
                <div style={{ fontFamily: 'monospace' }}>{report.scan_info.repository}</div>
              </div>
              {report.scan_info.pr_id && (
                <div>
                  <div style={{ fontWeight: 'bold', color: '#666', fontSize: '0.9em' }}>Pull Request</div>
                  <div>#{report.scan_info.pr_id}</div>
                </div>
              )}
              <div>
                <div style={{ fontWeight: 'bold', color: '#666', fontSize: '0.9em' }}>Files Analyzed</div>
                <div>{report.metadata.total_files_analyzed}</div>
              </div>
              <div>
                <div style={{ fontWeight: 'bold', color: '#666', fontSize: '0.9em' }}>Successful Parses</div>
                <div>{report.metadata.successful_parses}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Findings Tab */}
      {activeTab === 'findings' && (
        <div>
          {/* Filters */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{ marginRight: '12px', fontWeight: 'bold' }}>Filter by severity:</label>
            <select
              value={findingsFilter}
              onChange={(e) => setFindingsFilter(e.target.value as any)}
              style={{
                padding: '6px 12px',
                border: '1px solid #ccc',
                borderRadius: '4px',
              }}
            >
              <option value="all">All ({report.static_analysis_findings.length})</option>
              <option value="Error">Error ({report.summary.severity_breakdown.Error || 0})</option>
              <option value="Warning">Warning ({report.summary.severity_breakdown.Warning || 0})</option>
              <option value="Info">Info ({report.summary.severity_breakdown.Info || 0})</option>
              <option value="Unknown">Unknown ({report.summary.severity_breakdown.Unknown || 0})</option>
            </select>
          </div>

          {/* Findings List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {filteredFindings.map((finding, index) => (
              <div
                key={index}
                style={{
                  backgroundColor: 'white',
                  border: '1px solid #e9ecef',
                  borderRadius: '8px',
                  padding: '16px',
                }}
              >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: '12px',
                }}>
                  <div>
                    <h4 style={{ margin: 0, marginBottom: '4px' }}>{finding.message}</h4>
                    <div style={{ fontSize: '0.9em', color: '#666' }}>
                      {finding.file}:{finding.line}
                      {finding.column && `:${finding.column}`}
                    </div>
                  </div>
                  <span className={getSeverityClass(finding.severity)}>
                    {finding.severity}
                  </span>
                </div>

                <div style={{ marginBottom: '8px' }}>
                  <span style={{
                    backgroundColor: '#e3f2fd',
                    color: '#1565c0',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    fontSize: '0.8em',
                    fontWeight: 'bold',
                  }}>
                    {finding.category}
                  </span>
                  <span style={{
                    backgroundColor: '#f3e5f5',
                    color: '#7b1fa2',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    fontSize: '0.8em',
                    fontWeight: 'bold',
                    marginLeft: '8px',
                  }}>
                    {finding.rule_id}
                  </span>
                </div>

                {finding.suggestion && (
                  <div style={{
                    backgroundColor: '#e8f5e8',
                    border: '1px solid #4caf50',
                    borderRadius: '4px',
                    padding: '8px',
                    marginBottom: '8px',
                  }}>
                    <div style={{ fontWeight: 'bold', color: '#2e7d32', fontSize: '0.9em' }}>
                      Suggestion:
                    </div>
                    <div>{finding.suggestion}</div>
                  </div>
                )}

                {finding.code_snippet && renderCodeSnippet(finding.code_snippet, finding.file)}

                {/* Feedback Button for Finding */}
                <FeedbackButton
                  scanId={report.scan_info.scan_id}
                  itemId={`finding-${index}`}
                  feedbackType="finding"
                  itemContent={finding.message}
                  ruleId={finding.rule_id}
                  onFeedbackSubmitted={(response) => {
                    console.log('Feedback submitted for finding:', response);
                  }}
                />
              </div>
            ))}

            {filteredFindings.length === 0 && (
              <div style={{
                textAlign: 'center',
                padding: '40px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px',
                color: '#666',
              }}>
                No findings match the selected filter.
              </div>
            )}
          </div>
        </div>
      )}

      {/* LLM Insights Tab */}
      {activeTab === 'insights' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {report.llm_review.has_content ? (
            <div
              style={{
                backgroundColor: 'white',
                border: '1px solid #e9ecef',
                borderRadius: '8px',
                padding: '20px',
              }}
            >
              <h3 style={{ marginTop: 0, marginBottom: '12px', color: '#1976d2' }}>
                AI Code Review Analysis
              </h3>
              <div style={{
                lineHeight: '1.6',
                whiteSpace: 'pre-wrap',
                marginBottom: '16px',
              }}>
                {report.llm_review.insights}
              </div>

              {/* Display sections if available */}
              {Object.keys(report.llm_review.sections).length > 0 && (
                <div>
                  <h4 style={{ marginBottom: '8px', color: '#666' }}>Summary Sections:</h4>
                  {Object.entries(report.llm_review.sections).map(([key, value]) => (
                    <div key={key} style={{ marginBottom: '8px' }}>
                      <strong style={{ textTransform: 'capitalize' }}>{key.replace('_', ' ')}:</strong> {value}
                    </div>
                  ))}
                </div>
              )}

              {/* Feedback Button for LLM Insight */}
              <FeedbackButton
                scanId={report.scan_info.scan_id}
                itemId="llm-review"
                feedbackType="llm_insight"
                itemContent={report.llm_review.insights}
                suggestionType="code_review"
                onFeedbackSubmitted={(response) => {
                  console.log('Feedback submitted for LLM review:', response);
                }}
              />
            </div>
          ) : (
            <div style={{
              textAlign: 'center',
              padding: '40px',
              backgroundColor: '#f8f9fa',
              borderRadius: '8px',
              color: '#666',
            }}>
              No LLM insights available for this scan.
            </div>
          )}
        </div>
      )}

      {/* Diagrams Tab */}
      {activeTab === 'diagrams' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {report.diagrams.map((diagram, index) => (
            <div key={index}>
              <h3 style={{ marginBottom: '16px' }}>
                {diagram.type} - {diagram.format}
              </h3>
              <DiagramDisplay diagram={diagram} />
              
              {/* Feedback Button for Diagram */}
              <FeedbackButton
                scanId={report.scan_info.scan_id}
                itemId={`diagram-${index}`}
                feedbackType="diagram"
                itemContent={`${diagram.type} diagram`}
                suggestionType={diagram.format}
                onFeedbackSubmitted={(response) => {
                  console.log('Feedback submitted for diagram:', response);
                }}
              />
            </div>
          ))}

          {report.diagrams.length === 0 && (
            <div style={{
              textAlign: 'center',
              padding: '40px',
              backgroundColor: '#f8f9fa',
              borderRadius: '8px',
              color: '#666',
            }}>
              No diagrams available for this scan.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ReportView; 