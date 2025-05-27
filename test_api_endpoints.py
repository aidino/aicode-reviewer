#!/usr/bin/env python3
"""
Test script để kiểm tra API endpoints hoạt động đúng.
"""

import requests
import json

def test_api_endpoints():
    """Test các API endpoints chính."""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing API Endpoints")
    print("=" * 50)
    
    # Test 1: Root endpoint
    print("\n📡 Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 2: Health endpoint  
    print("\n🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test 3: Scans list endpoint
    print("\n📋 Testing scans list endpoint...")
    try:
        response = requests.get(f"{base_url}/api/scans/")
        if response.status_code == 200:
            print("✅ Scans list endpoint working")
            data = response.json()
            print(f"   Found {len(data)} scans")
            if data:
                print(f"   First scan: {data[0]['scan_id']}")
        else:
            print(f"❌ Scans list endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Scans list endpoint error: {e}")
    
    # Test 4: Demo scan report
    print("\n📊 Testing demo scan report...")
    try:
        response = requests.get(f"{base_url}/api/scans/demo_scan_1/report")
        if response.status_code == 200:
            print("✅ Demo scan report working")
            data = response.json()
            print(f"   Scan: {data['scan_info']['scan_id']}")
            print(f"   Findings: {data['summary']['total_findings']}")
        else:
            print(f"❌ Demo scan report failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Demo scan report error: {e}")
    
    # Test 5: API info
    print("\n📋 Testing API info...")
    try:
        response = requests.get(f"{base_url}/api/info")
        if response.status_code == 200:
            print("✅ API info working")
            data = response.json()
            print(f"   API: {data['name']} v{data['version']}")
        else:
            print(f"❌ API info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API info error: {e}")

if __name__ == "__main__":
    test_api_endpoints() 