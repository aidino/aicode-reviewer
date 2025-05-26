/**
 * Simple test page for debugging white screen issues.
 */

import React from 'react';

const TestPage: React.FC = () => {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Test Page - If you see this, React is working!</h1>
      <div style={{ marginTop: '20px' }}>
        <p>✅ React is loaded and working</p>
        <p>✅ TypeScript compilation successful</p>
        <p>✅ Vite dev server running</p>
        <p>Current time: {new Date().toLocaleString()}</p>
      </div>
      
      <div style={{ marginTop: '30px', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
        <h2>Debug Information</h2>
        <p><strong>User Agent:</strong> {navigator.userAgent}</p>
        <p><strong>URL:</strong> {window.location.href}</p>
        <p><strong>Viewport:</strong> {window.innerWidth} x {window.innerHeight}</p>
      </div>
      
      <div style={{ marginTop: '20px' }}>
        <button 
          onClick={() => alert('Button clicked! JavaScript is working.')}
          style={{
            padding: '10px 20px',
            backgroundColor: '#1976d2',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Test JavaScript
        </button>
      </div>
    </div>
  );
};

export default TestPage; 