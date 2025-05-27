/**
 * FeedbackButton component for collecting user feedback on findings and LLM suggestions.
 * 
 * This component provides an interface for users to submit feedback on scan results,
 * which can be used to improve LLM performance and static analysis rules.
 */

import React, { useState } from 'react';
import { FeedbackRequest, FeedbackResponse, FeedbackType, FeedbackRating } from '../types';

interface FeedbackButtonProps {
  scanId: string;
  itemId?: string;
  feedbackType: FeedbackType;
  itemContent?: string;
  ruleId?: string;
  suggestionType?: string;
  onFeedbackSubmitted?: (response: FeedbackResponse) => void;
  className?: string;
}

/**
 * Component for submitting feedback on scan results.
 * 
 * Args:
 *   scanId: ID of the scan being reviewed
 *   itemId: ID of the specific item (finding, insight, etc.)
 *   feedbackType: Type of item being reviewed
 *   itemContent: Content of the item being reviewed
 *   ruleId: Rule ID for static analysis findings
 *   suggestionType: Type of LLM suggestion
 *   onFeedbackSubmitted: Callback when feedback is submitted
 *   className: Additional CSS classes
 * 
 * Returns:
 *   JSX.Element: Rendered feedback button and form
 */
const FeedbackButton: React.FC<FeedbackButtonProps> = ({
  scanId,
  itemId,
  feedbackType,
  itemContent,
  ruleId,
  suggestionType,
  onFeedbackSubmitted,
  className = ''
}) => {
  const [showForm, setShowForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'success' | 'error' | null>(null);
  const [formData, setFormData] = useState({
    isHelpful: true,
    rating: 'helpful' as FeedbackRating,
    comment: ''
  });

  const handleSubmitFeedback = async (isHelpful: boolean) => {
    if (!showForm) {
      // Quick feedback without form
      await submitFeedback(isHelpful, 'helpful', '');
    } else {
      // Full form submission
      await submitFeedback(formData.isHelpful, formData.rating, formData.comment);
    }
  };

  const submitFeedback = async (isHelpful: boolean, rating: FeedbackRating, comment: string) => {
    setIsSubmitting(true);
    setSubmitStatus(null);

    try {
      const feedbackRequest: FeedbackRequest = {
        scan_id: scanId,
        finding_id: itemId,
        feedback_type: feedbackType,
        is_helpful: isHelpful,
        rating: rating,
        comment: comment,
        item_content: itemContent,
        rule_id: ruleId,
        suggestion_type: suggestionType
      };

      const response = await fetch('/api/feedback/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedbackRequest),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: FeedbackResponse = await response.json();
      setSubmitStatus('success');
      setShowForm(false);
      
      if (onFeedbackSubmitted) {
        onFeedbackSubmitted(result);
      }

      // Reset form after successful submission
      setFormData({
        isHelpful: true,
        rating: 'helpful',
        comment: ''
      });

    } catch (error) {
      console.error('Error submitting feedback:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickFeedback = (isHelpful: boolean) => {
    setFormData({ ...formData, isHelpful });
    handleSubmitFeedback(isHelpful);
  };

  const toggleForm = () => {
    setShowForm(!showForm);
    setSubmitStatus(null);
  };

  const getRatingValue = (rating: FeedbackRating): number => {
    const ratingValues = {
      'very_helpful': 5,
      'helpful': 4,
      'neutral': 3,
      'not_helpful': 2,
      'very_unhelpful': 1
    };
    return ratingValues[rating];
  };

  const getRatingColor = (rating: FeedbackRating): string => {
    const value = getRatingValue(rating);
    if (value >= 4) return '#4caf50';
    if (value === 3) return '#ff9800';
    return '#f44336';
  };

  return (
    <div className={`feedback-button ${className}`} style={{ marginTop: '8px' }}>
      {/* Status Messages */}
      {submitStatus === 'success' && (
        <div style={{
          backgroundColor: '#e8f5e8',
          color: '#2e7d32',
          padding: '8px 12px',
          borderRadius: '4px',
          fontSize: '0.9em',
          marginBottom: '8px',
          border: '1px solid #4caf50'
        }}>
          ✓ Thank you for your feedback!
        </div>
      )}

      {submitStatus === 'error' && (
        <div style={{
          backgroundColor: '#ffebee',
          color: '#c62828',
          padding: '8px 12px',
          borderRadius: '4px',
          fontSize: '0.9em',
          marginBottom: '8px',
          border: '1px solid #f44336'
        }}>
          ✗ Error submitting feedback. Please try again.
        </div>
      )}

      {/* Quick Feedback Buttons */}
      {!showForm && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.9em', color: '#666' }}>Was this helpful?</span>
          
          <button
            onClick={() => handleQuickFeedback(true)}
            disabled={isSubmitting}
            style={{
              padding: '4px 12px',
              backgroundColor: '#4caf50',
              color: 'white',
              border: 'none',
              borderRadius: '16px',
              fontSize: '0.8em',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              opacity: isSubmitting ? 0.6 : 1,
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            👍 Helpful
          </button>

          <button
            onClick={() => handleQuickFeedback(false)}
            disabled={isSubmitting}
            style={{
              padding: '4px 12px',
              backgroundColor: '#f44336',
              color: 'white',
              border: 'none',
              borderRadius: '16px',
              fontSize: '0.8em',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              opacity: isSubmitting ? 0.6 : 1,
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            👎 Not Helpful
          </button>

          <button
            onClick={toggleForm}
            style={{
              padding: '4px 8px',
              backgroundColor: 'transparent',
              color: '#1976d2',
              border: '1px solid #1976d2',
              borderRadius: '16px',
              fontSize: '0.8em',
              cursor: 'pointer'
            }}
          >
            📝 Detailed feedback
          </button>
        </div>
      )}

      {/* Detailed Feedback Form */}
      {showForm && (
        <div style={{
          backgroundColor: '#f8f9fa',
          border: '1px solid #e9ecef',
          borderRadius: '8px',
          padding: '16px',
          marginTop: '8px'
        }}>
          <h4 style={{ margin: '0 0 12px 0', fontSize: '1em' }}>Provide Detailed Feedback</h4>
          
          {/* Helpfulness Selection */}
          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'block', marginBottom: '4px', fontSize: '0.9em', fontWeight: 'bold' }}>
              Was this helpful?
            </label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.9em' }}>
                <input
                  type="radio"
                  name="helpful"
                  checked={formData.isHelpful}
                  onChange={() => setFormData({ ...formData, isHelpful: true })}
                />
                Yes
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.9em' }}>
                <input
                  type="radio"
                  name="helpful"
                  checked={!formData.isHelpful}
                  onChange={() => setFormData({ ...formData, isHelpful: false })}
                />
                No
              </label>
            </div>
          </div>

          {/* Rating Selection */}
          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'block', marginBottom: '4px', fontSize: '0.9em', fontWeight: 'bold' }}>
              Rating:
            </label>
            <select
              value={formData.rating}
              onChange={(e) => setFormData({ ...formData, rating: e.target.value as FeedbackRating })}
              style={{
                padding: '6px 8px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                fontSize: '0.9em',
                backgroundColor: 'white'
              }}
            >
              <option value="very_helpful">⭐⭐⭐⭐⭐ Very Helpful</option>
              <option value="helpful">⭐⭐⭐⭐ Helpful</option>
              <option value="neutral">⭐⭐⭐ Neutral</option>
              <option value="not_helpful">⭐⭐ Not Helpful</option>
              <option value="very_unhelpful">⭐ Very Unhelpful</option>
            </select>
          </div>

          {/* Comment */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '4px', fontSize: '0.9em', fontWeight: 'bold' }}>
              Comments (optional):
            </label>
            <textarea
              value={formData.comment}
              onChange={(e) => setFormData({ ...formData, comment: e.target.value })}
              placeholder="Tell us more about your experience with this finding/suggestion..."
              rows={3}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                fontSize: '0.9em',
                resize: 'vertical',
                fontFamily: 'inherit'
              }}
            />
          </div>

          {/* Form Buttons */}
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <button
              onClick={toggleForm}
              disabled={isSubmitting}
              style={{
                padding: '6px 12px',
                backgroundColor: '#666',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                fontSize: '0.9em',
                cursor: isSubmitting ? 'not-allowed' : 'pointer',
                opacity: isSubmitting ? 0.6 : 1
              }}
            >
              Cancel
            </button>
            <button
              onClick={() => handleSubmitFeedback(formData.isHelpful)}
              disabled={isSubmitting}
              style={{
                padding: '6px 12px',
                backgroundColor: getRatingColor(formData.rating),
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                fontSize: '0.9em',
                cursor: isSubmitting ? 'not-allowed' : 'pointer',
                opacity: isSubmitting ? 0.6 : 1
              }}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FeedbackButton; 