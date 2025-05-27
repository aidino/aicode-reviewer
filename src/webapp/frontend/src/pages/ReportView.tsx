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

  // Severity level styling
  const getSeverityStyle = (severity: SeverityLevel): React.CSSProperties => {
    const baseStyle: React.CSSProperties = {
      padding: '2px 8px',
      borderRadius: '12px',
      fontSize: '0.8em',
      fontWeight: 'bold',
      textTransform: 'uppercase',
    };

    switch (severity) {
      case 'critical':
        return { ...baseStyle, backgroundColor: '#ffebee', color: '#c62828' };
      case 'high':
        return { ...baseStyle, backgroundColor: '#fff3e0', color: '#ef6c00' };
      case 'medium':
        return { ...baseStyle, backgroundColor: '#fff8e1', color: '#f57f17' };
      case 'low':
        return { ...baseStyle, backgroundColor: '#e8f5e8', color: '#2e7d32' };
      default:
        return { ...baseStyle, backgroundColor: '#f5f5f5', color: '#666' };
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
      <div style={{
        backgroundColor: '#f8f9fa',
        border: '1px solid #e9ecef',
        borderRadius: '4px',
        padding: '12px',
        marginTop: '8px',
        fontFamily: 'monospace',
        fontSize: '0.9em',
        overflow: 'auto',
      }}>
        <div style={{
          fontSize: '0.8em',
          color: '#666',
          marginBottom: '8px',
          fontWeight: 'bold',
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
      <div className={`report-view ${className}`} style={{ padding: '20px' }}>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <div>Loading report...</div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={`report-view ${className}`} style={{ padding: '20px' }}>
        <div style={{
          padding: '20px',
          backgroundColor: '#ffebee',
          border: '1px solid #f44336',
          borderRadius: '4px',
          color: '#c62828',
        }}>
          <strong>Error loading report:</strong> {error.detail}
          <div style={{ marginTop: '12px' }}>
            <button
              onClick={refetch}
              style={{
                marginRight: '12px',
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
            <button
              onClick={() => navigate('/scans')}
              style={{
                padding: '6px 12px',
                backgroundColor: '#666',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Back to Scans
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className={`report-view ${className}`} style={{ padding: '20px' }}>
        <div>No report data available</div>
      </div>
    );
  }

  return (
    <div className={`report-view ${className}`} style={{ padding: '20px' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
        paddingBottom: '16px',
        borderBottom: '2px solid #e9ecef',
      }}>
        <div>
          <h1>Scan Report: {report.scan_info.scan_id}</h1>
          <div style={{ color: '#666', fontSize: '14px' }}>
            {report.scan_info.repository} • {formatDate(report.scan_info.created_at)}
          </div>
        </div>
        <button
          onClick={() => navigate('/scans')}
          style={{
            padding: '8px 16px',
            backgroundColor: '#666',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Back to Scans
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
            { key: 'insights', label: `LLM Insights (${report.llm_analysis.length})` },
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
                <div style={{ fontWeight: 'bold', color: '#666', fontSize: '0.9em' }}>Critical</div>
                <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#c62828' }}>{report.summary.critical_count}</div>
              </div>
              <div>
                <div style={{ fontWeight: 'bold', color: '#666', fontSize: '0.9em' }}>High</div>
                <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#ef6c00' }}>{report.summary.high_count}</div>
              </div>
              <div>
                <div style={{ fontWeight: 'bold', color: '#666', fontSize: '0.9em' }}>Medium</div>
                <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#f57f17' }}>{report.summary.medium_count}</div>
              </div>
              <div>
                <div style={{ fontWeight: 'bold', color: '#666', fontSize: '0.9em' }}>Low</div>
                <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#2e7d32' }}>{report.summary.low_count}</div>
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
                <div style={{ fontWeight: 'bold', color: '#666', fontSize: '0.9em' }}>Languages</div>
                <div>{report.metadata.languages_detected.join(', ')}</div>
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
              <option value="critical">Critical ({report.summary.critical_count})</option>
              <option value="high">High ({report.summary.high_count})</option>
              <option value="medium">Medium ({report.summary.medium_count})</option>
              <option value="low">Low ({report.summary.low_count})</option>
            </select>
          </div>

          {/* Findings List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {filteredFindings.map((finding) => (
              <div
                key={finding.id}
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
                      {finding.file_path}:{finding.line_number}
                      {finding.column_number && `:${finding.column_number}`}
                    </div>
                  </div>
                  <span style={getSeverityStyle(finding.severity)}>
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

                {finding.code_snippet && renderCodeSnippet(finding.code_snippet, finding.file_path)}

                {/* Feedback Button for Finding */}
                <FeedbackButton
                  scanId={report.scan_info.scan_id}
                  itemId={finding.id}
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
          {report.llm_analysis.map((insight, index) => (
            <div
              key={index}
              style={{
                backgroundColor: 'white',
                border: '1px solid #e9ecef',
                borderRadius: '8px',
                padding: '20px',
              }}
            >
              <h3 style={{ marginTop: 0, marginBottom: '12px', color: '#1976d2' }}>
                {insight.section}
              </h3>
              <div style={{
                lineHeight: '1.6',
                whiteSpace: 'pre-wrap',
              }}>
                {insight.content}
              </div>
              {insight.confidence_score && (
                <div style={{
                  marginTop: '12px',
                  fontSize: '0.9em',
                  color: '#666',
                }}>
                  Confidence: {Math.round(insight.confidence_score * 100)}%
                  {insight.model_used && ` • Model: ${insight.model_used}`}
                </div>
              )}

              {/* Feedback Button for LLM Insight */}
              <FeedbackButton
                scanId={report.scan_info.scan_id}
                itemId={`insight-${index}`}
                feedbackType="llm_insight"
                itemContent={insight.content}
                suggestionType={insight.section}
                onFeedbackSubmitted={(response) => {
                  console.log('Feedback submitted for insight:', response);
                }}
              />
            </div>
          ))}

          {report.llm_analysis.length === 0 && (
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
                {diagram.diagram_type} - {diagram.format}
              </h3>
              <DiagramDisplay diagram={diagram} />
              
              {/* Feedback Button for Diagram */}
              <FeedbackButton
                scanId={report.scan_info.scan_id}
                itemId={`diagram-${index}`}
                feedbackType="diagram"
                itemContent={`${diagram.diagram_type} diagram`}
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