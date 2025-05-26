#!/usr/bin/env python3
"""
Quick test script cho AI Code Reviewer.
"""

import webbrowser
import requests
import time


def main():
    print("🚀 Quick Test - AI Code Reviewer")
    print("=" * 40)
    
    # Test backend
    try:
        resp = requests.get("http://localhost:8000/health", timeout=3)
        if resp.status_code == 200:
            print("✅ Backend OK (port 8000)")
        else:
            print("❌ Backend Error")
    except:
        print("❌ Backend Not Running")
    
    # Test frontend ports
    frontend_port = None
    for port in [3001, 3000]:
        try:
            resp = requests.get(f"http://localhost:{port}/", timeout=2)
            if resp.status_code == 200:
                print(f"✅ Frontend OK (port {port})")
                frontend_port = port
                break
        except:
            continue
    
    if not frontend_port:
        print("❌ Frontend Not Running")
        return
    
    # Test pages
    pages = [
        ("Test Page", f"http://localhost:{frontend_port}/test"),
        ("Main App", f"http://localhost:{frontend_port}/"),
        ("Scans", f"http://localhost:{frontend_port}/scans"),
    ]
    
    print(f"\n🌐 Opening Browser - Port {frontend_port}")
    for name, url in pages:
        print(f"   {name}: {url}")
    
    # Open test page
    webbrowser.open(f"http://localhost:{frontend_port}/test")
    
    print("\n📋 Manual Check:")
    print("1. Trang /test có hiển thị 'Test Page - If you see this, React is working!'?")
    print("2. Nhấn F12 và kiểm tra Console có error không?")
    print("3. Thử các URL khác:")
    for name, url in pages:
        print(f"   - {url}")


if __name__ == "__main__":
    main() 