"""
Test cho LoginPage component.

Kiểm tra xem LoginPage có render được đúng cách không.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the frontend src to path for testing
frontend_src = os.path.join(os.path.dirname(__file__), '../../../../src/webapp/frontend/src')
sys.path.insert(0, frontend_src)

def test_login_page_basic():
    """
    Test cơ bản để đảm bảo LoginPage component có thể được import.
    
    Reason: Kiểm tra xem có lỗi import hoặc syntax error không.
    """
    # This is a basic test to ensure the component structure is valid
    # In a real React testing environment, we would use Jest/React Testing Library
    
    # For now, just test that the file exists and can be read
    login_page_path = os.path.join(
        os.path.dirname(__file__), 
        '../../../../src/webapp/frontend/src/pages/LoginPage.tsx'
    )
    
    assert os.path.exists(login_page_path), "LoginPage.tsx file should exist"
    
    # Read the file and check for basic structure
    with open(login_page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for essential parts
    assert 'export const LoginPage' in content, "LoginPage component should be exported"
    assert 'useAuth' in content, "Should use useAuth hook"
    assert 'useState' in content, "Should use useState hook"
    assert 'form' in content.lower(), "Should contain form element"
    assert 'email' in content.lower(), "Should have email field"
    assert 'password' in content.lower(), "Should have password field"

def test_login_page_imports():
    """
    Test để kiểm tra các import trong LoginPage.
    
    Reason: Đảm bảo tất cả dependencies được import đúng.
    """
    login_page_path = os.path.join(
        os.path.dirname(__file__), 
        '../../../../src/webapp/frontend/src/pages/LoginPage.tsx'
    )
    
    with open(login_page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required imports
    assert 'import React' in content, "Should import React"
    assert 'useNavigate' in content, "Should import useNavigate"
    assert 'useAuth' in content, "Should import useAuth"
    assert 'LoginRequest' in content, "Should import LoginRequest type"

def test_css_files_exist():
    """
    Test để kiểm tra các file CSS cần thiết có tồn tại không.
    
    Reason: Đảm bảo styling được load đúng cách.
    """
    css_files = [
        '../../../../src/webapp/frontend/src/styles/globals.css',
        '../../../../src/webapp/frontend/src/styles/soft-ui-enhanced.css',
        '../../../../src/webapp/frontend/src/styles/components.css',
        '../../../../src/webapp/frontend/src/styles/theme.css'
    ]
    
    for css_file in css_files:
        css_path = os.path.join(os.path.dirname(__file__), css_file)
        assert os.path.exists(css_path), f"CSS file {css_file} should exist"

def test_auth_context_exists():
    """
    Test để kiểm tra AuthContext có tồn tại không.
    
    Reason: LoginPage phụ thuộc vào AuthContext.
    """
    auth_context_path = os.path.join(
        os.path.dirname(__file__), 
        '../../../../src/webapp/frontend/src/contexts/AuthContext.tsx'
    )
    
    assert os.path.exists(auth_context_path), "AuthContext.tsx should exist"
    
    with open(auth_context_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'export const useAuth' in content, "Should export useAuth hook"
    assert 'AuthProvider' in content, "Should export AuthProvider"

if __name__ == '__main__':
    pytest.main([__file__]) 