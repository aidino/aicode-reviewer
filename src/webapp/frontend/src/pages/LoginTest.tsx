/**
 * LoginTest component đơn giản để debug vấn đề login screen trắng
 */

import React from 'react';

export const LoginTest: React.FC = () => {
  console.log('LoginTest component rendering...');
  
  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f3f4f6',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        width: '100%',
        maxWidth: '400px'
      }}>
        <h1 style={{
          fontSize: '2rem',
          fontWeight: 'bold',
          marginBottom: '1rem',
          textAlign: 'center',
          color: '#1f2937'
        }}>
          🧪 Login Test Page
        </h1>
        
        <p style={{
          color: '#6b7280',
          textAlign: 'center',
          marginBottom: '2rem'
        }}>
          Nếu bạn thấy page này, nghĩa là React và routing đang hoạt động.
        </p>
        
        <div style={{
          padding: '1rem',
          backgroundColor: '#f0fdf4',
          border: '1px solid #bbf7d0',
          borderRadius: '8px',
          marginBottom: '1rem'
        }}>
          <h3 style={{ color: '#166534', marginBottom: '0.5rem' }}>✅ Working Components:</h3>
          <ul style={{ color: '#166534', paddingLeft: '1.5rem' }}>
            <li>React rendering</li>
            <li>Component mounting</li>
            <li>CSS styling (inline)</li>
            <li>JavaScript execution</li>
          </ul>
        </div>
        
        <form style={{ marginBottom: '1rem' }}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              color: '#374151',
              fontWeight: '600'
            }}>
              Email Test:
            </label>
            <input
              type="email"
              placeholder="test@example.com"
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '1rem'
              }}
            />
          </div>
          
          <div style={{ marginBottom: '1rem' }}>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              color: '#374151',
              fontWeight: '600'
            }}>
              Password Test:
            </label>
            <input
              type="password"
              placeholder="TestPassword123!"
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '1rem'
              }}
            />
          </div>
          
          <button
            type="button"
            onClick={() => alert('Test button clicked! React events working.')}
            style={{
              width: '100%',
              padding: '0.75rem',
              backgroundColor: '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '1rem',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Test Button
          </button>
        </form>
        
        <div style={{
          padding: '1rem',
          backgroundColor: '#eff6ff',
          border: '1px solid #93c5fd',
          borderRadius: '8px'
        }}>
          <h3 style={{ color: '#1e40af', marginBottom: '0.5rem' }}>🔍 Next Steps:</h3>
          <ul style={{ color: '#1e40af', paddingLeft: '1.5rem', fontSize: '0.875rem' }}>
            <li>Nếu page này hiển thị → React OK</li>
            <li>Nếu button click → Events OK</li>
            <li>Kiểm tra browser console F12</li>
            <li>Kiểm tra Network tab</li>
            <li>Test with real LoginPage</li>
          </ul>
        </div>
      </div>
    </div>
  );
}; 