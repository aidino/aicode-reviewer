#!/usr/bin/env python3
"""
Script để kiểm tra logs và trạng thái của frontend và backend.
"""

import subprocess
import requests
import json
import time


def check_backend_status():
    """Kiểm tra trạng thái chi tiết của backend."""
    print("🔍 Checking backend status...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Backend healthy:")
            print(f"   Service: {health_data.get('service', 'Unknown')}")
            print(f"   Version: {health_data.get('version', 'Unknown')}")
            print(f"   Components: {health_data.get('components', {})}")
        
        # Test API docs
        docs_response = requests.get("http://localhost:8000/docs", timeout=5)
        if docs_response.status_code == 200:
            print("✅ API docs accessible at http://localhost:8000/docs")
        
        # Test sample endpoint
        demo_response = requests.get("http://localhost:8000/scans/demo_scan_1/report", timeout=5)
        if demo_response.status_code == 200:
            print("✅ Demo scan endpoint working")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return False


def check_frontend_status():
    """Kiểm tra trạng thái frontend."""
    print("\n🔍 Checking frontend status...")
    
    try:
        # Test main page
        response = requests.get("http://localhost:3000/", timeout=5)
        if response.status_code == 200:
            html = response.text
            print("✅ Frontend server responding")
            print(f"   HTML size: {len(html)} bytes")
            
            # Check for critical elements
            if 'id="root"' in html:
                print("✅ Root element found")
            else:
                print("❌ Root element missing")
            
            if 'index.tsx' in html:
                print("✅ React entry point found")
            else:
                print("❌ React entry point missing")
            
            if '@vite/client' in html:
                print("✅ Vite client scripts found")
            else:
                print("❌ Vite client scripts missing")
        
        # Test specific routes
        test_urls = [
            ("Test Page", "http://localhost:3000/test"),
            ("Scans Page", "http://localhost:3000/scans"),
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
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        return False


def check_processes():
    """Kiểm tra processes đang chạy."""
    print("\n🔍 Checking running processes...")
    
    try:
        # Check port 8000 (backend)
        result = subprocess.run(['lsof', '-ti:8000'], capture_output=True, text=True)
        if result.stdout.strip():
            print("✅ Process running on port 8000 (backend)")
        else:
            print("❌ No process on port 8000")
        
        # Check port 3000 (frontend)
        result = subprocess.run(['lsof', '-ti:3000'], capture_output=True, text=True)
        if result.stdout.strip():
            print("✅ Process running on port 3000 (frontend)")
        else:
            print("❌ No process on port 3000")
            
    except Exception as e:
        print(f"❌ Error checking processes: {e}")


def show_next_steps():
    """Hiển thị next steps cho debugging."""
    print("\n🔧 Next Steps for Debugging:")
    print("1. Open browser to: http://localhost:3000/test")
    print("2. Open Developer Tools (F12)")
    print("3. Check Console tab for JavaScript errors")
    print("4. Check Network tab for failed requests")
    print("5. If you see errors, copy them and share for help")
    print("\n📱 Manual Tests:")
    print("- http://localhost:3000/test (Simple test page)")
    print("- http://localhost:3000/ (Main application)")
    print("- http://localhost:3000/scans (Scans list)")
    print("- http://localhost:8000/docs (Backend API docs)")


def main():
    """Main function."""
    print("🔧 AI Code Reviewer - Status Check")
    print("=" * 50)
    
    backend_ok = check_backend_status()
    frontend_ok = check_frontend_status()
    check_processes()
    
    print(f"\n📊 Summary:")
    print(f"Backend: {'✅ OK' if backend_ok else '❌ ERROR'}")
    print(f"Frontend: {'✅ OK' if frontend_ok else '❌ ERROR'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 Both services are running! The issue might be in browser.")
        print("Check browser console for JavaScript errors.")
    else:
        print("\n⚠️ Some services have issues. Check the logs above.")
    
    show_next_steps()


if __name__ == "__main__":
    main() 