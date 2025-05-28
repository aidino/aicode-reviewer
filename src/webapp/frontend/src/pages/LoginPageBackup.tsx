import React from 'react';

/**
 * Backup LoginPage - cực kỳ đơn giản không có dependencies
 * Sử dụng khi LoginPage chính bị lỗi
 */
export const LoginPageBackup: React.FC = () => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert('Backup login form submitted!');
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f8fafc',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '40px',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        width: '100%',
        maxWidth: '400px'
      }}>
        <h1 style={{ 
          textAlign: 'center', 
          marginBottom: '30px', 
          color: '#1e293b',
          fontSize: '28px'
        }}>
          🔐 Login (Backup)
        </h1>
        
        <p style={{ 
          textAlign: 'center', 
          color: '#64748b', 
          marginBottom: '30px',
          fontSize: '14px'
        }}>
          Đây là trang login backup. Nếu bạn thấy trang này,<br/>
          có nghĩa là React đang hoạt động!
        </p>
        
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '8px', 
              fontWeight: '600',
              color: '#374151'
            }}>
              Email:
            </label>
            <input
              type="email"
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #e5e7eb',
                borderRadius: '6px',
                fontSize: '16px',
                boxSizing: 'border-box'
              }}
              placeholder="your@email.com"
              required
            />
          </div>
          
          <div style={{ marginBottom: '25px' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '8px', 
              fontWeight: '600',
              color: '#374151'
            }}>
              Password:
            </label>
            <input
              type="password"
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #e5e7eb',
                borderRadius: '6px',
                fontSize: '16px',
                boxSizing: 'border-box'
              }}
              placeholder="your password"
              required
            />
          </div>
          
          <button
            type="submit"
            style={{
              width: '100%',
              backgroundColor: '#3b82f6',
              color: 'white',
              padding: '12px',
              border: 'none',
              borderRadius: '6px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              marginBottom: '20px'
            }}
          >
            Login
          </button>
        </form>
        
        <div style={{ 
          textAlign: 'center', 
          fontSize: '14px', 
          color: '#6b7280',
          borderTop: '1px solid #e5e7eb',
          paddingTop: '20px'
        }}>
          <p>✅ React rendering OK</p>
          <p>✅ Form elements working</p>
          <p>✅ No external dependencies</p>
          <p>
            <a href="/" style={{ color: '#3b82f6', textDecoration: 'none' }}>
              ← Go to Home
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}; 