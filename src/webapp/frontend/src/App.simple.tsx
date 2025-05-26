/**
 * Simplified App component for debugging white screen issues.
 */

import React from 'react';

const SimpleApp: React.FC = () => {
  console.log('SimpleApp rendering...');
  
  return (
    <div style={{ padding: '20px' }}>
      <h1>Simple App Test</h1>
      <p>If you see this, React is working!</p>
      <div>
        <button onClick={() => console.log('Button clicked!')}>
          Test Console Log
        </button>
      </div>
    </div>
  );
};

export default SimpleApp; 