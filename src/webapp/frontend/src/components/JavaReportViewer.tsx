/**
 * JavaReportViewer component for displaying Java-specific analysis reports.
 * 
 * This component provides specialized functionality for Java code analysis results
 * including class structures, dependency analysis, and Java-specific patterns.
 */

import React, { useState } from 'react';
import { CodeAnalysisReport, AnalysisIssue } from '../types';

interface JavaReportViewerProps {
  report: CodeAnalysisReport;
  className?: string;
  onClassClick?: (className: string) => void;
  onMethodClick?: (className: string, methodName: string) => void;
  onPackageClick?: (packageName: string) => void;
  showMetrics?: boolean;
  showDependencies?: boolean;
}

interface JavaClass {
  name: string;
  package: string;
  type: 'class' | 'interface' | 'enum' | 'annotation';
  methods: JavaMethod[];
  fields: JavaField[];
  dependencies: string[];
  annotations: string[];
}

interface JavaMethod {
  name: string;
  returnType: string;
  parameters: JavaParameter[];
  visibility: 'public' | 'private' | 'protected' | 'package';
  isStatic: boolean;
  isAbstract: boolean;
  annotations: string[];
}

interface JavaParameter {
  name: string;
  type: string;
}

interface JavaField {
  name: string;
  type: string;
  visibility: 'public' | 'private' | 'protected' | 'package';
  isStatic: boolean;
  isFinal: boolean;
}

interface JavaMetrics {
  totalClasses: number;
  totalMethods: number;
  totalFields: number;
  averageMethodsPerClass: number;
  cyclomaticComplexity: number;
  linesOfCode: number;
  packageCount: number;
}

/**
 * Component for displaying Java-specific analysis reports with detailed views.
 * 
 * Args:
 *   report: Code analysis report containing Java data
 *   className: Additional CSS classes
 *   onClassClick: Callback when a class is clicked
 *   onMethodClick: Callback when a method is clicked
 *   onPackageClick: Callback when a package is clicked
 *   showMetrics: Whether to show code metrics (default: true)
 *   showDependencies: Whether to show dependency analysis (default: true)
 * 
 * Returns:
 *   JSX.Element: Rendered Java report viewer component
 */
const JavaReportViewer: React.FC<JavaReportViewerProps> = ({
  report,
  className = '',
  onClassClick,
  onMethodClick,
  onPackageClick,
  showMetrics = true,
  showDependencies = true,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'classes' | 'packages' | 'issues' | 'metrics'>('overview');
  const [selectedClass, setSelectedClass] = useState<string | null>(null);
  const [expandedPackages, setExpandedPackages] = useState<Set<string>>(new Set());

  // Parse Java-specific data from the report
  const parseJavaData = (): {
    classes: JavaClass[];
    packages: Record<string, string[]>;
    metrics: JavaMetrics;
  } => {
    // This would typically parse actual Java analysis data
    // For now, we'll create mock data structure
    const classes: JavaClass[] = [];
    const packages: Record<string, string[]> = {};
    const metrics: JavaMetrics = {
      totalClasses: 0,
      totalMethods: 0,
      totalFields: 0,
      averageMethodsPerClass: 0,
      cyclomaticComplexity: 0,
      linesOfCode: 0,
      packageCount: 0,
    };

    // Parse from report.analysis_result if available
    if (report.analysis_result) {
      try {
        const data = typeof report.analysis_result === 'string' 
          ? JSON.parse(report.analysis_result) 
          : report.analysis_result;
        
        // Extract Java-specific information
        if (data.java_classes) {
          data.java_classes.forEach((cls: any) => {
            classes.push({
              name: cls.name || 'Unknown',
              package: cls.package || 'default',
              type: cls.type || 'class',
              methods: cls.methods || [],
              fields: cls.fields || [],
              dependencies: cls.dependencies || [],
              annotations: cls.annotations || [],
            });
          });
        }

        if (data.java_metrics) {
          Object.assign(metrics, data.java_metrics);
        }
      } catch (error) {
        console.warn('Failed to parse Java data from report:', error);
      }
    }

    // Group classes by package
    classes.forEach(cls => {
      if (!packages[cls.package]) {
        packages[cls.package] = [];
      }
      packages[cls.package].push(cls.name);
    });

    // Calculate derived metrics
    metrics.totalClasses = classes.length;
    metrics.totalMethods = classes.reduce((sum, cls) => sum + cls.methods.length, 0);
    metrics.totalFields = classes.reduce((sum, cls) => sum + cls.fields.length, 0);
    metrics.averageMethodsPerClass = metrics.totalClasses > 0 ? metrics.totalMethods / metrics.totalClasses : 0;
    metrics.packageCount = Object.keys(packages).length;

    return { classes, packages, metrics };
  };

  const { classes, packages, metrics } = parseJavaData();

  // Filter issues specific to Java
  const javaIssues = report.issues?.filter(issue => 
    issue.category?.toLowerCase().includes('java') ||
    issue.message?.toLowerCase().includes('java') ||
    issue.file_path?.endsWith('.java')
  ) || [];

  // Render overview tab
  const renderOverview = () => (
    <div style={{ padding: '16px' }}>
      <h3 style={{ marginBottom: '16px', color: '#333' }}>Java Analysis Overview</h3>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '24px',
      }}>
        <div style={{
          padding: '16px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #e9ecef',
        }}>
          <h4 style={{ margin: '0 0 8px 0', color: '#007bff' }}>Classes</h4>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{metrics.totalClasses}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>Total classes found</div>
        </div>
        
        <div style={{
          padding: '16px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #e9ecef',
        }}>
          <h4 style={{ margin: '0 0 8px 0', color: '#28a745' }}>Methods</h4>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{metrics.totalMethods}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>Average: {metrics.averageMethodsPerClass.toFixed(1)} per class</div>
        </div>
        
        <div style={{
          padding: '16px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #e9ecef',
        }}>
          <h4 style={{ margin: '0 0 8px 0', color: '#ffc107' }}>Packages</h4>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{metrics.packageCount}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>Package organization</div>
        </div>
        
        <div style={{
          padding: '16px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #e9ecef',
        }}>
          <h4 style={{ margin: '0 0 8px 0', color: '#dc3545' }}>Issues</h4>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{javaIssues.length}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>Java-specific issues</div>
        </div>
      </div>

      {javaIssues.length > 0 && (
        <div style={{
          padding: '16px',
          backgroundColor: '#fff3cd',
          border: '1px solid #ffeaa7',
          borderRadius: '8px',
          marginBottom: '16px',
        }}>
          <h4 style={{ margin: '0 0 12px 0', color: '#856404' }}>Key Issues Found</h4>
          {javaIssues.slice(0, 3).map((issue, index) => (
            <div key={index} style={{ marginBottom: '8px' }}>
              <span style={{
                padding: '2px 6px',
                backgroundColor: getSeverityColor(issue.severity),
                color: 'white',
                borderRadius: '4px',
                fontSize: '10px',
                marginRight: '8px',
              }}>
                {issue.severity}
              </span>
              <span style={{ fontSize: '14px' }}>{issue.message}</span>
            </div>
          ))}
          {javaIssues.length > 3 && (
            <div style={{ fontSize: '12px', color: '#666', marginTop: '8px' }}>
              And {javaIssues.length - 3} more issues...
            </div>
          )}
        </div>
      )}
    </div>
  );

  // Render classes tab
  const renderClasses = () => (
    <div style={{ padding: '16px' }}>
      <h3 style={{ marginBottom: '16px', color: '#333' }}>Java Classes ({classes.length})</h3>
      
      <div style={{ display: 'grid', gap: '12px' }}>
        {classes.map((cls, index) => (
          <div
            key={index}
            onClick={() => {
              setSelectedClass(selectedClass === cls.name ? null : cls.name);
              if (onClassClick) onClassClick(cls.name);
            }}
            style={{
              border: '1px solid #e9ecef',
              borderRadius: '8px',
              backgroundColor: selectedClass === cls.name ? '#e3f2fd' : 'white',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            <div style={{
              padding: '12px 16px',
              borderBottom: selectedClass === cls.name ? '1px solid #e9ecef' : 'none',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{
                  padding: '2px 8px',
                  backgroundColor: getClassTypeColor(cls.type),
                  color: 'white',
                  borderRadius: '4px',
                  fontSize: '10px',
                  fontWeight: 'bold',
                }}>
                  {cls.type.toUpperCase()}
                </span>
                <strong style={{ fontSize: '16px' }}>{cls.name}</strong>
              </div>
              <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                Package: {cls.package} • {cls.methods.length} methods • {cls.fields.length} fields
              </div>
            </div>
            
            {selectedClass === cls.name && (
              <div style={{ padding: '16px' }}>
                {cls.methods.length > 0 && (
                  <div style={{ marginBottom: '16px' }}>
                    <h5 style={{ margin: '0 0 8px 0', color: '#495057' }}>Methods</h5>
                    <div style={{ fontSize: '12px' }}>
                      {cls.methods.map((method, methodIndex) => (
                        <div
                          key={methodIndex}
                          onClick={(e) => {
                            e.stopPropagation();
                            if (onMethodClick) onMethodClick(cls.name, method.name);
                          }}
                          style={{
                            padding: '6px 8px',
                            margin: '2px 0',
                            backgroundColor: '#f8f9fa',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            border: '1px solid #e9ecef',
                          }}
                        >
                          <span style={{
                            padding: '1px 4px',
                            backgroundColor: getVisibilityColor(method.visibility),
                            color: 'white',
                            borderRadius: '2px',
                            fontSize: '9px',
                            marginRight: '6px',
                          }}>
                            {method.visibility}
                          </span>
                          <code>{method.returnType} {method.name}({method.parameters.map(p => `${p.type} ${p.name}`).join(', ')})</code>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {cls.fields.length > 0 && (
                  <div>
                    <h5 style={{ margin: '0 0 8px 0', color: '#495057' }}>Fields</h5>
                    <div style={{ fontSize: '12px' }}>
                      {cls.fields.map((field, fieldIndex) => (
                        <div
                          key={fieldIndex}
                          style={{
                            padding: '4px 8px',
                            margin: '2px 0',
                            backgroundColor: '#f1f3f4',
                            borderRadius: '4px',
                          }}
                        >
                          <span style={{
                            padding: '1px 4px',
                            backgroundColor: getVisibilityColor(field.visibility),
                            color: 'white',
                            borderRadius: '2px',
                            fontSize: '9px',
                            marginRight: '6px',
                          }}>
                            {field.visibility}
                          </span>
                          <code>{field.type} {field.name}</code>
                          {field.isStatic && <span style={{ color: '#666', fontSize: '10px' }}> (static)</span>}
                          {field.isFinal && <span style={{ color: '#666', fontSize: '10px' }}> (final)</span>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  // Render packages tab
  const renderPackages = () => (
    <div style={{ padding: '16px' }}>
      <h3 style={{ marginBottom: '16px', color: '#333' }}>Package Structure ({metrics.packageCount} packages)</h3>
      
      <div style={{ display: 'grid', gap: '8px' }}>
        {Object.entries(packages).map(([packageName, classNames]) => (
          <div key={packageName} style={{
            border: '1px solid #e9ecef',
            borderRadius: '8px',
            backgroundColor: 'white',
          }}>
            <div
              onClick={() => {
                const newExpanded = new Set(expandedPackages);
                if (newExpanded.has(packageName)) {
                  newExpanded.delete(packageName);
                } else {
                  newExpanded.add(packageName);
                }
                setExpandedPackages(newExpanded);
                if (onPackageClick) onPackageClick(packageName);
              }}
              style={{
                padding: '12px 16px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <strong style={{ fontSize: '14px' }}>{packageName}</strong>
                <div style={{ fontSize: '12px', color: '#666' }}>
                  {classNames.length} class{classNames.length !== 1 ? 'es' : ''}
                </div>
              </div>
              <span style={{ fontSize: '12px', color: '#666' }}>
                {expandedPackages.has(packageName) ? '▼' : '▶'}
              </span>
            </div>
            
            {expandedPackages.has(packageName) && (
              <div style={{
                padding: '8px 16px 16px 16px',
                borderTop: '1px solid #e9ecef',
                backgroundColor: '#f8f9fa',
              }}>
                {classNames.map((className, index) => (
                  <div
                    key={index}
                    onClick={() => {
                      if (onClassClick) onClassClick(className);
                    }}
                    style={{
                      padding: '4px 8px',
                      margin: '2px 0',
                      backgroundColor: 'white',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      border: '1px solid #e9ecef',
                    }}
                  >
                    📄 {className}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  // Render issues tab
  const renderIssues = () => (
    <div style={{ padding: '16px' }}>
      <h3 style={{ marginBottom: '16px', color: '#333' }}>Java Issues ({javaIssues.length})</h3>
      
      {javaIssues.length === 0 ? (
        <div style={{
          padding: '20px',
          textAlign: 'center',
          color: '#28a745',
          backgroundColor: '#d4edda',
          border: '1px solid #c3e6cb',
          borderRadius: '8px',
        }}>
          🎉 No Java-specific issues found!
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '12px' }}>
          {javaIssues.map((issue, index) => (
            <div
              key={index}
              style={{
                padding: '16px',
                border: '1px solid #e9ecef',
                borderRadius: '8px',
                backgroundColor: 'white',
                borderLeft: `4px solid ${getSeverityColor(issue.severity)}`,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span style={{
                  padding: '2px 8px',
                  backgroundColor: getSeverityColor(issue.severity),
                  color: 'white',
                  borderRadius: '4px',
                  fontSize: '10px',
                  fontWeight: 'bold',
                }}>
                  {issue.severity}
                </span>
                <span style={{
                  padding: '2px 8px',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  borderRadius: '4px',
                  fontSize: '10px',
                }}>
                  {issue.category || 'General'}
                </span>
              </div>
              
              <div style={{ fontSize: '14px', fontWeight: '500', marginBottom: '4px' }}>
                {issue.message}
              </div>
              
              {issue.file_path && (
                <div style={{ fontSize: '12px', color: '#666' }}>
                  📄 {issue.file_path}
                  {issue.line_number && ` (line ${issue.line_number})`}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );

  // Render metrics tab
  const renderMetrics = () => (
    <div style={{ padding: '16px' }}>
      <h3 style={{ marginBottom: '16px', color: '#333' }}>Code Metrics</h3>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '16px',
      }}>
        <div style={{
          padding: '16px',
          border: '1px solid #e9ecef',
          borderRadius: '8px',
          backgroundColor: 'white',
        }}>
          <h4 style={{ margin: '0 0 12px 0', color: '#007bff' }}>Code Structure</h4>
          <div style={{ fontSize: '12px', lineHeight: '1.6' }}>
            <div>Total Classes: <strong>{metrics.totalClasses}</strong></div>
            <div>Total Methods: <strong>{metrics.totalMethods}</strong></div>
            <div>Total Fields: <strong>{metrics.totalFields}</strong></div>
            <div>Packages: <strong>{metrics.packageCount}</strong></div>
          </div>
        </div>
        
        <div style={{
          padding: '16px',
          border: '1px solid #e9ecef',
          borderRadius: '8px',
          backgroundColor: 'white',
        }}>
          <h4 style={{ margin: '0 0 12px 0', color: '#28a745' }}>Quality Metrics</h4>
          <div style={{ fontSize: '12px', lineHeight: '1.6' }}>
            <div>Avg Methods/Class: <strong>{metrics.averageMethodsPerClass.toFixed(1)}</strong></div>
            <div>Cyclomatic Complexity: <strong>{metrics.cyclomaticComplexity || 'N/A'}</strong></div>
            <div>Lines of Code: <strong>{metrics.linesOfCode || 'N/A'}</strong></div>
          </div>
        </div>
      </div>
    </div>
  );

  // Helper functions for styling
  const getSeverityColor = (severity: string): string => {
    switch (severity?.toLowerCase()) {
      case 'high': return '#dc3545';
      case 'medium': return '#fd7e14';
      case 'low': return '#ffc107';
      default: return '#6c757d';
    }
  };

  const getClassTypeColor = (type: string): string => {
    switch (type) {
      case 'class': return '#007bff';
      case 'interface': return '#28a745';
      case 'enum': return '#ffc107';
      case 'annotation': return '#6f42c1';
      default: return '#6c757d';
    }
  };

  const getVisibilityColor = (visibility: string): string => {
    switch (visibility) {
      case 'public': return '#28a745';
      case 'private': return '#dc3545';
      case 'protected': return '#fd7e14';
      case 'package': return '#6c757d';
      default: return '#6c757d';
    }
  };

  // Render tab navigation
  const renderTabs = () => {
    const tabs = [
      { id: 'overview', label: 'Overview' },
      { id: 'classes', label: `Classes (${classes.length})` },
      { id: 'packages', label: `Packages (${metrics.packageCount})` },
      { id: 'issues', label: `Issues (${javaIssues.length})` },
      { id: 'metrics', label: 'Metrics' },
    ];

    return (
      <div style={{
        borderBottom: '1px solid #e9ecef',
        marginBottom: '0',
        backgroundColor: '#f8f9fa',
      }}>
        <div style={{ display: 'flex', overflowX: 'auto' }}>
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              style={{
                padding: '12px 16px',
                border: 'none',
                backgroundColor: activeTab === tab.id ? 'white' : 'transparent',
                borderBottom: activeTab === tab.id ? '2px solid #007bff' : '2px solid transparent',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: activeTab === tab.id ? '500' : 'normal',
                color: activeTab === tab.id ? '#007bff' : '#495057',
                minWidth: 'max-content',
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className={`java-report-viewer ${className}`}>
      <div style={{
        border: '1px solid #e9ecef',
        borderRadius: '8px',
        backgroundColor: 'white',
        overflow: 'hidden',
      }}>
        <div style={{
          padding: '16px',
          backgroundColor: '#f8f9fa',
          borderBottom: '1px solid #e9ecef',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}>
          <span style={{ fontSize: '20px' }}>☕</span>
          <h2 style={{ margin: 0, color: '#333' }}>Java Analysis Report</h2>
          <span style={{
            padding: '4px 8px',
            backgroundColor: '#007bff',
            color: 'white',
            borderRadius: '4px',
            fontSize: '12px',
            marginLeft: 'auto',
          }}>
            {report.language?.toUpperCase() || 'JAVA'}
          </span>
        </div>

        {renderTabs()}

        <div style={{ minHeight: '400px' }}>
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'classes' && renderClasses()}
          {activeTab === 'packages' && renderPackages()}
          {activeTab === 'issues' && renderIssues()}
          {activeTab === 'metrics' && renderMetrics()}
        </div>
      </div>
    </div>
  );
};

export default JavaReportViewer; 