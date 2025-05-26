/**
 * ScanForm component for initiating code scans.
 * 
 * This component provides a form interface for users to initiate
 * new code scans for both PR and project scans with validation.
 */

import React, { useState, useCallback } from 'react';
import { ScanType, ScanRequest, ScanInitiateResponse } from '../types';

interface ScanFormProps {
  className?: string;
  onScanInitiated?: (response: ScanInitiateResponse) => void;
  onCancel?: () => void;
  initialData?: Partial<ScanRequest>;
}

/**
 * Form component for initiating new scans.
 * 
 * Args:
 *   className: Additional CSS classes
 *   onScanInitiated: Callback when scan is successfully initiated
 *   onCancel: Callback when form is cancelled
 *   initialData: Initial form data
 * 
 * Returns:
 *   JSX.Element: Rendered scan form component
 */
const ScanForm: React.FC<ScanFormProps> = ({ 
  className = '', 
  onScanInitiated,
  onCancel,
  initialData = {}
}) => {
  // Form state
  const [formData, setFormData] = useState<ScanRequest>({
    repo_url: initialData.repo_url || '',
    scan_type: initialData.scan_type || 'pr',
    pr_id: initialData.pr_id,
    target_branch: initialData.target_branch || 'main',
    source_branch: initialData.source_branch || '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string>('');

  // Handle input changes
  const handleInputChange = useCallback((field: keyof ScanRequest, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  }, [errors]);

  // Validate form
  const validateForm = useCallback((): boolean => {
    const newErrors: Record<string, string> = {};

    // Repository URL validation
    if (!formData.repo_url.trim()) {
      newErrors.repo_url = 'Repository URL is required';
    } else if (!isValidGitUrl(formData.repo_url)) {
      newErrors.repo_url = 'Please enter a valid Git repository URL';
    }

    // PR-specific validation
    if (formData.scan_type === 'pr') {
      if (!formData.pr_id || formData.pr_id <= 0) {
        newErrors.pr_id = 'PR ID is required for PR scans';
      }
      if (!formData.source_branch?.trim()) {
        newErrors.source_branch = 'Source branch is required for PR scans';
      }
    }

    // Target branch validation for project scans
    if (formData.scan_type === 'project' && !formData.target_branch?.trim()) {
      newErrors.target_branch = 'Target branch is required for project scans';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  // Submit form
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setSubmitError('');

    try {
      // Call backend API to initiate scan
      const response = await fetch('/api/scans/initiate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to initiate scan');
      }

      const result: ScanInitiateResponse = await response.json();
      
      // Call success callback
      if (onScanInitiated) {
        onScanInitiated(result);
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred';
      setSubmitError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, validateForm, onScanInitiated]);

  // Helper function to validate Git URLs
  const isValidGitUrl = (url: string): boolean => {
    const gitUrlPattern = /^(https?:\/\/|git@)[\w\.-]+[:\w\.-]+\.git$|^https?:\/\/[\w\.-]+\/[\w\.-]+\/[\w\.-]+\/?$/;
    return gitUrlPattern.test(url.trim());
  };

  // Render form field with error handling
  const renderField = (
    label: string,
    field: keyof ScanRequest,
    type: 'text' | 'number' = 'text',
    placeholder?: string,
    required: boolean = false
  ) => (
    <div style={{ marginBottom: '16px' }}>
      <label style={{
        display: 'block',
        marginBottom: '6px',
        fontWeight: '500',
        color: '#333',
      }}>
        {label} {required && <span style={{ color: '#f44336' }}>*</span>}
      </label>
      <input
        type={type}
        value={formData[field] || ''}
        onChange={(e) => handleInputChange(field, type === 'number' ? parseInt(e.target.value) || 0 : e.target.value)}
        placeholder={placeholder}
        disabled={isSubmitting}
        style={{
          width: '100%',
          padding: '10px',
          border: errors[field] ? '2px solid #f44336' : '1px solid #ddd',
          borderRadius: '4px',
          fontSize: '14px',
          backgroundColor: isSubmitting ? '#f5f5f5' : 'white',
        }}
      />
      {errors[field] && (
        <div style={{
          color: '#f44336',
          fontSize: '12px',
          marginTop: '4px',
        }}>
          {errors[field]}
        </div>
      )}
    </div>
  );

  return (
    <div className={`scan-form ${className}`}>
      <form onSubmit={handleSubmit} style={{
        maxWidth: '600px',
        margin: '0 auto',
        backgroundColor: 'white',
        padding: '24px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}>
        <h2 style={{
          marginBottom: '24px',
          color: '#333',
          textAlign: 'center',
        }}>
          Initiate Code Scan
        </h2>

        {/* Scan Type Selection */}
        <div style={{ marginBottom: '16px' }}>
          <label style={{
            display: 'block',
            marginBottom: '6px',
            fontWeight: '500',
            color: '#333',
          }}>
            Scan Type <span style={{ color: '#f44336' }}>*</span>
          </label>
          <div style={{ display: 'flex', gap: '16px' }}>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                value="pr"
                checked={formData.scan_type === 'pr'}
                onChange={(e) => handleInputChange('scan_type', e.target.value as ScanType)}
                disabled={isSubmitting}
                style={{ marginRight: '8px' }}
              />
              Pull Request Scan
            </label>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                value="project"
                checked={formData.scan_type === 'project'}
                onChange={(e) => handleInputChange('scan_type', e.target.value as ScanType)}
                disabled={isSubmitting}
                style={{ marginRight: '8px' }}
              />
              Full Project Scan
            </label>
          </div>
        </div>

        {/* Repository URL */}
        {renderField(
          'Repository URL', 
          'repo_url', 
          'text', 
          'https://github.com/owner/repo.git or https://github.com/owner/repo',
          true
        )}

        {/* PR-specific fields */}
        {formData.scan_type === 'pr' && (
          <>
            {renderField(
              'Pull Request ID',
              'pr_id',
              'number',
              'e.g., 123',
              true
            )}
            {renderField(
              'Source Branch',
              'source_branch',
              'text',
              'e.g., feature/new-feature',
              true
            )}
            {renderField(
              'Target Branch',
              'target_branch',
              'text',
              'e.g., main, master, develop'
            )}
          </>
        )}

        {/* Project-specific fields */}
        {formData.scan_type === 'project' && (
          <>
            {renderField(
              'Branch to Scan',
              'target_branch',
              'text',
              'e.g., main, master, develop',
              true
            )}
          </>
        )}

        {/* Submit Error */}
        {submitError && (
          <div style={{
            backgroundColor: '#ffebee',
            border: '1px solid #f44336',
            borderRadius: '4px',
            padding: '12px',
            marginBottom: '16px',
            color: '#c62828',
          }}>
            <strong>Error:</strong> {submitError}
          </div>
        )}

        {/* Action Buttons */}
        <div style={{
          display: 'flex',
          gap: '12px',
          justifyContent: 'flex-end',
          marginTop: '24px',
        }}>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              disabled={isSubmitting}
              style={{
                padding: '10px 20px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                backgroundColor: 'white',
                color: '#666',
                cursor: isSubmitting ? 'not-allowed' : 'pointer',
                fontSize: '14px',
              }}
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              padding: '10px 20px',
              border: 'none',
              borderRadius: '4px',
              backgroundColor: isSubmitting ? '#ccc' : '#1976d2',
              color: 'white',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: '500',
            }}
          >
            {isSubmitting ? 'Initiating Scan...' : 'Start Scan'}
          </button>
        </div>

        {/* Help Text */}
        <div style={{
          marginTop: '20px',
          fontSize: '12px',
          color: '#666',
          lineHeight: '1.4',
        }}>
          <strong>Tip:</strong> {formData.scan_type === 'pr' 
            ? 'PR scans analyze the differences between source and target branches, providing focused feedback on changed code.'
            : 'Project scans analyze the entire codebase, providing comprehensive insights into code quality and architecture.'
          }
        </div>
      </form>
    </div>
  );
};

export default ScanForm; 