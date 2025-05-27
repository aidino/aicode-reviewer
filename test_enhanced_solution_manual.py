#!/usr/bin/env python3
"""
Manual Test Script for Enhanced Solution Suggestion Agent via Web API.

This script tests the enhanced solution suggestion capabilities through the web interface,
demonstrating XAI features, multiple alternatives, and comprehensive error handling.
"""

import requests
import json
import sys
import time
from typing import Dict, Any
import webbrowser
from urllib.parse import urljoin


class EnhancedSolutionTester:
    """Test the Enhanced Solution Suggestion Agent via web API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def check_backend_health(self) -> bool:
        """Check if backend is running and healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Backend Health: {health_data.get('status')}")
                return True
            else:
                print(f"❌ Backend unhealthy: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend connection failed: {str(e)}")
            return False
    
    def create_enhanced_scan_request(self) -> Dict[str, Any]:
        """Create a scan request specifically for testing enhanced solution suggestions."""
        return {
            "scan_id": "enhanced_test_scan",
            "repo_url": "https://github.com/test/enhanced-solution-demo",
            "scan_type": "pr",
            "pr_id": 123,
            "settings": {
                "enable_enhanced_solutions": True,
                "max_alternatives": 3,
                "confidence_threshold": 0.7,
                "suggestion_types": [
                    "security_fix",
                    "performance_optimization", 
                    "best_practice",
                    "bug_fix",
                    "testing"
                ]
            }
        }
    
    def test_scan_initiation(self) -> str:
        """Test scan initiation with enhanced solution settings."""
        print("\n🚀 Testing Enhanced Solution Scan Initiation")
        print("=" * 60)
        
        scan_request = self.create_enhanced_scan_request()
        
        try:
            response = self.session.post(
                f"{self.base_url}/scans/initiate",
                json=scan_request,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                job_id = result.get("job_id")
                print(f"✅ Scan initiated successfully!")
                print(f"📋 Job ID: {job_id}")
                print(f"🎯 Enhanced features enabled: {scan_request['settings']['enable_enhanced_solutions']}")
                return job_id
            else:
                print(f"❌ Scan initiation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Scan initiation error: {str(e)}")
            return None
    
    def monitor_scan_progress(self, job_id: str) -> bool:
        """Monitor scan progress until completion."""
        print(f"\n⏳ Monitoring Scan Progress: {job_id}")
        print("=" * 50)
        
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = self.session.get(
                    f"{self.base_url}/scans/jobs/{job_id}/status",
                    timeout=5
                )
                
                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data.get("status")
                    progress = status_data.get("progress", 0)
                    
                    print(f"📊 Attempt {attempt + 1}: Status = {status}, Progress = {progress}%")
                    
                    if status == "completed":
                        print("✅ Scan completed successfully!")
                        return True
                    elif status == "failed":
                        print("❌ Scan failed!")
                        return False
                    
                    time.sleep(2)  # Wait 2 seconds before next check
                else:
                    print(f"❌ Status check failed: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Status check error: {str(e)}")
                return False
        
        print("⏰ Scan monitoring timeout!")
        return False
    
    def get_enhanced_scan_report(self, scan_id: str = None) -> Dict[str, Any]:
        """Get scan report with enhanced solution suggestions."""
        scan_id = scan_id or "demo_scan_1"  # Use demo scan if no specific scan
        
        print(f"\n📊 Retrieving Enhanced Solution Report: {scan_id}")
        print("=" * 60)
        
        try:
            response = self.session.get(
                f"{self.base_url}/scans/{scan_id}/report",
                timeout=10
            )
            
            if response.status_code == 200:
                report_data = response.json()
                print("✅ Report retrieved successfully!")
                return report_data
            else:
                print(f"❌ Report retrieval failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Report retrieval error: {str(e)}")
            return None
    
    def analyze_enhanced_solutions(self, report_data: Dict[str, Any]):
        """Analyze and display enhanced solution suggestions from report."""
        print("\n🧠 ENHANCED SOLUTION ANALYSIS")
        print("=" * 50)
        
        # Look for enhanced solution suggestions in the report
        findings = report_data.get("findings", [])
        enhanced_solutions_found = 0
        
        for finding in findings:
            solution = finding.get("solution_suggestion")
            if solution and self.is_enhanced_solution(solution):
                enhanced_solutions_found += 1
                self.display_enhanced_solution(finding, solution)
        
        if enhanced_solutions_found == 0:
            print("ℹ️  No enhanced solutions found in current report.")
            print("💡 This might be expected for demo data - enhanced solutions")
            print("   are generated for new scans with the enhanced agent enabled.")
        else:
            print(f"\n🎉 Found {enhanced_solutions_found} enhanced solution(s)!")
    
    def is_enhanced_solution(self, solution: Dict[str, Any]) -> bool:
        """Check if a solution has enhanced XAI features."""
        enhanced_indicators = [
            "confidence_score",
            "evidence",
            "alternative_solutions", 
            "xai_reasoning",
            "pros_cons",
            "implementation_complexity"
        ]
        
        return any(indicator in solution for indicator in enhanced_indicators)
    
    def display_enhanced_solution(self, finding: Dict[str, Any], solution: Dict[str, Any]):
        """Display enhanced solution details in readable format."""
        print(f"\n🔍 FINDING: {finding.get('rule_id', 'Unknown')}")
        print("-" * 40)
        print(f"📄 Message: {finding.get('message', 'No description')}")
        print(f"🎯 Severity: {finding.get('severity', 'unknown')}")
        print(f"📁 File: {finding.get('file_path', 'unknown')}")
        
        # Primary solution
        primary = solution.get("primary_solution", {})
        if primary:
            print(f"\n🥇 PRIMARY SOLUTION: {primary.get('approach_name', 'Unnamed')}")
            print(f"   Complexity: {primary.get('implementation_complexity', 'unknown')}")
            if 'confidence_score' in primary:
                print(f"   Confidence: {primary['confidence_score']:.2f}")
        
        # Alternative solutions
        alternatives = solution.get("alternative_solutions", [])
        if alternatives:
            print(f"\n🔄 ALTERNATIVES ({len(alternatives)}):")
            for i, alt in enumerate(alternatives, 1):
                print(f"   {i}. {alt.get('approach_name', 'Unnamed Alternative')}")
                if 'confidence_score' in alt:
                    print(f"      Confidence: {alt['confidence_score']:.2f}")
        
        # XAI features
        if 'overall_reasoning' in solution:
            reasoning = solution['overall_reasoning']
            print(f"\n🧠 XAI REASONING:")
            print(f"   Primary Reason: {reasoning.get('primary_reason', '')[:80]}...")
            print(f"   Evidence Items: {len(reasoning.get('evidence', []))}")
            print(f"   Confidence: {reasoning.get('confidence_score', 0):.2f}")
    
    def test_api_endpoints(self):
        """Test specific API endpoints related to enhanced solutions."""
        print("\n🔧 Testing Enhanced Solution API Endpoints")
        print("=" * 55)
        
        # Test available scans
        try:
            response = self.session.get(f"{self.base_url}/scans/", timeout=5)
            if response.status_code == 200:
                scans = response.json()
                print(f"✅ Available scans: {len(scans)}")
                for scan in scans[:3]:  # Show first 3
                    print(f"   📋 {scan.get('scan_id', 'unknown')} - {scan.get('status', 'unknown')}")
            else:
                print(f"❌ Scans endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Scans endpoint error: {str(e)}")
        
        # Test API documentation
        try:
            response = self.session.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                print("✅ API documentation accessible at /docs")
            else:
                print(f"❌ API docs not accessible: {response.status_code}")
        except Exception as e:
            print(f"❌ API docs error: {str(e)}")
    
    def open_browser_for_manual_testing(self):
        """Open browser windows for manual testing."""
        print("\n🌐 Opening Browser for Manual Testing")
        print("=" * 45)
        
        urls_to_open = [
            (f"{self.base_url}/docs", "API Documentation (Swagger UI)"),
            (f"{self.base_url}/redoc", "API Documentation (ReDoc)"),
            (f"{self.base_url}/scans/", "Available Scans API"),
            (f"{self.base_url}/health", "Health Check API")
        ]
        
        for url, description in urls_to_open:
            try:
                print(f"🔗 Opening: {description}")
                print(f"   URL: {url}")
                webbrowser.open(url)
                time.sleep(1)  # Small delay between opens
            except Exception as e:
                print(f"❌ Failed to open {url}: {str(e)}")
        
        print("\n💡 Manual Testing Instructions:")
        print("1. Check API documentation in browser for enhanced solution endpoints")
        print("2. Test POST /scans/initiate with enhanced settings")
        print("3. Monitor GET /scans/jobs/{job_id}/status for progress")
        print("4. Retrieve GET /scans/{scan_id}/report for enhanced solutions")
        print("5. Look for XAI features: confidence_score, evidence, alternatives")
    
    def demonstrate_enhanced_features(self):
        """Demonstrate enhanced solution features with sample data."""
        print("\n🎯 ENHANCED SOLUTION FEATURES DEMONSTRATION")
        print("=" * 60)
        
        sample_enhanced_solution = {
            "finding_id": "sql_injection_001",
            "suggestion_type": "security_fix", 
            "primary_solution": {
                "approach_name": "Parameterized Query Implementation",
                "confidence_score": 0.95,
                "implementation_complexity": "low",
                "pros_cons": {
                    "pros": ["Complete SQL injection prevention", "Better performance"],
                    "cons": ["Requires code refactoring", "Learning curve"]
                }
            },
            "alternative_solutions": [
                {
                    "approach_name": "ORM-Based Query Builder",
                    "confidence_score": 0.82,
                    "implementation_complexity": "medium"
                },
                {
                    "approach_name": "Stored Procedure Implementation", 
                    "confidence_score": 0.75,
                    "implementation_complexity": "high"
                }
            ],
            "overall_reasoning": {
                "primary_reason": "Parameterized queries provide complete protection against SQL injection",
                "confidence_score": 0.95,
                "evidence": [
                    {"type": "security_principle", "description": "OWASP Top 10 recommendation"},
                    {"type": "performance_benchmark", "description": "15-30% query improvement"}
                ]
            }
        }
        
        print("📋 SAMPLE ENHANCED SOLUTION STRUCTURE:")
        print(json.dumps(sample_enhanced_solution, indent=2))
        
        print("\n🧠 KEY XAI FEATURES DEMONSTRATED:")
        print("✓ Multiple solution alternatives with confidence scores")
        print("✓ Pros/cons analysis for each approach")
        print("✓ Evidence-based reasoning with specific sources")
        print("✓ Implementation complexity assessment")
        print("✓ Numerical confidence scoring (0.0-1.0)")
        print("✓ Context-specific suggestion types")


def main():
    """Run the enhanced solution manual testing suite."""
    print("🎯 ENHANCED SOLUTION SUGGESTION AGENT - MANUAL TEST")
    print("=" * 70)
    print("Testing XAI capabilities, multiple alternatives, and web API integration")
    print()
    
    tester = EnhancedSolutionTester()
    
    # Step 1: Check backend health
    if not tester.check_backend_health():
        print("❌ Backend not available. Please start the backend server:")
        print("   python -m uvicorn src.webapp.backend.api.main:app --reload --port 8000")
        sys.exit(1)
    
    # Step 2: Test API endpoints
    tester.test_api_endpoints()
    
    # Step 3: Get and analyze existing report
    report_data = tester.get_enhanced_scan_report("demo_scan_1")
    if report_data:
        tester.analyze_enhanced_solutions(report_data)
    
    # Step 4: Demonstrate enhanced features
    tester.demonstrate_enhanced_features()
    
    # Step 5: Open browser for manual testing
    tester.open_browser_for_manual_testing()
    
    # Step 6: Test new scan (optional)
    user_input = input("\n❓ Do you want to test a new enhanced scan? (y/n): ").lower().strip()
    if user_input == 'y':
        job_id = tester.test_scan_initiation()
        if job_id:
            if tester.monitor_scan_progress(job_id):
                # Get the new report
                enhanced_report = tester.get_enhanced_scan_report("enhanced_test_scan")
                if enhanced_report:
                    tester.analyze_enhanced_solutions(enhanced_report)
    
    print("\n🎉 MANUAL TESTING COMPLETE")
    print("=" * 40)
    print("🌐 Browser windows opened for further manual testing")
    print("📚 Check API documentation for detailed endpoint testing")
    print("🔧 Use Swagger UI to interactively test enhanced solution features")
    print("\n💡 Key URLs for manual testing:")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • ReDoc: http://localhost:8000/redoc") 
    print("   • Health: http://localhost:8000/health")
    print("   • Scans: http://localhost:8000/scans/")


if __name__ == "__main__":
    main() 