#!/usr/bin/env python3
"""
Frontend debugging script for AI Code Reviewer.

This script helps debug frontend issues by:
1. Checking if backend is running
2. Checking if frontend is accessible
3. Testing different routes
4. Providing debugging instructions
"""

import requests
import webbrowser
import time
import sys
from pathlib import Path


def test_backend():
    """Test if backend is running."""
    print("🔍 Testing backend...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy")
            return True
        else:
            print(f"❌ Backend responding with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend not accessible on port 8000")
        return False
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False


def test_frontend():
    """Test if frontend is running."""
    print("\n🔍 Testing frontend...")
    
    # Try both ports (3000 and 3001) as Vite might use different port
    ports_to_try = [3000, 3001]
    
    for port in ports_to_try:
        try:
            print(f"   Trying port {port}...")
            response = requests.get(f"http://localhost:{port}/", timeout=3)
            if response.status_code == 200:
                print(f"✅ Frontend is running on port {port}")
                print(f"   Response size: {len(response.text)} bytes")
                
                # Check for critical elements
                html = response.text
                if 'id="root"' in html:
                    print("✅ Root element found in HTML")
                else:
                    print("❌ Root element missing from HTML")
                
                if 'index.tsx' in html:
                    print("✅ React entry point found")
                else:
                    print("❌ React entry point missing")
                
                # Test specific routes
                test_urls = [
                    ("Test Page", f"http://localhost:{port}/test"),
                    ("Scans Page", f"http://localhost:{port}/scans"),
                ]
                
                for name, url in test_urls:
                    try:
                        resp = requests.get(url, timeout=3)
                        if resp.status_code == 200:
                            print(f"✅ {name} accessible")
                        else:
                            print(f"❌ {name} returned {resp.status_code}")
                    except:
                        print(f"❌ {name} not accessible")
                
                return port  # Return the working port
            else:
                print(f"❌ Frontend on port {port} responding with status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Frontend not accessible on port {port}")
        except Exception as e:
            print(f"❌ Frontend test error on port {port}: {e}")
    
    print("❌ Frontend not accessible on any port")
    return False


def open_debug_browser(port=3001):
    """Open browser with debug tools."""
    print(f"\n🌐 Opening browser for debugging on port {port}...")
    
    urls_to_test = [
        ("Test Page", f"http://localhost:{port}/test"),
        ("Main App", f"http://localhost:{port}/"),
        ("Scans Page", f"http://localhost:{port}/scans"),
    ]
    
    for name, url in urls_to_test:
        print(f"   {name}: {url}")
    
    # Open the test page first
    webbrowser.open(f"http://localhost:{port}/test")
    
    print("\n🔧 Debugging Instructions:")
    print("1. Open browser Developer Tools (F12)")
    print("2. Go to Console tab")
    print("3. Look for any error messages")
    print("4. Check Network tab for failed requests")
    print("5. Try these URLs manually:")
    for name, url in urls_to_test:
        print(f"   - {name}: {url}")


def show_debugging_tips():
    """Show common debugging tips."""
    print("\n💡 Common Issues and Solutions:")
    print()
    print("1. White Screen - JavaScript Error:")
    print("   - Check browser console for errors")
    print("   - Look for React import/export issues")
    print("   - Check if all dependencies are installed")
    print()
    print("2. API Connection Issues:")
    print("   - Verify backend is running on port 8000")
    print("   - Check CORS configuration")
    print("   - Test API endpoints directly with curl")
    print()
    print("3. Routing Issues:")
    print("   - Try accessing different routes directly")
    print("   - Check React Router configuration")
    print("   - Look for 404 errors in Network tab")
    print()
    print("4. Module Loading Issues:")
    print("   - Clear npm cache: npm cache clean --force")
    print("   - Reinstall dependencies: rm -rf node_modules && npm install")
    print("   - Check for TypeScript errors")


def main():
    """Main debugging function."""
    print("🐛 AI Code Reviewer Frontend Debugging")
    print("=" * 50)
    
    backend_ok = test_backend()
    frontend_port = test_frontend()
    
    if not backend_ok:
        print("\n⚠️  Backend is not running. Start it with:")
        print("   python -m uvicorn src.webapp.backend.api.main:app --reload --port 8000")
    
    if not frontend_port:
        print("\n⚠️  Frontend is not running. Start it with:")
        print("   cd src/webapp/frontend && npm run dev")
    
    if frontend_port:
        print(f"\n🚀 Frontend is accessible on port {frontend_port}. Opening browser for debugging...")
        time.sleep(1)
        open_debug_browser(frontend_port)
    
    show_debugging_tips()
    
    print("\n📝 Debug Checklist:")
    print("□ Check browser console for JavaScript errors")
    print("□ Check Network tab for failed API requests")
    print(f"□ Try test page: http://localhost:{frontend_port or 3001}/test")
    print("□ Verify React components are loading")
    print("□ Check if routes are working correctly")
    
    return 0 if (backend_ok and frontend_port) else 1


if __name__ == "__main__":
    sys.exit(main()) 