#!/usr/bin/env python3
"""
Demo script for Enhanced Solution Suggestion Agent.

This script demonstrates the enhanced XAI capabilities, multiple solution alternatives,
and comprehensive error handling of the new solution suggestion agent.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from unittest.mock import Mock
import json
from datetime import datetime

from src.core_engine.agents.enhanced_solution_suggestion_agent import EnhancedSolutionSuggestionAgent
from src.core_engine.agents.models.solution_suggestion_models import (
    SuggestionType, ConfidenceLevel
)


def create_mock_llm_orchestrator():
    """Create a mock LLM orchestrator with realistic responses."""
    orchestrator = Mock()
    
    # Mock response for SQL injection vulnerability
    def mock_sql_injection_response(*args, **kwargs):
        return """
## PRIMARY SOLUTION

### Approach Name
Parameterized Query Implementation

### Description
Replace string concatenation with parameterized queries to completely eliminate SQL injection vulnerabilities.

### Reasoning
**Primary Reason:** Parameterized queries provide complete protection against SQL injection by separating SQL logic from data
**Supporting Reasons:**
- Database automatically handles parameter escaping and validation
- Improves query performance through prepared statement caching
- Industry standard security practice recommended by OWASP
- Works across all major database systems
**Confidence Score:** 0.95
**Evidence:**
- OWASP Top 10 recommends parameterized queries as primary defense
- CVE database shows 99% reduction in SQL injection when properly implemented
- Performance benchmarks show 15-30% improvement in query execution
**Assumptions:**
- Database driver supports parameterized queries
- Development team can be trained on proper syntax
- Existing query structure allows for parameterization
**Limitations:**
- Cannot parameterize table/column names dynamically
- May require refactoring of complex dynamic queries

### Pros and Cons
**Pros:**
- Complete SQL injection prevention
- Better query performance
- Database-agnostic security approach
- Simplified input validation requirements
- Easier code maintenance

**Cons:**
- Requires refactoring existing code
- Learning curve for team members
- Cannot handle all dynamic SQL scenarios

**Trade-offs:**
- Initial development time vs. long-term security
- Code complexity vs. attack surface reduction
- Performance optimization vs. security hardening

**Risk Assessment:** Very low risk - proven solution with extensive real-world validation

### Implementation Complexity
low - Standard database operation with well-documented patterns

### Code Suggestion
```python
# Title: Convert to parameterized query
# Description: Replace string formatting with safe parameter binding
def get_user_data(user_id):
    # Before: Vulnerable to SQL injection
    # query = f"SELECT * FROM users WHERE id = {user_id}"
    
    # After: Safe parameterized query
    query = "SELECT * FROM users WHERE id = ?"
    result = database.execute(query, (user_id,))
    return result
```

**Impact Assessment:** High positive impact - eliminates critical security vulnerability while improving performance

### Implementation Steps
1. Identify all string-formatted SQL queries in codebase
2. Replace string formatting with parameterized query syntax
3. Update database.execute calls to pass parameters separately
4. Add input validation for additional defense in depth
5. Test with various input types including edge cases
6. Update code review guidelines to catch future SQL injection risks

## ALTERNATIVE SOLUTION 1

### Approach Name
ORM-Based Query Builder

### Description
Implement an Object-Relational Mapping (ORM) solution to provide higher-level database abstraction with built-in SQL injection protection.

### Reasoning
**Primary Reason:** ORMs provide automatic SQL injection protection with higher developer productivity
**Supporting Reasons:**
- Automatic parameter binding and escaping
- Type safety and validation
- Database-agnostic code
- Reduced boilerplate and maintenance overhead
**Confidence Score:** 0.82
**Evidence:**
- Popular ORMs like SQLAlchemy have strong security track records
- 40% reduction in database-related bugs in projects using ORMs
- Built-in protection against common SQL vulnerabilities
**Assumptions:**
- Team willing to adopt ORM framework
- Application architecture supports ORM integration
- Performance requirements allow for ORM overhead
**Limitations:**
- Learning curve for complex ORM features
- Potential performance overhead for simple queries
- Less control over generated SQL

### Pros and Cons
**Pros:**
- Comprehensive security protection
- Higher development productivity
- Better code maintainability
- Built-in validation and type checking
- Database migration management

**Cons:**
- Framework dependency and lock-in
- Performance overhead for simple operations
- Complex queries may be harder to optimize
- Additional abstraction layer to understand

**Trade-offs:**
- Development speed vs. SQL control
- Security automation vs. query optimization
- Framework benefits vs. dependency management

**Risk Assessment:** Low risk - mature frameworks with strong community support

### Implementation Complexity
medium - Requires framework setup and team training

### Code Suggestion
```python
# Title: ORM-based secure query
# Description: Use SQLAlchemy ORM for automatic SQL injection protection
from sqlalchemy.orm import sessionmaker
from models import User

def get_user_data(user_id):
    session = sessionmaker()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    return user
```

**Impact Assessment:** Moderate positive impact - comprehensive security with development productivity gains

### Implementation Steps
1. Choose appropriate ORM framework (SQLAlchemy, Django ORM, etc.)
2. Design database models and relationships
3. Set up ORM configuration and connection management
4. Migrate existing queries to ORM syntax
5. Train team on ORM best practices
6. Implement proper session management and connection pooling

## ALTERNATIVE SOLUTION 2

### Approach Name
Stored Procedure Implementation

### Description
Move SQL logic to database stored procedures to eliminate dynamic query construction in application code.

### Reasoning
**Primary Reason:** Stored procedures eliminate SQL injection by removing dynamic query construction from application layer
**Supporting Reasons:**
- Database-level access control and validation
- Improved performance through precompilation
- Centralized business logic management
- Clear separation of data access and application logic
**Confidence Score:** 0.75
**Evidence:**
- Database vendors recommend stored procedures for security-critical operations
- Performance benefits of 20-40% for complex operations
- Simplified application code with clear API boundaries
**Assumptions:**
- Database supports stored procedures
- Team has database development expertise
- Application architecture allows for database-centric logic
**Limitations:**
- Database vendor lock-in
- More complex deployment and version management
- Debugging challenges across application and database layers

### Pros and Cons
**Pros:**
- Excellent performance for complex operations
- Strong security through database-level access control
- Simplified application data access layer
- Centralized business rule enforcement

**Cons:**
- Database vendor dependency
- Complex development and deployment workflow
- Limited portability across database systems
- Requires additional database development skills

**Trade-offs:**
- Performance optimization vs. vendor independence
- Security isolation vs. development complexity
- Centralized logic vs. application flexibility

**Risk Assessment:** Medium risk - requires careful architecture and team capability assessment

### Implementation Complexity
high - Requires database development expertise and workflow changes

### Code Suggestion
```python
# Title: Stored procedure implementation
# Description: Call secure stored procedure instead of dynamic SQL
def get_user_data(user_id):
    # Call stored procedure with parameters
    result = database.call_procedure('sp_GetUserData', [user_id])
    return result
```

**Impact Assessment:** High positive impact for performance and security, with increased complexity

### Implementation Steps
1. Design stored procedure interface and security model
2. Implement stored procedures with proper parameter validation
3. Create application wrapper functions for stored procedure calls
4. Update deployment scripts to include database schema changes
5. Implement stored procedure version management
6. Train team on stored procedure development and debugging

## OVERALL ANALYSIS

### Impact Analysis
The SQL injection vulnerability represents a critical security risk that could lead to data breaches, unauthorized access, and compliance violations. Implementing any of these solutions will significantly reduce the attack surface and improve the overall security posture. The parameterized query approach provides the best balance of security, performance, and implementation simplicity.

### Context Considerations
- Current development team expertise and available training time
- Existing codebase size and complexity
- Database infrastructure and vendor requirements
- Performance requirements and scalability needs
- Regulatory compliance and security audit requirements
- Integration with existing development and deployment workflows

### Best Practices
- Always use parameterized queries or equivalent protection for dynamic SQL
- Implement input validation and sanitization as defense in depth
- Regular security code reviews focusing on data access patterns
- Automated static analysis to detect SQL injection vulnerabilities
- Database principle of least privilege for application accounts
- Regular security testing including SQL injection attack simulations

### Confidence Breakdown
- **Solution Accuracy:** 0.93
- **Implementation Feasibility:** 0.88
- **Impact Assessment:** 0.95
- **Risk Analysis:** 0.91
"""
    
    orchestrator.invoke_llm = mock_sql_injection_response
    return orchestrator


def create_sample_findings():
    """Create sample findings for testing."""
    return [
        {
            'rule_id': 'sql_injection_001',
            'message': 'Potential SQL injection vulnerability in user query',
            'line': 45,
            'category': 'security',
            'severity': 'critical',
            'file_path': 'api/user_service.py'
        },
        {
            'rule_id': 'performance_loop_001',
            'message': 'Inefficient nested loop detected',
            'line': 23,
            'category': 'performance',
            'severity': 'medium',
            'file_path': 'utils/data_processor.py'
        },
        {
            'rule_id': 'test_coverage_001',
            'message': 'Missing unit tests for critical function',
            'line': 12,
            'category': 'testing',
            'severity': 'low',
            'file_path': 'core/calculator.py'
        }
    ]


def create_sample_code():
    """Create sample code snippets."""
    return {
        'api/user_service.py': '''
def get_user_by_id(user_id):
    """Get user information by ID."""
    # Vulnerable SQL query construction
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = database.execute(query)
    
    if result:
        return result[0]
    return None

def update_user_profile(user_id, profile_data):
    """Update user profile information."""
    fields = []
    values = []
    
    for key, value in profile_data.items():
        fields.append(f"{key} = '{value}'")
    
    query = f"UPDATE users SET {', '.join(fields)} WHERE id = {user_id}"
    return database.execute(query)
''',
        
        'utils/data_processor.py': '''
def process_data_inefficient(data_list):
    """Process data with inefficient nested loops."""
    results = []
    
    for item in data_list:
        for subitem in item.subitems:
            for detail in subitem.details:
                if detail.is_valid():
                    results.append(process_detail(detail))
    
    return results

def find_duplicates(items):
    """Find duplicate items using inefficient O(n²) algorithm."""
    duplicates = []
    
    for i, item1 in enumerate(items):
        for j, item2 in enumerate(items[i+1:], i+1):
            if item1.id == item2.id:
                duplicates.append((i, j))
    
    return duplicates
''',
        
        'core/calculator.py': '''
def calculate_compound_interest(principal, rate, time, compounds_per_year=1):
    """Calculate compound interest."""
    amount = principal * (1 + rate / compounds_per_year) ** (compounds_per_year * time)
    return amount - principal

def calculate_loan_payment(principal, annual_rate, years):
    """Calculate monthly loan payment."""
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        return principal / num_payments
    
    payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    return payment
'''
    }


def demo_single_solution():
    """Demonstrate single solution generation with detailed XAI output."""
    print("🔍 DEMO: Enhanced Solution Suggestion Agent - Single Solution")
    print("=" * 70)
    
    # Create agent with enhanced capabilities
    agent = EnhancedSolutionSuggestionAgent(
        enable_alternatives=True,
        max_alternatives=2,
        confidence_threshold=0.8
    )
    
    # Create mock orchestrator
    orchestrator = create_mock_llm_orchestrator()
    
    # Sample security finding
    finding = {
        'rule_id': 'sql_injection_001',
        'message': 'Potential SQL injection vulnerability in user query',
        'line': 45,
        'category': 'security',
        'severity': 'critical',
        'file_path': 'api/user_service.py'
    }
    
    code_snippet = '''def get_user_by_id(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = database.execute(query)
    return result[0] if result else None'''
    
    print(f"📋 Finding: {finding['rule_id']}")
    print(f"📄 Message: {finding['message']}")
    print(f"🎯 Type: {finding['category']} ({finding['severity']})")
    print()
    
    # Generate enhanced solution
    print("🚀 Generating enhanced solution with XAI capabilities...")
    solution = agent.generate_enhanced_solution(
        finding=finding,
        code_snippet=code_snippet,
        llm_orchestrator=orchestrator
    )
    
    # Display results
    print("\n✅ ENHANCED SOLUTION GENERATED")
    print("=" * 50)
    
    print(f"🎯 Solution Type: {solution.suggestion_type.value}")
    print(f"📊 Overall Confidence: {solution.overall_reasoning.confidence_score:.2f} ({solution.overall_reasoning.confidence_level.value})")
    print(f"⏱️  Processing Time: {solution.processing_time_ms}ms")
    print()
    
    # Primary solution details
    print("🥇 PRIMARY SOLUTION")
    print("-" * 30)
    primary = solution.primary_solution
    print(f"Name: {primary.approach_name}")
    print(f"Description: {primary.description[:100]}...")
    print(f"Complexity: {primary.implementation_complexity}")
    print(f"Confidence: {primary.reasoning.confidence_score:.2f}")
    print(f"Evidence Count: {len(primary.reasoning.evidence)}")
    print(f"Code Suggestions: {len(primary.code_suggestions)}")
    print()
    
    # Alternative solutions
    if solution.alternative_solutions:
        print(f"🔄 ALTERNATIVE SOLUTIONS ({len(solution.alternative_solutions)})")
        print("-" * 40)
        for i, alt in enumerate(solution.alternative_solutions, 1):
            print(f"{i}. {alt.approach_name}")
            print(f"   Confidence: {alt.reasoning.confidence_score:.2f}")
            print(f"   Complexity: {alt.implementation_complexity}")
            print()
    
    # XAI Analysis
    print("🧠 EXPLAINABLE AI ANALYSIS")
    print("-" * 35)
    reasoning = solution.overall_reasoning
    print(f"Primary Reason: {reasoning.primary_reason[:80]}...")
    print(f"Supporting Reasons: {len(reasoning.supporting_reasons)}")
    print(f"Evidence Items: {len(reasoning.evidence)}")
    print(f"Assumptions: {len(reasoning.assumptions)}")
    print(f"Limitations: {len(reasoning.limitations)}")
    print()
    
    # Impact analysis
    if solution.impact_analysis:
        print("📈 IMPACT ANALYSIS")
        print("-" * 25)
        print(solution.impact_analysis[:200] + "...")
        print()
    
    # Implementation guidance
    if solution.implementation_steps:
        print("🛠️  IMPLEMENTATION STEPS")
        print("-" * 30)
        for i, step in enumerate(solution.implementation_steps[:3], 1):
            print(f"{i}. {step}")
        if len(solution.implementation_steps) > 3:
            print(f"   ... and {len(solution.implementation_steps) - 3} more steps")
        print()
    
    return solution


def demo_batch_processing():
    """Demonstrate batch processing of multiple findings."""
    print("\n🔄 DEMO: Batch Solution Processing")
    print("=" * 50)
    
    # Create agent
    agent = EnhancedSolutionSuggestionAgent(
        enable_alternatives=True,
        max_alternatives=2
    )
    
    # Create mock orchestrator with varied responses
    orchestrator = Mock()
    responses = [
        "## PRIMARY SOLUTION\n### Approach Name\nSecurity Fix\n### Description\nFix security issue",
        "## PRIMARY SOLUTION\n### Approach Name\nPerformance Optimization\n### Description\nOptimize performance",
        "## PRIMARY SOLUTION\n### Approach Name\nTest Coverage\n### Description\nAdd missing tests"
    ]
    orchestrator.invoke_llm.side_effect = responses
    
    # Sample findings and code
    findings = create_sample_findings()
    code_files = create_sample_code()
    
    print(f"📋 Processing {len(findings)} findings...")
    print()
    
    # Generate batch solutions
    batch = agent.generate_solution_batch(
        findings=findings,
        code_files=code_files,
        llm_orchestrator=orchestrator
    )
    
    # Display batch results
    print("✅ BATCH PROCESSING COMPLETE")
    print("-" * 35)
    print(f"📊 Total Findings: {batch.total_findings}")
    print(f"✅ Successful: {batch.successful_suggestions}")
    print(f"❌ Failed: {batch.failed_suggestions}")
    print(f"⏱️  Total Time: {batch.total_processing_time_ms}ms")
    
    if batch.average_confidence:
        print(f"📈 Average Confidence: {batch.average_confidence:.2f}")
    
    print()
    
    # Suggestion type breakdown
    if batch.suggestion_types_breakdown:
        print("🏷️  SUGGESTION TYPES")
        print("-" * 25)
        for suggestion_type, count in batch.suggestion_types_breakdown.items():
            print(f"{suggestion_type.value}: {count}")
        print()
    
    # Individual solution summaries
    print("📋 INDIVIDUAL SOLUTIONS")
    print("-" * 30)
    for i, solution in enumerate(batch.suggestions, 1):
        print(f"{i}. {solution.finding_id}")
        print(f"   Type: {solution.suggestion_type.value}")
        print(f"   Confidence: {solution.overall_reasoning.confidence_score:.2f}")
        print(f"   Alternatives: {len(solution.alternative_solutions)}")
        print()
    
    return batch


def demo_agent_metrics():
    """Demonstrate agent metrics and performance tracking."""
    print("\n📊 DEMO: Agent Metrics & Performance")
    print("=" * 45)
    
    # Create agent
    agent = EnhancedSolutionSuggestionAgent()
    
    # Simulate some activity
    for i in range(5):
        agent.metrics['total_suggestions'] += 1
        agent.metrics['successful_suggestions'] += 1
        agent.metrics['generation_times'].append(0.1 + i * 0.05)
    
    # Get metrics
    metrics = agent.get_metrics()
    
    print("📈 PERFORMANCE METRICS")
    print("-" * 30)
    print(f"Total Suggestions: {metrics.total_suggestions}")
    print(f"Success Rate: {metrics.success_rate:.1%}")
    print(f"Average Generation Time: {metrics.average_generation_time_ms:.1f}ms")
    print()
    
    # Get agent info
    info = agent.get_agent_info()
    
    print("ℹ️  AGENT INFORMATION")
    print("-" * 25)
    print(f"Agent: {info['agent_name']}")
    print(f"Version: {info['version']}")
    print(f"Has LLM: {info['has_llm_orchestrator']}")
    print()
    
    print("🚀 CAPABILITIES")
    print("-" * 20)
    for capability in info['capabilities']:
        print(f"✓ {capability.replace('_', ' ').title()}")
    print()
    
    return metrics, info


def main():
    """Run the complete demo."""
    print("🎯 ENHANCED SOLUTION SUGGESTION AGENT DEMO")
    print("=" * 75)
    print("Demonstrating XAI capabilities, multiple alternatives, and error handling")
    print()
    
    try:
        # Demo 1: Single solution with detailed XAI
        solution = demo_single_solution()
        
        # Demo 2: Batch processing
        batch = demo_batch_processing()
        
        # Demo 3: Metrics and agent info
        metrics, info = demo_agent_metrics()
        
        print("🎉 DEMO COMPLETE")
        print("=" * 30)
        print("The Enhanced Solution Suggestion Agent demonstrates:")
        print("✓ Explainable AI with confidence scoring and evidence")
        print("✓ Multiple solution alternatives with pros/cons analysis")
        print("✓ Diverse suggestion types (security, performance, testing)")
        print("✓ Comprehensive error handling and fallback mechanisms")
        print("✓ Performance metrics and quality tracking")
        print("✓ Rich metadata for continuous improvement")
        print()
        print("Ready for production use in AI Code Review System! 🚀")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 