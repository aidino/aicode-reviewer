#!/usr/bin/env python3
"""
Test script để kiểm tra flat design mới của frontend.
Kiểm tra các CSS files và components đã được cập nhật.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(file_path: str) -> bool:
    """Kiểm tra file có tồn tại không."""
    return Path(file_path).exists()

def check_css_variables(file_path: str) -> bool:
    """Kiểm tra CSS variables có được định nghĩa không."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Kiểm tra các CSS variables quan trọng
        required_vars = [
            '--color-primary',
            '--color-secondary', 
            '--color-background',
            '--color-surface',
            '--color-text-primary',
            '--spacing-md',
            '--radius-md',
            '--font-size-base'
        ]
        
        for var in required_vars:
            if var not in content:
                print(f"❌ Missing CSS variable: {var}")
                return False
                
        print(f"✅ All CSS variables found in {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def check_component_classes(file_path: str, expected_classes: list) -> bool:
    """Kiểm tra component có sử dụng CSS classes mới không."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        found_classes = []
        for css_class in expected_classes:
            if css_class in content:
                found_classes.append(css_class)
                
        if len(found_classes) >= len(expected_classes) * 0.7:  # 70% classes found
            print(f"✅ Component {file_path} uses flat design classes: {found_classes}")
            return True
        else:
            print(f"❌ Component {file_path} missing classes: {set(expected_classes) - set(found_classes)}")
            return False
            
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def run_frontend_build_test():
    """Chạy build test cho frontend."""
    frontend_dir = "src/webapp/frontend"
    
    if not os.path.exists(frontend_dir):
        print(f"❌ Frontend directory not found: {frontend_dir}")
        return False
        
    try:
        # Change to frontend directory
        os.chdir(frontend_dir)
        
        # Run npm install if node_modules doesn't exist
        if not os.path.exists("node_modules"):
            print("📦 Installing npm dependencies...")
            result = subprocess.run(["npm", "install"], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ npm install failed: {result.stderr}")
                return False
                
        # Run build test
        print("🔨 Testing frontend build...")
        result = subprocess.run(["npm", "run", "build"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Frontend build successful")
            return True
        else:
            print(f"❌ Frontend build failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running build test: {e}")
        return False
    finally:
        # Return to original directory
        os.chdir("../../..")

def main():
    """Main test function."""
    print("🎨 Testing Flat Design Implementation")
    print("=" * 50)
    
    # Test 1: Check CSS files exist
    print("\n📁 Checking CSS files...")
    css_files = [
        "src/webapp/frontend/src/styles/globals.css",
        "src/webapp/frontend/src/styles/Dashboard.css", 
        "src/webapp/frontend/src/styles/components.css"
    ]
    
    css_files_ok = True
    for css_file in css_files:
        if check_file_exists(css_file):
            print(f"✅ Found: {css_file}")
        else:
            print(f"❌ Missing: {css_file}")
            css_files_ok = False
            
    # Test 2: Check CSS variables
    print("\n🎨 Checking CSS variables...")
    if css_files_ok:
        globals_css_ok = check_css_variables("src/webapp/frontend/src/styles/globals.css")
    else:
        globals_css_ok = False
        
    # Test 3: Check component updates
    print("\n⚛️ Checking component updates...")
    components_to_check = [
        {
            "file": "src/webapp/frontend/src/pages/ScanList.tsx",
            "classes": ["scan-list-container", "btn", "badge", "card"]
        },
        {
            "file": "src/webapp/frontend/src/pages/ReportView.tsx", 
            "classes": ["report-container", "btn", "badge", "card"]
        },
        {
            "file": "src/webapp/frontend/src/pages/CreateScan.tsx",
            "classes": ["create-scan-container", "btn", "card", "text-center"]
        },
        {
            "file": "src/webapp/frontend/src/pages/Dashboard.tsx",
            "classes": ["dashboard-container", "btn", "card", "metric-card"]
        }
    ]
    
    components_ok = True
    for component in components_to_check:
        if check_file_exists(component["file"]):
            if not check_component_classes(component["file"], component["classes"]):
                components_ok = False
        else:
            print(f"❌ Component not found: {component['file']}")
            components_ok = False
            
    # Test 4: Frontend build test
    print("\n🔨 Testing frontend build...")
    build_ok = run_frontend_build_test()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"CSS Files: {'✅ PASS' if css_files_ok else '❌ FAIL'}")
    print(f"CSS Variables: {'✅ PASS' if globals_css_ok else '❌ FAIL'}")
    print(f"Component Updates: {'✅ PASS' if components_ok else '❌ FAIL'}")
    print(f"Frontend Build: {'✅ PASS' if build_ok else '❌ FAIL'}")
    
    all_tests_pass = css_files_ok and globals_css_ok and components_ok and build_ok
    
    if all_tests_pass:
        print("\n🎉 All tests passed! Flat design implementation successful.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 