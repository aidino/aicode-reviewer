#!/usr/bin/env python3
"""
Test script để kiểm tra full setup của AI Code Reviewer.

Script này kiểm tra:
1. Backend API có hoạt động không
2. Frontend development server có hoạt động không (nếu có)
3. Các endpoint chính có phản hồi đúng không
4. Connectivity giữa frontend và backend
"""

import requests
import time
import json
import sys
from typing import Dict, Any


def test_backend_health() -> bool:
    """Test backend health endpoint."""
    try:
        print("🔍 Testing backend health...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend health: {data['status']}")
            print(f"   Service: {data['service']}")
            print(f"   Version: {data['version']}")
            return True
        else:
            print(f"❌ Backend health check failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend not accessible. Make sure server is running on port 8000")
        print("   Start with: python -m uvicorn src.webapp.backend.api.main:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False


def test_backend_api() -> bool:
    """Test backend API endpoints."""
    try:
        print("\n🔍 Testing backend API endpoints...")
        
        # Test root endpoint
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: HTTP {response.status_code}")
            return False
        
        # Test demo scan report
        response = requests.get("http://localhost:8000/scans/demo_scan_1/report", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Demo scan report working")
            print(f"   Scan ID: {data['scan_info']['scan_id']}")
            print(f"   Repository: {data['scan_info']['repository']}")
            print(f"   Total findings: {data['summary']['total_findings']}")
        else:
            print(f"❌ Demo scan report failed: HTTP {response.status_code}")
            return False
        
        # Test API info endpoint
        response = requests.get("http://localhost:8000/api/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API info endpoint working")
            print(f"   Supported languages: {', '.join(data['supported_languages'])}")
            print(f"   Scan types: {', '.join(data['scan_types'])}")
        else:
            print(f"❌ API info endpoint failed: HTTP {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Backend API test error: {e}")
        return False


def test_frontend() -> bool:
    """Test frontend server."""
    try:
        print("\n🔍 Testing frontend server...")
        response = requests.get("http://localhost:5173/", timeout=5)
        
        if response.status_code == 200:
            content = response.text
            if "AI Code Reviewer" in content or "React" in content or "Vite" in content:
                print("✅ Frontend server working")
                print(f"   Response size: {len(content)} bytes")
                return True
            else:
                print("⚠️  Frontend server responding but content looks unexpected")
                return False
        else:
            print(f"❌ Frontend server failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Frontend not accessible. Start with: cd src/webapp/frontend && npm run dev")
        return False
    except Exception as e:
        print(f"❌ Frontend test error: {e}")
        return False


def test_api_docs() -> bool:
    """Test API documentation endpoints."""
    try:
        print("\n🔍 Testing API documentation...")
        
        # Test Swagger docs
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Swagger UI accessible at http://localhost:8000/docs")
        else:
            print(f"❌ Swagger UI failed: HTTP {response.status_code}")
            return False
        
        # Test ReDoc
        response = requests.get("http://localhost:8000/redoc", timeout=5)
        if response.status_code == 200:
            print("✅ ReDoc UI accessible at http://localhost:8000/redoc")
        else:
            print(f"❌ ReDoc UI failed: HTTP {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ API docs test error: {e}")
        return False


def main():
    """Main test runner."""
    print("🚀 AI Code Reviewer Setup Test")
    print("=" * 50)
    
    results = {
        "backend_health": test_backend_health(),
        "backend_api": False,
        "frontend": False,
        "api_docs": False
    }
    
    if results["backend_health"]:
        results["backend_api"] = test_backend_api()
        results["api_docs"] = test_api_docs()
    
    results["frontend"] = test_frontend()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:15} | {status}")
    
    print(f"\nResults: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Your setup is working correctly.")
        print("\n🔗 Access Points:")
        print("   Web App:  http://localhost:5173")
        print("   API:      http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Check the error messages above.")
        print("\n💡 Quick Setup Commands:")
        print("   Backend:  python -m uvicorn src.webapp.backend.api.main:app --reload --port 8000")
        print("   Frontend: cd src/webapp/frontend && npm run dev")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 