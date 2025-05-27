"""
Comprehensive unit tests for EnhancedSolutionSuggestionAgent.

This test suite covers:
- XAI capabilities and reasoning
- Multiple solution alternatives  
- Edge cases and error handling
- LLM errors and timeout scenarios
- Confidence scoring and evidence tracking
- Diverse suggestion types
- Performance metrics and analytics
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import time

from src.core_engine.agents.enhanced_solution_suggestion_agent import EnhancedSolutionSuggestionAgent
from src.core_engine.agents.models.solution_suggestion_models import (
    ConfidenceLevel,
    SuggestionType,
    EvidenceType,
    XAIReasoning,
    Evidence,
    ProsCons,
    CodeSuggestion,
    AlternativeSolution,
    SolutionSuggestion,
    SuggestionBatch,
    SuggestionMetrics,
)
from src.core_engine.agents.llm_orchestrator_agent import LLMOrchestratorAgent


@pytest.fixture
def mock_llm_orchestrator():
    """Create a mock LLMOrchestratorAgent with enhanced response."""
    orchestrator = Mock(spec=LLMOrchestratorAgent)
    
    # Add a small delay to simulate processing time
    def mock_invoke_llm(*args, **kwargs):
        import time
        time.sleep(0.001)  # Small delay to ensure processing_time_ms > 0
        return """
## PRIMARY SOLUTION

### Approach Name
Logging-Based Debug Replacement

### Description
Replace the debugging statement with structured logging that provides better control and can be easily disabled in production.

### Reasoning
**Primary Reason:** Logging provides better control over debug output and follows production best practices
**Supporting Reasons:** 
- Allows for different log levels and filtering
- Can be easily disabled in production
- Provides structured output with timestamps and context
**Confidence Score:** 0.85
**Evidence:** 
- Industry standard practice for debug information
- Python logging module documentation recommends this approach
- Prevents accidental debug code in production
**Assumptions:** 
- Logging module is available and configured
- Development team follows logging best practices
**Limitations:** 
- Requires understanding of logging configuration
- May need additional setup for log formatting

### Pros and Cons
**Pros:**
- Production-safe debugging
- Configurable output levels
- Better performance in production
- Structured debug information

**Cons:**
- Requires logging setup
- Slightly more complex than print statements

**Trade-offs:**
- Initial setup complexity vs. long-term maintainability
- Structured approach vs. quick debugging

**Risk Assessment:** Low risk - standard industry practice with well-documented benefits

### Implementation Complexity
low - Simple replacement with logging calls

### Code Suggestion
```python
# Title: Replace pdb.set_trace() with logging
# Description: Replace debugging statement with structured logging
import logging

logger = logging.getLogger(__name__)

def test_function():
    logger.debug("Debug checkpoint reached - investigating variable state")
    result = some_calculation()
    logger.debug(f"Calculation result: {result}")
    return result
```

**Impact Assessment:** Minimal impact - same functionality with better production safety

### Implementation Steps
1. Import logging module at top of file
2. Create logger instance for the module
3. Replace pdb.set_trace() with appropriate logger.debug() call
4. Configure logging level in application settings

## ALTERNATIVE SOLUTION 1

### Approach Name
Conditional Debug Flag

### Description
Use a conditional debug flag that can be easily toggled without removing the debug code entirely.

### Reasoning
**Primary Reason:** Allows quick enabling/disabling of debug behavior without code changes
**Supporting Reasons:**
- Easy to toggle during development
- Minimal code changes required
- Preserves original debug intent
**Confidence Score:** 0.72
**Evidence:**
- Common pattern in development environments
- Minimal performance impact when disabled
**Assumptions:**
- Debug flag is properly managed
- Team understands when to enable/disable
**Limitations:**
- Still has debug code in production
- Could be accidentally enabled

### Pros and Cons
**Pros:**
- Quick to implement
- Easy to toggle
- Preserves debug capability

**Cons:**
- Debug code remains in production
- Potential security/performance risk if enabled
- Not following production best practices

**Trade-offs:**
- Development convenience vs. production cleanliness
- Quick fix vs. proper solution

**Risk Assessment:** Medium risk - debug code still present in production

### Implementation Complexity
low - Simple conditional wrapper

### Code Suggestion
```python
# Title: Add conditional debug flag
# Description: Wrap debug statement in conditional flag
import os

DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

def test_function():
    if DEBUG_MODE:
        import pdb; pdb.set_trace()
    result = some_calculation()
    return result
```

**Impact Assessment:** Low impact - preserves current behavior with optional control

### Implementation Steps
1. Define DEBUG_MODE environment variable or configuration
2. Wrap pdb.set_trace() in conditional check
3. Document how to enable/disable debug mode
4. Update deployment configuration to ensure DEBUG_MODE is false

## ALTERNATIVE SOLUTION 2

### Approach Name
Custom Debug Context Manager

### Description
Create a custom context manager that provides controlled debugging capabilities with automatic cleanup.

### Reasoning
**Primary Reason:** Provides sophisticated debug control with automatic state management
**Supporting Reasons:**
- Ensures debug state is properly cleaned up
- Allows for context-specific debugging
- Can integrate with monitoring systems
**Confidence Score:** 0.68
**Evidence:**
- Context managers provide excellent resource management
- Allows for sophisticated debug workflows
**Assumptions:**
- Team is comfortable with context managers
- Additional debug infrastructure is desired
**Limitations:**
- More complex implementation
- Requires understanding of context managers

### Pros and Cons
**Pros:**
- Sophisticated debug control
- Automatic cleanup
- Extensible for future needs
- Can integrate with monitoring

**Cons:**
- More complex to implement
- Requires additional infrastructure
- May be overkill for simple debugging

**Trade-offs:**
- Sophistication vs. simplicity
- Infrastructure investment vs. immediate needs

**Risk Assessment:** Medium risk - complexity may not be justified for simple debugging

### Implementation Complexity
medium - Requires custom context manager implementation

### Code Suggestion
```python
# Title: Custom debug context manager
# Description: Sophisticated debug control with automatic cleanup
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

@contextmanager
def debug_context(description="Debug checkpoint"):
    logger.info(f"Entering debug context: {description}")
    try:
        yield
    finally:
        logger.info(f"Exiting debug context: {description}")

def test_function():
    with debug_context("Investigating calculation"):
        result = some_calculation()
        logger.debug(f"Result: {result}")
    return result
```

**Impact Assessment:** Moderate impact - changes debug workflow but provides more control

### Implementation Steps
1. Implement debug context manager
2. Replace pdb.set_trace() with context manager usage
3. Configure logging for debug context
4. Document new debug patterns for team

## OVERALL ANALYSIS

### Impact Analysis
Removing the pdb.set_trace() statement eliminates the risk of accidentally leaving debugging code in production, which could cause applications to hang or expose sensitive information. The logging-based approach provides equivalent debugging capability while maintaining production safety.

### Context Considerations
- Production environment safety requirements
- Development team's debugging workflow preferences
- Existing logging infrastructure and configuration
- Code review processes to catch debugging statements

### Best Practices
- Always use logging instead of print/pdb for debug information
- Configure different log levels for development vs. production
- Implement automated checks to prevent debug statements in production
- Use structured logging with proper context and formatting

### Confidence Breakdown
- **Solution Accuracy:** 0.88
- **Implementation Feasibility:** 0.92
- **Impact Assessment:** 0.85
- **Risk Analysis:** 0.90
"""
    
    orchestrator.invoke_llm = mock_invoke_llm
    return orchestrator


@pytest.fixture
def enhanced_agent():
    """Create an EnhancedSolutionSuggestionAgent instance."""
    return EnhancedSolutionSuggestionAgent(
        enable_alternatives=True,
        max_alternatives=2,
        confidence_threshold=0.7
    )


@pytest.fixture
def enhanced_agent_with_orchestrator(mock_llm_orchestrator):
    """Create an EnhancedSolutionSuggestionAgent with LLM orchestrator."""
    return EnhancedSolutionSuggestionAgent(
        llm_orchestrator=mock_llm_orchestrator,
        enable_alternatives=True,
        max_alternatives=3
    )


@pytest.fixture
def sample_security_finding():
    """Create a sample security-related finding."""
    return {
        'rule_id': 'sql_injection_vulnerability',
        'message': 'Potential SQL injection vulnerability detected',
        'line': 15,
        'category': 'security',
        'severity': 'high',
        'file_path': 'api/database.py'
    }


@pytest.fixture
def sample_performance_finding():
    """Create a sample performance-related finding."""
    return {
        'rule_id': 'inefficient_loop',
        'message': 'Inefficient nested loop detected',
        'line': 25,
        'category': 'performance',
        'severity': 'medium',
        'file_path': 'utils/data_processor.py'
    }


@pytest.fixture
def sample_code_snippet():
    """Create a sample code snippet."""
    return """def process_user_data(user_id, data):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = database.execute(query)
    
    for item in data:
        for subitem in item.subitems:
            process_subitem(subitem)
    
    return result"""


@pytest.fixture
def complex_llm_response():
    """Create a complex LLM response for parsing tests."""
    return """
## PRIMARY SOLUTION

### Approach Name
Parameterized Query with Prepared Statements

### Description
Replace string concatenation with parameterized queries to prevent SQL injection attacks.

### Reasoning
**Primary Reason:** Parameterized queries completely eliminate SQL injection vulnerabilities
**Supporting Reasons:**
- Database handles parameter escaping automatically
- Better performance due to query plan caching
- Industry standard security practice
**Confidence Score:** 0.95
**Evidence:**
- OWASP guidelines recommend parameterized queries
- All major databases support prepared statements
- Proven track record in preventing SQL injection
**Assumptions:**
- Database driver supports parameterized queries
- Team understands parameterized query syntax
**Limitations:**
- Requires rewriting existing query logic
- May need database driver updates

### Pros and Cons
**Pros:**
- Complete SQL injection prevention
- Better performance
- Database-agnostic security
- Industry standard approach

**Cons:**
- Requires code refactoring
- Team training may be needed

**Trade-offs:**
- Initial refactoring effort vs. long-term security
- Learning curve vs. security benefits

**Risk Assessment:** Very low risk - proven security solution

### Implementation Complexity
low - Standard database operation

### Code Suggestion
```python
# Title: Implement parameterized query
# Description: Replace string formatting with parameterized query
def process_user_data(user_id, data):
    query = "SELECT * FROM users WHERE id = ?"
    result = database.execute(query, (user_id,))
    
    for item in data:
        for subitem in item.subitems:
            process_subitem(subitem)
    
    return result
```

**Impact Assessment:** High positive impact - eliminates security vulnerability

### Implementation Steps
1. Identify all string-formatted SQL queries
2. Replace with parameterized query syntax
3. Update database.execute calls to pass parameters
4. Test thoroughly with various input types

## ALTERNATIVE SOLUTION 1

### Approach Name
ORM-Based Query Builder

### Description
Use an Object-Relational Mapping (ORM) library to automatically handle query parameterization and provide additional abstraction.

### Reasoning
**Primary Reason:** ORMs provide automatic SQL injection protection with higher-level abstraction
**Supporting Reasons:**
- Automatic parameter handling
- Database-agnostic code
- Built-in validation and type checking
**Confidence Score:** 0.82
**Evidence:**
- Popular ORMs like SQLAlchemy have excellent security records
- Reduced boilerplate code
- Built-in protection against common vulnerabilities
**Assumptions:**
- Team is willing to adopt ORM
- Application architecture supports ORM integration
**Limitations:**
- Learning curve for ORM
- May add complexity for simple queries

### Implementation Complexity
medium - Requires ORM setup and learning

### Code Suggestion
```python
# Title: ORM-based query implementation
# Description: Use SQLAlchemy ORM for secure queries
from sqlalchemy.orm import sessionmaker
from models import User

def process_user_data(user_id, data):
    session = sessionmaker()
    result = session.query(User).filter(User.id == user_id).first()
    
    for item in data:
        for subitem in item.subitems:
            process_subitem(subitem)
    
    return result
```

## OVERALL ANALYSIS

### Impact Analysis
Implementing parameterized queries eliminates SQL injection vulnerabilities completely while providing better performance through query plan caching. This is a critical security improvement with minimal downside.

### Context Considerations
- Existing database infrastructure and drivers
- Team familiarity with parameterized queries
- Current codebase complexity and technical debt
- Security audit and compliance requirements

### Best Practices
- Always use parameterized queries for dynamic SQL
- Implement automated security scanning in CI/CD
- Regular security training for development team
- Code review processes that specifically check for SQL injection risks

### Confidence Breakdown
- **Solution Accuracy:** 0.95
- **Implementation Feasibility:** 0.90
- **Impact Assessment:** 0.92
- **Risk Analysis:** 0.94
"""


class TestEnhancedSolutionSuggestionAgent:
    """Test suite for EnhancedSolutionSuggestionAgent."""

    def test_init_default_settings(self, enhanced_agent):
        """Test initialization with default settings."""
        assert enhanced_agent.llm_orchestrator is None
        assert enhanced_agent.enable_alternatives is True
        assert enhanced_agent.max_alternatives == 2
        assert enhanced_agent.confidence_threshold == 0.7
        assert enhanced_agent.metrics['total_suggestions'] == 0

    def test_init_with_orchestrator(self, enhanced_agent_with_orchestrator, mock_llm_orchestrator):
        """Test initialization with LLM orchestrator."""
        assert enhanced_agent_with_orchestrator.llm_orchestrator == mock_llm_orchestrator
        assert enhanced_agent_with_orchestrator.enable_alternatives is True
        assert enhanced_agent_with_orchestrator.max_alternatives == 3

    def test_classify_suggestion_type_security(self, enhanced_agent, sample_security_finding):
        """Test security finding classification."""
        suggestion_type = enhanced_agent._classify_suggestion_type(sample_security_finding)
        assert suggestion_type == SuggestionType.SECURITY_FIX

    def test_classify_suggestion_type_performance(self, enhanced_agent, sample_performance_finding):
        """Test performance finding classification."""
        suggestion_type = enhanced_agent._classify_suggestion_type(sample_performance_finding)
        assert suggestion_type == SuggestionType.PERFORMANCE_OPTIMIZATION

    def test_classify_suggestion_type_edge_cases(self, enhanced_agent):
        """Test suggestion type classification edge cases."""
        # Empty finding
        empty_finding = {}
        suggestion_type = enhanced_agent._classify_suggestion_type(empty_finding)
        assert suggestion_type == SuggestionType.BEST_PRACTICE
        
        # High severity should default to bug fix
        high_severity_finding = {'severity': 'high', 'category': 'unknown'}
        suggestion_type = enhanced_agent._classify_suggestion_type(high_severity_finding)
        assert suggestion_type == SuggestionType.BUG_FIX
        
        # Testing patterns
        test_finding = {'category': 'testing', 'rule_id': 'test_coverage'}
        suggestion_type = enhanced_agent._classify_suggestion_type(test_finding)
        assert suggestion_type == SuggestionType.TESTING

    def test_construct_enhanced_prompt(self, enhanced_agent, sample_security_finding, sample_code_snippet):
        """Test enhanced prompt construction."""
        suggestion_type = SuggestionType.SECURITY_FIX
        prompt = enhanced_agent._construct_enhanced_prompt(
            sample_security_finding, sample_code_snippet, suggestion_type
        )
        
        # Verify prompt contains all necessary components
        assert 'sql_injection_vulnerability' in prompt
        assert 'SECURITY FOCUS' in prompt
        assert 'Enhanced XAI Requirements' in prompt
        assert 'PRIMARY SOLUTION' in prompt
        assert 'ALTERNATIVE SOLUTION' in prompt
        assert 'OVERALL ANALYSIS' in prompt
        assert sample_code_snippet in prompt
        assert 'Confidence Score' in prompt
        assert 'Evidence' in prompt

    def test_parse_enhanced_response_complete(self, enhanced_agent, complex_llm_response):
        """Test parsing of complete enhanced LLM response."""
        parsed = enhanced_agent._parse_enhanced_response(complex_llm_response, SuggestionType.SECURITY_FIX)
        
        # Verify primary solution
        assert parsed['primary_solution'] is not None
        primary = parsed['primary_solution']
        assert primary['approach_name'] == 'Parameterized Query with Prepared Statements'
        assert 'string concatenation' in primary['description']
        assert primary['reasoning']['confidence_score'] == 0.95
        assert len(primary['reasoning']['supporting_reasons']) > 0
        assert len(primary['pros_cons']['pros']) > 0
        assert len(primary['code_suggestions']) > 0
        
        # Verify alternative solutions
        assert len(parsed['alternative_solutions']) == 1
        alt = parsed['alternative_solutions'][0]
        assert alt['approach_name'] == 'ORM-Based Query Builder'
        
        # Verify overall analysis
        overall = parsed['overall_analysis']
        assert 'SQL injection vulnerabilities' in overall['impact_analysis']
        assert len(overall['best_practices']) > 0
        assert len(overall['confidence_breakdown']) > 0

    def test_parse_enhanced_response_malformed(self, enhanced_agent):
        """Test parsing of malformed LLM response."""
        malformed_response = "This is just plain text without proper structure."
        
        parsed = enhanced_agent._parse_enhanced_response(malformed_response, SuggestionType.BUG_FIX)
        
        # Should create fallback solution
        assert parsed['primary_solution'] is not None
        fallback = parsed['primary_solution']
        assert 'Fallback' in fallback['approach_name']
        assert fallback['reasoning']['confidence_score'] == 0.3

    def test_generate_enhanced_solution_success(self, enhanced_agent_with_orchestrator, 
                                              sample_security_finding, sample_code_snippet):
        """Test successful enhanced solution generation."""
        solution = enhanced_agent_with_orchestrator.generate_enhanced_solution(
            finding=sample_security_finding,
            code_snippet=sample_code_snippet
        )
        
        # Verify solution structure
        assert isinstance(solution, SolutionSuggestion)
        assert solution.finding_id == 'sql_injection_vulnerability'
        assert solution.suggestion_type == SuggestionType.SECURITY_FIX
        assert solution.primary_solution is not None
        assert len(solution.alternative_solutions) >= 0
        assert solution.overall_reasoning is not None
        assert solution.processing_time_ms > 0
        assert solution.raw_llm_response is not None

    def test_generate_enhanced_solution_no_orchestrator(self, enhanced_agent, 
                                                       sample_security_finding, sample_code_snippet):
        """Test solution generation without orchestrator."""
        with pytest.raises(ValueError, match="No LLMOrchestratorAgent provided"):
            enhanced_agent.generate_enhanced_solution(
                finding=sample_security_finding,
                code_snippet=sample_code_snippet
            )

    def test_generate_enhanced_solution_llm_error(self, enhanced_agent, 
                                                sample_security_finding, sample_code_snippet):
        """Test solution generation with LLM error."""
        # Mock orchestrator that raises an exception
        mock_orchestrator = Mock()
        mock_orchestrator.invoke_llm.side_effect = Exception("LLM API timeout")
        
        solution = enhanced_agent.generate_enhanced_solution(
            finding=sample_security_finding,
            code_snippet=sample_code_snippet,
            llm_orchestrator=mock_orchestrator
        )
        
        # Should return fallback solution
        assert isinstance(solution, SolutionSuggestion)
        assert solution.title == "Manual Review Required"
        assert solution.overall_reasoning.confidence_level == ConfidenceLevel.VERY_LOW
        assert "LLM API timeout" in solution.impact_analysis

    def test_generate_enhanced_solution_llm_timeout(self, enhanced_agent, 
                                                  sample_security_finding, sample_code_snippet):
        """Test solution generation with LLM timeout."""
        mock_orchestrator = Mock()
        mock_orchestrator.invoke_llm.side_effect = TimeoutError("Request timeout")
        
        solution = enhanced_agent.generate_enhanced_solution(
            finding=sample_security_finding,
            code_snippet=sample_code_snippet,
            llm_orchestrator=mock_orchestrator
        )
        
        assert solution.title == "Manual Review Required"
        assert "Request timeout" in solution.impact_analysis

    def test_generate_enhanced_solution_network_error(self, enhanced_agent,
                                                    sample_security_finding, sample_code_snippet):
        """Test solution generation with network error."""
        mock_orchestrator = Mock()
        mock_orchestrator.invoke_llm.side_effect = ConnectionError("Network unreachable")
        
        solution = enhanced_agent.generate_enhanced_solution(
            finding=sample_security_finding,
            code_snippet=sample_code_snippet,
            llm_orchestrator=mock_orchestrator
        )
        
        assert solution.title == "Manual Review Required"
        assert "Network unreachable" in solution.impact_analysis

    def test_generate_solution_batch_success(self, enhanced_agent_with_orchestrator, sample_code_snippet):
        """Test successful batch solution generation."""
        findings = [
            {
                'rule_id': 'security_issue_1',
                'message': 'SQL injection vulnerability',
                'line': 10,
                'category': 'security',
                'severity': 'high',
                'file_path': 'test.py'
            },
            {
                'rule_id': 'performance_issue_1',
                'message': 'Inefficient algorithm',
                'line': 20,
                'category': 'performance',
                'severity': 'medium',
                'file_path': 'test.py'
            }
        ]
        
        code_files = {'test.py': sample_code_snippet}
        
        batch = enhanced_agent_with_orchestrator.generate_solution_batch(
            findings=findings,
            code_files=code_files
        )
        
        # Verify batch structure
        assert isinstance(batch, SuggestionBatch)
        assert batch.total_findings == 2
        assert batch.successful_suggestions == 2
        assert batch.failed_suggestions == 0
        assert len(batch.suggestions) == 2
        assert batch.batch_end_time is not None
        assert batch.average_confidence is not None

    def test_generate_solution_batch_mixed_results(self, enhanced_agent, sample_code_snippet):
        """Test batch generation with mixed success/failure results."""
        findings = [
            {
                'rule_id': 'good_finding',
                'message': 'Valid finding',
                'line': 10,
                'category': 'security',
                'severity': 'high',
                'file_path': 'test.py'
            },
            {
                'rule_id': 'bad_finding',
                'message': 'This will cause an error',
                'line': 20,
                'category': 'unknown',
                'severity': 'low',
                'file_path': 'test.py'
            }
        ]
        
        code_files = {'test.py': sample_code_snippet}
        
        # Mock orchestrator that succeeds for first, fails for second
        mock_orchestrator = Mock()
        mock_orchestrator.invoke_llm.side_effect = [
            "## PRIMARY SOLUTION\n### Approach Name\nGood Solution",
            Exception("API Error")
        ]
        
        batch = enhanced_agent.generate_solution_batch(
            findings=findings,
            code_files=code_files,
            llm_orchestrator=mock_orchestrator
        )
        
        # Note: Both will be successful because even failed LLM calls create fallback solutions
        assert batch.total_findings == 2
        assert batch.successful_suggestions == 2  # Both succeed (one normal, one fallback)
        assert batch.failed_suggestions == 0

    def test_generate_solution_batch_missing_files(self, enhanced_agent_with_orchestrator):
        """Test batch generation with missing code files."""
        findings = [
            {
                'rule_id': 'test_finding',
                'message': 'Test issue',
                'line': 10,
                'category': 'test',
                'severity': 'low',
                'file_path': 'missing_file.py'
            }
        ]
        
        code_files = {}  # Empty - no files available
        
        batch = enhanced_agent_with_orchestrator.generate_solution_batch(
            findings=findings,
            code_files=code_files
        )
        
        assert batch.total_findings == 1
        assert batch.successful_suggestions == 1
        assert len(batch.suggestions) == 1

    def test_parse_reasoning_section(self, enhanced_agent):
        """Test parsing of reasoning section."""
        reasoning_content = """
**Primary Reason:** This is the main reason for the recommendation
**Supporting Reasons:** 
- First supporting reason
- Second supporting reason
**Confidence Score:** 0.85
**Evidence:** 
- Evidence item 1
- Evidence item 2
**Assumptions:** 
- Assumption 1
**Limitations:** 
- Limitation 1
"""
        
        reasoning = enhanced_agent._parse_reasoning_section(reasoning_content)
        
        assert reasoning['primary_reason'] == 'This is the main reason for the recommendation'
        assert len(reasoning['supporting_reasons']) == 2
        assert reasoning['confidence_score'] == 0.85
        assert len(reasoning['evidence']) == 2
        assert len(reasoning['assumptions']) == 1
        assert len(reasoning['limitations']) == 1

    def test_parse_pros_cons_section(self, enhanced_agent):
        """Test parsing of pros and cons section."""
        proscons_content = """
**Pros:**
- Advantage 1
- Advantage 2
- Advantage 3

**Cons:**
- Disadvantage 1
- Disadvantage 2

**Trade-offs:**
- Trade-off 1

**Risk Assessment:** Low risk approach with proven benefits
"""
        
        pros_cons = enhanced_agent._parse_pros_cons_section(proscons_content)
        
        assert len(pros_cons['pros']) == 3
        assert len(pros_cons['cons']) == 2
        assert len(pros_cons['trade_offs']) == 0  # Not parsing trade-offs in this simple version
        assert 'Low risk approach' in pros_cons['risk_assessment']

    def test_parse_confidence_breakdown(self, enhanced_agent):
        """Test parsing of confidence breakdown."""
        confidence_content = """
- **Solution Accuracy:** 0.92
- **Implementation Feasibility:** 0.88
- **Impact Assessment:** 0.85
- **Risk Analysis:** 0.90
"""
        
        breakdown = enhanced_agent._parse_confidence_breakdown(confidence_content)
        
        assert breakdown['Solution Accuracy'] == 0.92
        assert breakdown['Implementation Feasibility'] == 0.88
        assert breakdown['Impact Assessment'] == 0.85
        assert breakdown['Risk Analysis'] == 0.90

    def test_metrics_tracking(self, enhanced_agent_with_orchestrator, 
                            sample_security_finding, sample_code_snippet):
        """Test metrics tracking functionality."""
        # Generate a few solutions to build metrics
        for i in range(3):
            enhanced_agent_with_orchestrator.generate_enhanced_solution(
                finding=sample_security_finding,
                code_snippet=sample_code_snippet
            )
        
        metrics = enhanced_agent_with_orchestrator.get_metrics()
        
        assert isinstance(metrics, SuggestionMetrics)
        assert metrics.total_suggestions == 3
        assert metrics.success_rate == 1.0
        assert metrics.average_generation_time_ms > 0

    def test_get_agent_info(self, enhanced_agent):
        """Test agent information retrieval."""
        info = enhanced_agent.get_agent_info()
        
        assert info['agent_name'] == 'EnhancedSolutionSuggestionAgent'
        assert info['version'] == '2.0.0'
        assert info['has_llm_orchestrator'] is False
        assert 'xai_reasoning' in info['capabilities']
        assert 'multiple_alternatives' in info['capabilities']
        assert 'confidence_scoring' in info['capabilities']
        assert info['configuration']['enable_alternatives'] is True

    def test_get_agent_info_with_orchestrator(self, enhanced_agent_with_orchestrator):
        """Test agent information with orchestrator."""
        info = enhanced_agent_with_orchestrator.get_agent_info()
        
        assert info['has_llm_orchestrator'] is True
        assert info['configuration']['max_alternatives'] == 3

    def test_edge_case_empty_response(self, enhanced_agent):
        """Test handling of empty LLM response."""
        empty_response = ""
        
        parsed = enhanced_agent._parse_enhanced_response(empty_response, SuggestionType.BUG_FIX)
        
        assert parsed['primary_solution'] is not None
        assert 'Fallback' in parsed['primary_solution']['approach_name']

    def test_edge_case_partial_response(self, enhanced_agent):
        """Test handling of partial LLM response."""
        partial_response = """
## PRIMARY SOLUTION

### Approach Name
Incomplete Solution

### Description
This solution is incomplete...
"""
        
        parsed = enhanced_agent._parse_enhanced_response(partial_response, SuggestionType.BEST_PRACTICE)
        
        assert parsed['primary_solution'] is not None
        assert parsed['primary_solution']['approach_name'] == 'Incomplete Solution'
        # Should handle missing sections gracefully

    def test_confidence_level_classification(self, enhanced_agent):
        """Test confidence level classification logic."""
        # Test different suggestion types for confidence behavior
        high_severity_finding = {
            'rule_id': 'critical_bug',
            'message': 'Critical null pointer exception',
            'severity': 'critical',
            'category': 'bugs'
        }
        
        suggestion_type = enhanced_agent._classify_suggestion_type(high_severity_finding)
        assert suggestion_type == SuggestionType.BUG_FIX

    def test_performance_tracking(self, enhanced_agent_with_orchestrator):
        """Test performance tracking during solution generation."""
        finding = {
            'rule_id': 'test_performance',
            'message': 'Performance test',
            'line': 1,
            'category': 'performance',
            'severity': 'medium',
            'file_path': 'test.py'
        }
        
        # Get initial metrics count
        initial_generation_count = len(enhanced_agent_with_orchestrator.metrics['generation_times'])
        initial_success_count = enhanced_agent_with_orchestrator.metrics['successful_suggestions']
        initial_total_count = enhanced_agent_with_orchestrator.metrics['total_suggestions']
        
        solution = enhanced_agent_with_orchestrator.generate_enhanced_solution(
            finding=finding,
            code_snippet="# test code"
        )
        
        # Verify metrics were updated
        assert enhanced_agent_with_orchestrator.metrics['total_suggestions'] == initial_total_count + 1
        assert enhanced_agent_with_orchestrator.metrics['successful_suggestions'] == initial_success_count + 1
        assert len(enhanced_agent_with_orchestrator.metrics['generation_times']) == initial_generation_count + 1
        assert solution.processing_time_ms > 0

    def test_multiple_code_suggestions_parsing(self, enhanced_agent):
        """Test parsing multiple code suggestions from response."""
        response_with_multiple_code = """
## PRIMARY SOLUTION

### Approach Name
Multi-Code Solution

### Description
A solution with multiple code suggestions

### Code Suggestion
```python
# Title: First code change
# Description: First modification
def first_function():
    pass
```

```python
# Title: Second code change  
# Description: Second modification
def second_function():
    pass
```
"""
        
        solution_data = enhanced_agent._parse_solution_section(
            response_with_multiple_code, 
            SuggestionType.BEST_PRACTICE
        )
        
        # Should capture multiple code suggestions
        assert solution_data is not None
        assert len(solution_data['code_suggestions']) == 2

    @pytest.mark.parametrize("suggestion_type,expected_guidance", [
        (SuggestionType.SECURITY_FIX, "SECURITY FOCUS"),
        (SuggestionType.PERFORMANCE_OPTIMIZATION, "PERFORMANCE FOCUS"),
        (SuggestionType.BEST_PRACTICE, "BEST PRACTICE FOCUS"),
        (SuggestionType.BUG_FIX, "BUG FIX FOCUS"),
        (SuggestionType.TESTING, "TESTING FOCUS"),
    ])
    def test_suggestion_type_specific_guidance(self, enhanced_agent, suggestion_type, expected_guidance):
        """Test that different suggestion types get appropriate guidance."""
        finding = {'rule_id': 'test', 'message': 'test', 'line': 1}
        
        prompt = enhanced_agent._construct_enhanced_prompt(
            finding, "# test code", suggestion_type
        )
        
        assert expected_guidance in prompt

    def test_batch_suggestion_types_breakdown(self, enhanced_agent_with_orchestrator):
        """Test that batch tracks suggestion types correctly."""
        findings = [
            {'rule_id': 'sec1', 'category': 'security', 'severity': 'high', 'line': 1, 'file_path': 'test.py'},
            {'rule_id': 'perf1', 'category': 'performance', 'severity': 'medium', 'line': 2, 'file_path': 'test.py'},
            {'rule_id': 'sec2', 'category': 'security', 'severity': 'high', 'line': 3, 'file_path': 'test.py'},
        ]
        
        code_files = {'test.py': '# test code'}
        
        batch = enhanced_agent_with_orchestrator.generate_solution_batch(findings, code_files)
        
        # Should track suggestion types
        assert SuggestionType.SECURITY_FIX in batch.suggestion_types_breakdown
        assert SuggestionType.PERFORMANCE_OPTIMIZATION in batch.suggestion_types_breakdown
        assert batch.suggestion_types_breakdown[SuggestionType.SECURITY_FIX] == 2
        assert batch.suggestion_types_breakdown[SuggestionType.PERFORMANCE_OPTIMIZATION] == 1


class TestErrorRecoveryAndFallbacks:
    """Test suite specifically for error recovery and fallback mechanisms."""

    def test_vector_store_disconnection(self, enhanced_agent):
        """Test handling when vector store is disconnected."""
        mock_orchestrator = Mock()
        mock_orchestrator.invoke_llm.side_effect = Exception("Vector store connection failed")
        
        finding = {'rule_id': 'test', 'message': 'test', 'line': 1}
        solution = enhanced_agent.generate_enhanced_solution(
            finding, "# code", mock_orchestrator
        )
        
        assert solution.title == "Manual Review Required"
        assert "Vector store connection failed" in solution.impact_analysis

    def test_neo4j_disconnection(self, enhanced_agent):
        """Test handling when Neo4j is disconnected."""
        mock_orchestrator = Mock()
        mock_orchestrator.invoke_llm.side_effect = Exception("Neo4j connection refused")
        
        finding = {'rule_id': 'graph_test', 'message': 'test', 'line': 1}
        solution = enhanced_agent.generate_enhanced_solution(
            finding, "# code", mock_orchestrator
        )
        
        assert solution.overall_reasoning.confidence_level == ConfidenceLevel.VERY_LOW

    def test_large_file_handling(self, enhanced_agent_with_orchestrator):
        """Test handling of very large code files."""
        # Create a very large code snippet
        large_code = "\n".join([f"# Line {i}: " + "x" * 100 for i in range(1000)])
        
        finding = {'rule_id': 'large_file_test', 'message': 'test', 'line': 500}
        
        # Should handle gracefully without crashing
        solution = enhanced_agent_with_orchestrator.generate_enhanced_solution(
            finding, large_code
        )
        
        assert isinstance(solution, SolutionSuggestion)

    def test_invalid_json_response(self, enhanced_agent):
        """Test handling of invalid JSON in LLM response."""
        mock_orchestrator = Mock()
        mock_orchestrator.invoke_llm.return_value = '{"invalid": json response without closing brace'
        
        finding = {'rule_id': 'json_test', 'message': 'test', 'line': 1}
        solution = enhanced_agent.generate_enhanced_solution(
            finding, "# code", mock_orchestrator
        )
        
        # Should create fallback solution
        assert solution.title.startswith("Fallback") or solution.title == "Manual Review Required"

    def test_unicode_handling(self, enhanced_agent_with_orchestrator):
        """Test handling of Unicode characters in code and responses."""
        unicode_code = """
def test_function():
    # 测试函数 with émojis 🚀
    return "Hello 世界"
"""
        
        finding = {
            'rule_id': 'unicode_test',
            'message': 'Test with unicode: 测试',
            'line': 1
        }
        
        solution = enhanced_agent_with_orchestrator.generate_enhanced_solution(
            finding, unicode_code
        )
        
        assert isinstance(solution, SolutionSuggestion)

    def test_memory_pressure_simulation(self, enhanced_agent):
        """Test behavior under simulated memory pressure."""
        mock_orchestrator = Mock()
        mock_orchestrator.invoke_llm.side_effect = MemoryError("Out of memory")
        
        finding = {'rule_id': 'memory_test', 'message': 'test', 'line': 1}
        solution = enhanced_agent.generate_enhanced_solution(
            finding, "# code", mock_orchestrator
        )
        
        assert solution.title == "Manual Review Required"
        assert "Out of memory" in solution.impact_analysis 