/**
 * KotlinReportViewer component for displaying Kotlin-specific analysis reports.
 * 
 * This component provides specialized functionality for Kotlin code analysis results
 * including class structures, extension functions, data classes, and Kotlin-specific patterns.
 */

import React, { useState } from 'react';
import { CodeAnalysisReport, AnalysisIssue } from '../types';

interface KotlinReportViewerProps {
  report: CodeAnalysisReport;
  className?: string;
  onClassClick?: (className: string) => void;
  onFunctionClick?: (className: string, functionName: string) => void;
  onPackageClick?: (packageName: string) => void;
  showMetrics?: boolean;
  showExtensions?: boolean;
}

interface KotlinClass {
  name: string;
  package: string;
  type: 'class' | 'data class' | 'sealed class' | 'object' | 'interface' | 'enum class';
  functions: KotlinFunction[];
  properties: KotlinProperty[];
  companions: KotlinCompanion[];
  extensions: KotlinExtension[];
  annotations: string[];
}

interface KotlinFunction {
  name: string;
  returnType: string;
  parameters: KotlinParameter[];
  visibility: 'public' | 'private' | 'protected' | 'internal';
  isInline: boolean;
  isSuspend: boolean;
  isExtension: boolean;
  annotations: string[];
}

interface KotlinParameter {
  name: string;
  type: string;
  hasDefaultValue: boolean;
  isVararg: boolean;
}

interface KotlinProperty {
  name: string;
  type: string;
  visibility: 'public' | 'private' | 'protected' | 'internal';
  isVal: boolean;
  isLateInit: boolean;
  hasCustomGetter: boolean;
  hasCustomSetter: boolean;
}

interface KotlinCompanion {
  name?: string;
  functions: KotlinFunction[];
  properties: KotlinProperty[];
}

interface KotlinExtension {
  receiverType: string;
  functionName: string;
  returnType: string;
  parameters: KotlinParameter[];
}

interface KotlinMetrics {
  totalClasses: number;
  totalFunctions: number;
  totalProperties: number;
  dataClasses: number;
  sealedClasses: number;
  objects: number;
  extensionFunctions: number;
  inlineFunctions: number;
  suspendFunctions: number;
  packageCount: number;
}

/**
 * Component for displaying Kotlin-specific analysis reports with detailed views.
 * 
 * Args:
 *   report: Code analysis report containing Kotlin data
 *   className: Additional CSS classes
 *   onClassClick: Callback when a class is clicked
 *   onFunctionClick: Callback when a function is clicked
 *   onPackageClick: Callback when a package is clicked
 *   showMetrics: Whether to show code metrics (default: true)
 *   showExtensions: Whether to show extension functions (default: true)
 * 
 * Returns:
 *   JSX.Element: Rendered Kotlin report viewer component
 */
const KotlinReportViewer: React.FC<KotlinReportViewerProps> = ({
  report,
  className = '',
  onClassClick,
  onFunctionClick,
  onPackageClick,
  showMetrics = true,
  showExtensions = true,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'classes' | 'extensions' | 'packages' | 'issues' | 'metrics'>('overview');
  const [selectedClass, setSelectedClass] = useState<string | null>(null);
  const [expandedPackages, setExpandedPackages] = useState<Set<string>>(new Set());

  // Parse Kotlin-specific data from the report
  const parseKotlinData = (): {
    classes: KotlinClass[];
    packages: Record<string, string[]>;
    extensions: KotlinExtension[];
    metrics: KotlinMetrics;
  } => {
    const classes: KotlinClass[] = [];
    const packages: Record<string, string[]> = {};
    const extensions: KotlinExtension[] = [];
    const metrics: KotlinMetrics = {
      totalClasses: 0,
      totalFunctions: 0,
      totalProperties: 0,
      dataClasses: 0,
      sealedClasses: 0,
      objects: 0,
      extensionFunctions: 0,
      inlineFunctions: 0,
      suspendFunctions: 0,
      packageCount: 0,
    };

    // Parse from report.analysis_result if available
    if (report.analysis_result) {
      try {
        const data = typeof report.analysis_result === 'string' 
          ? JSON.parse(report.analysis_result) 
          : report.analysis_result;
        
        // Extract Kotlin-specific information
        if (data.kotlin_classes) {
          data.kotlin_classes.forEach((cls: any) => {
            classes.push({
              name: cls.name || 'Unknown',
              package: cls.package || 'default',
              type: cls.type || 'class',
              functions: cls.functions || [],
              properties: cls.properties || [],
              companions: cls.companions || [],
              extensions: cls.extensions || [],
              annotations: cls.annotations || [],
            });
          });
        }

        if (data.kotlin_extensions) {
          extensions.push(...data.kotlin_extensions);
        }

        if (data.kotlin_metrics) {
          Object.assign(metrics, data.kotlin_metrics);
        }
      } catch (error) {
        console.warn('Failed to parse Kotlin data from report:', error);
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
    metrics.totalFunctions = classes.reduce((sum, cls) => sum + cls.functions.length, 0);
    metrics.totalProperties = classes.reduce((sum, cls) => sum + cls.properties.length, 0);
    metrics.dataClasses = classes.filter(cls => cls.type === 'data class').length;
    metrics.sealedClasses = classes.filter(cls => cls.type === 'sealed class').length;
    metrics.objects = classes.filter(cls => cls.type === 'object').length;
    metrics.extensionFunctions = extensions.length + classes.reduce((sum, cls) => 
      sum + cls.functions.filter(fn => fn.isExtension).length, 0);
    metrics.inlineFunctions = classes.reduce((sum, cls) => 
      sum + cls.functions.filter(fn => fn.isInline).length, 0);
    metrics.suspendFunctions = classes.reduce((sum, cls) => 
      sum + cls.functions.filter(fn => fn.isSuspend).length, 0);
    metrics.packageCount = Object.keys(packages).length;

    return { classes, packages, extensions, metrics };
  };

  const { classes, packages, extensions, metrics } = parseKotlinData();

  // Filter issues specific to Kotlin
  const kotlinIssues = report.issues?.filter(issue => 
    issue.category?.toLowerCase().includes('kotlin') ||
    issue.message?.toLowerCase().includes('kotlin') ||
    issue.file_path?.endsWith('.kt') ||
    issue.file_path?.endsWith('.kts')
  ) || [];

  // Render overview tab
  const renderOverview = () => (
    <div style={{ padding: '16px' }}>
      <h3 style={{ marginBottom: '16px', color: '#333' }}>Kotlin Analysis Overview</h3>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '16px',
        marginBottom: '24px',
      }}>
        <div style={{
          padding: '16px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #e9ecef',
        }}>
          <h4 style={{ margin: '0 0 8px 0', color: '#7c4dff' }}>Classes</h4>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{metrics.totalClasses}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>Total classes found</div>
        </div>
        
        <div style={{
          padding: '16px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #e9ecef',
        }}>
          <h4 style={{ margin: '0 0 8px 0', color: '#ff5722' }}>Functions</h4>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{metrics.totalFunctions}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>{metrics.extensionFunctions} extensions</div>
        </div>
        
        <div style={{
          padding: '16px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #e9ecef',
        }}>
          <h4 style={{ margin: '0 0 8px 0', color: '#4caf50' }}>Data Classes</h4>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{metrics.dataClasses}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>Immutable data structures</div>
        </div>
        
        <div style={{
          padding: '16px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #e9ecef',
        }}>
          <h4 style={{ margin: '0 0 8px 0', color: '#ff9800' }}>Suspend Functions</h4>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{metrics.suspendFunctions}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>Coroutine functions</div>
        </div>
        
        <div style={{
          padding: '16px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #e9ecef',
        }}>
          <h4 style={{ margin: '0 0 8px 0', color: '#2196f3' }}>Objects</h4>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{metrics.objects}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>Singleton objects</div>
        </div>
        
        <div style={{
          padding: '16px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #e9ecef',
        }}>
          <h4 style={{ margin: '0 0 8px 0', color: '#dc3545' }}>Issues</h4>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{kotlinIssues.length}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>Kotlin-specific issues</div>
        </div>
      </div>

      {kotlinIssues.length > 0 && (
        <div style={{
          padding: '16px',
          backgroundColor: '#fff3cd',
          border: '1px solid #ffeaa7',
          borderRadius: '8px',
          marginBottom: '16px',
        }}>
          <h4 style={{ margin: '0 0 12px 0', color: '#856404' }}>Key Issues Found</h4>
          {kotlinIssues.slice(0, 3).map((issue, index) => (
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
          {kotlinIssues.length > 3 && (
            <div style={{ fontSize: '12px', color: '#666', marginTop: '8px' }}>
              And {kotlinIssues.length - 3} more issues...
            </div>
          )}
        </div>
      )}
    </div>
  );

  // Render classes tab
  const renderClasses = () => (
    <div style={{ padding: '16px' }}>
      <h3 style={{ marginBottom: '16px', color: '#333' }}>Kotlin Classes ({classes.length})</h3>
      
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
              backgroundColor: selectedClass === cls.name ? '#e8f5e8' : 'white',
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
                  backgroundColor: getKotlinClassTypeColor(cls.type),
                  color: 'white',
                  borderRadius: '4px',
                  fontSize: '10px',
                  fontWeight: 'bold',
                }}>
                  {cls.type.toUpperCase()}
                </span>
                <strong style={{ fontSize: '16px' }}>{cls.name}</strong>
                {cls.annotations.length > 0 && (
                  <span style={{ fontSize: '12px', color: '#666' }}>
                    @{cls.annotations.join(' @')}
                  </span>
                )}
              </div>
              <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                Package: {cls.package} • {cls.functions.length} functions • {cls.properties.length} properties
              </div>
            </div>
            
            {selectedClass === cls.name && (
              <div style={{ padding: '16px' }}>
                {cls.functions.length > 0 && (
                  <div style={{ marginBottom: '16px' }}>
                    <h5 style={{ margin: '0 0 8px 0', color: '#495057' }}>Functions</h5>
                    <div style={{ fontSize: '12px' }}>
                      {cls.functions.map((func, functionIndex) => (
                        <div
                          key={functionIndex}
                          onClick={(e) => {
                            e.stopPropagation();
                            if (onFunctionClick) onFunctionClick(cls.name, func.name);
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
                          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
                            <span style={{
                              padding: '1px 4px',
                              backgroundColor: getVisibilityColor(func.visibility),
                              color: 'white',
                              borderRadius: '2px',
                              fontSize: '9px',
                            }}>
                              {func.visibility}
                            </span>
                            {func.isInline && (
                              <span style={{
                                padding: '1px 4px',
                                backgroundColor: '#ff9800',
                                color: 'white',
                                borderRadius: '2px',
                                fontSize: '9px',
                              }}>
                                inline
                              </span>
                            )}
                            {func.isSuspend && (
                              <span style={{
                                padding: '1px 4px',
                                backgroundColor: '#9c27b0',
                                color: 'white',
                                borderRadius: '2px',
                                fontSize: '9px',
                              }}>
                                suspend
                              </span>
                            )}
                            {func.isExtension && (
                              <span style={{
                                padding: '1px 4px',
                                backgroundColor: '#2196f3',
                                color: 'white',
                                borderRadius: '2px',
                                fontSize: '9px',
                              }}>
                                ext
                              </span>
                            )}
                          </div>
                          <code>
                            fun {func.name}({func.parameters.map(p => 
                              `${p.name}: ${p.type}${p.hasDefaultValue ? ' = ...' : ''}${p.isVararg ? '...' : ''}`
                            ).join(', ')}): {func.returnType}
                          </code>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {cls.properties.length > 0 && (
                  <div style={{ marginBottom: '16px' }}>
                    <h5 style={{ margin: '0 0 8px 0', color: '#495057' }}>Properties</h5>
                    <div style={{ fontSize: '12px' }}>
                      {cls.properties.map((prop, propIndex) => (
                        <div
                          key={propIndex}
                          style={{
                            padding: '4px 8px',
                            margin: '2px 0',
                            backgroundColor: '#f1f3f4',
                            borderRadius: '4px',
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <span style={{
                              padding: '1px 4px',
                              backgroundColor: getVisibilityColor(prop.visibility),
                              color: 'white',
                              borderRadius: '2px',
                              fontSize: '9px',
                            }}>
                              {prop.visibility}
                            </span>
                            <code>
                              {prop.isVal ? 'val' : 'var'} {prop.name}: {prop.type}
                            </code>
                            {prop.isLateInit && <span style={{ color: '#666', fontSize: '10px' }}> (lateinit)</span>}
                            {prop.hasCustomGetter && <span style={{ color: '#666', fontSize: '10px' }}> (custom get)</span>}
                            {prop.hasCustomSetter && <span style={{ color: '#666', fontSize: '10px' }}> (custom set)</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {cls.companions.length > 0 && (
                  <div>
                    <h5 style={{ margin: '0 0 8px 0', color: '#495057' }}>Companion Objects</h5>
                    {cls.companions.map((companion, compIndex) => (
                      <div
                        key={compIndex}
                        style={{
                          padding: '8px',
                          margin: '4px 0',
                          backgroundColor: '#e3f2fd',
                          borderRadius: '4px',
                          fontSize: '12px',
                        }}
                      >
                        <strong>{companion.name || 'Companion'}</strong>
                        <div style={{ marginTop: '4px' }}>
                          {companion.functions.length} functions, {companion.properties.length} properties
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  // Render extensions tab
  const renderExtensions = () => (
    <div style={{ padding: '16px' }}>
      <h3 style={{ marginBottom: '16px', color: '#333' }}>Extension Functions ({extensions.length})</h3>
      
      {extensions.length === 0 ? (
        <div style={{
          padding: '20px',
          textAlign: 'center',
          color: '#666',
          backgroundColor: '#f8f9fa',
          border: '1px solid #e9ecef',
          borderRadius: '8px',
        }}>
          No extension functions found
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '8px' }}>
          {extensions.map((ext, index) => (
            <div
              key={index}
              style={{
                padding: '12px',
                border: '1px solid #e9ecef',
                borderRadius: '8px',
                backgroundColor: 'white',
                borderLeft: '4px solid #2196f3',
              }}
            >
              <div style={{ fontSize: '14px', fontWeight: '500', marginBottom: '4px' }}>
                <code>
                  fun {ext.receiverType}.{ext.functionName}({ext.parameters.map(p => 
                    `${p.name}: ${p.type}${p.hasDefaultValue ? ' = ...' : ''}`
                  ).join(', ')}): {ext.returnType}
                </code>
              </div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                Extends <strong>{ext.receiverType}</strong>
              </div>
            </div>
          ))}
        </div>
      )}
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

  const getKotlinClassTypeColor = (type: string): string => {
    switch (type) {
      case 'class': return '#7c4dff';
      case 'data class': return '#4caf50';
      case 'sealed class': return '#ff5722';
      case 'object': return '#2196f3';
      case 'interface': return '#ff9800';
      case 'enum class': return '#9c27b0';
      default: return '#6c757d';
    }
  };

  const getVisibilityColor = (visibility: string): string => {
    switch (visibility) {
      case 'public': return '#28a745';
      case 'private': return '#dc3545';
      case 'protected': return '#fd7e14';
      case 'internal': return '#6f42c1';
      default: return '#6c757d';
    }
  };

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
                    🎯 {className}
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
      <h3 style={{ marginBottom: '16px', color: '#333' }}>Kotlin Issues ({kotlinIssues.length})</h3>
      
      {kotlinIssues.length === 0 ? (
        <div style={{
          padding: '20px',
          textAlign: 'center',
          color: '#28a745',
          backgroundColor: '#d4edda',
          border: '1px solid #c3e6cb',
          borderRadius: '8px',
        }}>
          🎉 No Kotlin-specific issues found!
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '12px' }}>
          {kotlinIssues.map((issue, index) => (
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
                  🎯 {issue.file_path}
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
      <h3 style={{ marginBottom: '16px', color: '#333' }}>Kotlin Metrics</h3>
      
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
          <h4 style={{ margin: '0 0 12px 0', color: '#7c4dff' }}>Code Structure</h4>
          <div style={{ fontSize: '12px', lineHeight: '1.6' }}>
            <div>Total Classes: <strong>{metrics.totalClasses}</strong></div>
            <div>Total Functions: <strong>{metrics.totalFunctions}</strong></div>
            <div>Total Properties: <strong>{metrics.totalProperties}</strong></div>
            <div>Packages: <strong>{metrics.packageCount}</strong></div>
          </div>
        </div>
        
        <div style={{
          padding: '16px',
          border: '1px solid #e9ecef',
          borderRadius: '8px',
          backgroundColor: 'white',
        }}>
          <h4 style={{ margin: '0 0 12px 0', color: '#4caf50' }}>Kotlin Features</h4>
          <div style={{ fontSize: '12px', lineHeight: '1.6' }}>
            <div>Data Classes: <strong>{metrics.dataClasses}</strong></div>
            <div>Sealed Classes: <strong>{metrics.sealedClasses}</strong></div>
            <div>Objects: <strong>{metrics.objects}</strong></div>
            <div>Extension Functions: <strong>{metrics.extensionFunctions}</strong></div>
          </div>
        </div>
        
        <div style={{
          padding: '16px',
          border: '1px solid #e9ecef',
          borderRadius: '8px',
          backgroundColor: 'white',
        }}>
          <h4 style={{ margin: '0 0 12px 0', color: '#ff9800' }}>Advanced Features</h4>
          <div style={{ fontSize: '12px', lineHeight: '1.6' }}>
            <div>Inline Functions: <strong>{metrics.inlineFunctions}</strong></div>
            <div>Suspend Functions: <strong>{metrics.suspendFunctions}</strong></div>
          </div>
        </div>
      </div>
    </div>
  );

  // Render tab navigation
  const renderTabs = () => {
    const tabs = [
      { id: 'overview', label: 'Overview' },
      { id: 'classes', label: `Classes (${classes.length})` },
      { id: 'extensions', label: `Extensions (${extensions.length})` },
      { id: 'packages', label: `Packages (${metrics.packageCount})` },
      { id: 'issues', label: `Issues (${kotlinIssues.length})` },
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
                borderBottom: activeTab === tab.id ? '2px solid #7c4dff' : '2px solid transparent',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: activeTab === tab.id ? '500' : 'normal',
                color: activeTab === tab.id ? '#7c4dff' : '#495057',
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
    <div className={`kotlin-report-viewer ${className}`}>
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
          <span style={{ fontSize: '20px' }}>🎯</span>
          <h2 style={{ margin: 0, color: '#333' }}>Kotlin Analysis Report</h2>
          <span style={{
            padding: '4px 8px',
            backgroundColor: '#7c4dff',
            color: 'white',
            borderRadius: '4px',
            fontSize: '12px',
            marginLeft: 'auto',
          }}>
            {report.language?.toUpperCase() || 'KOTLIN'}
          </span>
        </div>

        {renderTabs()}

        <div style={{ minHeight: '400px' }}>
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'classes' && renderClasses()}
          {activeTab === 'extensions' && renderExtensions()}
          {activeTab === 'packages' && renderPackages()}
          {activeTab === 'issues' && renderIssues()}
          {activeTab === 'metrics' && renderMetrics()}
        </div>
      </div>
    </div>
  );
};

export default KotlinReportViewer; 