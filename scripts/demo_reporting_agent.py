#!/usr/bin/env python3
"""
Demo script for ReportingAgent.

This script demonstrates the capabilities of the ReportingAgent by generating
sample reports with mock data.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core_engine.agents.reporting_agent import ReportingAgent


def create_sample_static_findings():
    """Create sample static analysis findings for demonstration."""
    return [
        {
            "rule_id": "PDB_TRACE_FOUND",
            "message": "pdb.set_trace() found - remove before production",
            "line": 25,
            "column": 4,
            "severity": "Warning",
            "category": "debugging",
            "file": "src/api/handlers.py",
            "suggestion": "Remove pdb.set_trace() before deploying to production"
        },
        {
            "rule_id": "PRINT_STATEMENT_FOUND",
            "message": "print() statement found - use logging instead",
            "line": 42,
            "column": 8,
            "severity": "Info", 
            "category": "logging",
            "file": "src/utils/helpers.py",
            "suggestion": "Replace print() with proper logging (logger.info, logger.debug)"
        },
        {
            "rule_id": "FUNCTION_TOO_LONG",
            "message": "Function 'process_data' is 85 lines long (max 50)",
            "line": 15,
            "column": 1,
            "severity": "Warning",
            "category": "complexity",
            "file": "src/data/processor.py",
            "suggestion": "Break down large function into smaller, focused functions"
        },
        {
            "rule_id": "POTENTIALLY_UNUSED_IMPORT",
            "message": "Import 'unused_module' appears to be unused",
            "line": 3,
            "column": 1,
            "severity": "Info",
            "category": "imports",
            "file": "src/main.py",
            "suggestion": "Remove unused import to clean up code"
        },
        {
            "rule_id": "CLASS_TOO_LONG",
            "message": "Class 'DataManager' is 250 lines long (max 200)",
            "line": 8,
            "column": 1,
            "severity": "Error",
            "category": "complexity",
            "file": "src/data/manager.py",
            "suggestion": "Split large class into multiple focused classes"
        }
    ]


def create_sample_llm_insights():
    """Create sample LLM insights for demonstration."""
    return """# AI Code Review Analysis

## Code Quality Assessment
- The overall code structure shows good organization with clear separation of concerns
- Function and variable naming follows Python conventions consistently
- Code readability is generally good with appropriate comments and docstrings

## Security Considerations
- **Critical**: Debugging statements detected that must be removed before production deployment
- Remove all pdb.set_trace() calls to prevent security vulnerabilities
- Consider implementing proper logging levels for different environments
- No obvious SQL injection or XSS vulnerabilities detected in the analyzed code

## Performance Analysis  
- **Performance Concern**: Large functions and classes detected that may impact maintainability
- The 85-line function 'process_data' should be refactored for better performance and readability
- Consider implementing caching mechanisms for frequently accessed data
- Review database query patterns for potential optimization opportunities

## Best Practices
- **Logging Issues**: Print statements detected that should use proper logging framework
- Implement structured logging with appropriate log levels (DEBUG, INFO, WARNING, ERROR)
- Consider using configuration files for environment-specific settings
- Follow PEP 8 style guidelines consistently across the codebase

## Architectural Insights
- Current code shows signs of growing complexity that may benefit from refactoring
- Consider implementing design patterns like Strategy or Factory for better maintainability
- The large DataManager class suggests a need for Single Responsibility Principle application
- Evaluate opportunities for dependency injection to improve testability

## Specific Recommendations
1. **Immediate**: Remove all debugging statements (pdb.set_trace) before production
2. **High Priority**: Implement proper logging framework to replace print statements  
3. **Medium Priority**: Refactor large functions (>50 lines) into smaller, focused components
4. **Medium Priority**: Split large classes (>200 lines) following Single Responsibility Principle
5. **Low Priority**: Clean up unused imports to improve code clarity
6. **Code Quality**: Add comprehensive unit tests for all new functionality
7. **Documentation**: Ensure all public functions have proper docstrings
8. **Configuration**: Implement environment-specific configuration management"""


def create_sample_scan_details():
    """Create sample scan details for demonstration."""
    return {
        "repo_url": "https://github.com/example/ai-code-reviewer-demo",
        "pr_id": 42,
        "branch": "feature/reporting-improvements", 
        "scan_type": "pr",
        "total_files": 12,
        "successful_parses": 11,
        "scan_id": "demo_scan_2025_01_27"
    }


def demo_basic_report_generation():
    """Demonstrate basic report generation functionality."""
    print("🚀 ReportingAgent Demo - Basic Report Generation")
    print("=" * 60)
    
    # Initialize the ReportingAgent
    reporting_agent = ReportingAgent()
    
    # Create sample data
    static_findings = create_sample_static_findings()
    llm_insights = create_sample_llm_insights()
    scan_details = create_sample_scan_details()
    
    print(f"📊 Sample Data:")
    print(f"   - Static Findings: {len(static_findings)} issues")
    print(f"   - LLM Insights: {len(llm_insights.split())} words")
    print(f"   - Repository: {scan_details['repo_url']}")
    print(f"   - PR ID: #{scan_details['pr_id']}")
    print()
    
    # Generate structured report data
    print("📋 Generating structured report data...")
    report_data = reporting_agent.generate_report_data(
        static_findings=static_findings,
        llm_insights=llm_insights,
        scan_details=scan_details
    )
    
    # Display summary statistics
    summary = report_data['summary']
    print(f"✅ Report generated successfully!")
    print(f"   - Total Findings: {summary['total_findings']}")
    print(f"   - Severity Breakdown: {summary['severity_breakdown']}")
    print(f"   - Categories: {list(summary['category_breakdown'].keys())}")
    print(f"   - Has LLM Analysis: {summary['has_llm_analysis']}")
    print()
    
    return report_data, reporting_agent


def demo_markdown_formatting(report_data, reporting_agent):
    """Demonstrate Markdown report formatting."""
    print("📝 Formatting Markdown Report")
    print("=" * 40)
    
    # Generate Markdown report
    markdown_report = reporting_agent.format_markdown_report(report_data)
    
    print(f"📄 Markdown report generated ({len(markdown_report)} characters)")
    print()
    
    # Display first few lines of the report
    lines = markdown_report.split('\n')
    print("🔍 Report Preview (first 20 lines):")
    print("-" * 40)
    for i, line in enumerate(lines[:20], 1):
        print(f"{i:2d}: {line}")
    print("...")
    print(f"    (Total: {len(lines)} lines)")
    print()
    
    return markdown_report


def demo_json_export(report_data, reporting_agent):
    """Demonstrate JSON export functionality."""
    print("🔄 JSON Export")
    print("=" * 20)
    
    # Export as JSON
    json_report = reporting_agent.export_json(report_data)
    
    print(f"📦 JSON export completed ({len(json_report)} characters)")
    
    # Display structure overview
    import json
    parsed_json = json.loads(json_report)
    print("🏗️  JSON Structure:")
    for key in parsed_json.keys():
        print(f"   - {key}")
    print()
    
    return json_report


def demo_error_handling():
    """Demonstrate error handling capabilities."""
    print("⚠️  Error Handling Demo")
    print("=" * 30)
    
    reporting_agent = ReportingAgent()
    
    # Test with invalid data
    print("🧪 Testing with invalid data...")
    error_report = reporting_agent.generate_report_data(
        static_findings=None,  # Invalid
        llm_insights="",
        scan_details={}
    )
    
    print(f"✅ Error handled gracefully:")
    print(f"   - Scan Status: {error_report['summary']['scan_status']}")
    print(f"   - Total Findings: {error_report['summary']['total_findings']}")
    print()
    
    # Test error markdown generation
    error_markdown = reporting_agent._generate_error_markdown("Demo error", {})
    print("📝 Error Markdown generated:")
    print("   - Contains error information")
    print("   - Provides user-friendly message")
    print()


def demo_report_features():
    """Demonstrate advanced report features."""
    print("🎯 Advanced Features Demo")
    print("=" * 35)
    
    reporting_agent = ReportingAgent()
    
    # Test supported formats
    formats = reporting_agent.get_supported_formats()
    print(f"📋 Supported Formats: {formats}")
    
    # Test empty findings scenario
    empty_data = reporting_agent.generate_report_data(
        static_findings=[],
        llm_insights="",
        scan_details={"repo_url": "https://github.com/example/clean-repo"}
    )
    
    empty_markdown = reporting_agent.format_markdown_report(empty_data)
    print("✅ Empty findings report:")
    print("   - Handles zero issues gracefully")
    print("   - Shows positive messaging")
    print(f"   - Report length: {len(empty_markdown)} characters")
    print()


def save_demo_reports(markdown_report, json_report):
    """Save demo reports to files."""
    print("💾 Saving Demo Reports")
    print("=" * 30)
    
    try:
        # Create reports directory if it doesn't exist
        reports_dir = "demo_reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Save Markdown report
        with open(f"{reports_dir}/demo_report.md", "w", encoding="utf-8") as f:
            f.write(markdown_report)
        
        # Save JSON report  
        with open(f"{reports_dir}/demo_report.json", "w", encoding="utf-8") as f:
            f.write(json_report)
        
        print(f"✅ Reports saved to {reports_dir}/")
        print(f"   - demo_report.md ({len(markdown_report)} chars)")
        print(f"   - demo_report.json ({len(json_report)} chars)")
        print()
        
    except Exception as e:
        print(f"❌ Error saving reports: {e}")
        print()


def main():
    """Main demo function."""
    print("🎉 ReportingAgent Comprehensive Demo")
    print("=" * 50)
    print("This demo showcases the capabilities of the ReportingAgent")
    print("for generating comprehensive code review reports.")
    print()
    
    try:
        # Demo 1: Basic report generation
        report_data, agent = demo_basic_report_generation()
        
        # Demo 2: Markdown formatting
        markdown_report = demo_markdown_formatting(report_data, agent)
        
        # Demo 3: JSON export
        json_report = demo_json_export(report_data, agent)
        
        # Demo 4: Error handling
        demo_error_handling()
        
        # Demo 5: Advanced features
        demo_report_features()
        
        # Demo 6: Save reports
        save_demo_reports(markdown_report, json_report)
        
        print("🎊 Demo completed successfully!")
        print("All ReportingAgent features demonstrated.")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 