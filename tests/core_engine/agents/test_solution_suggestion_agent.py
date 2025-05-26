"""Unit tests for SolutionSuggestionAgent."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.core_engine.agents.solution_suggestion_agent import SolutionSuggestionAgent
from src.core_engine.agents.llm_orchestrator_agent import LLMOrchestratorAgent


@pytest.fixture
def mock_llm_orchestrator():
    """Create a mock LLMOrchestratorAgent."""
    orchestrator = Mock(spec=LLMOrchestratorAgent)
    
    # Mock response with structured format
    orchestrator.invoke_llm.return_value = """
### Explanation
This is a test issue that needs to be fixed because it violates coding standards.

### Impact
This could lead to debugging statements being left in production code.

### Solution
Remove the pdb.set_trace() statement and replace with proper logging.

### Suggested Code
```python
import logging
logger = logging.getLogger(__name__)

def test_function():
    logger.debug("Debug information here")
    return True
```

### Best Practices
Use logging instead of print statements for better control over output levels.
"""
    
    return orchestrator


@pytest.fixture
def solution_agent():
    """Create a SolutionSuggestionAgent instance."""
    return SolutionSuggestionAgent()


@pytest.fixture
def solution_agent_with_orchestrator(mock_llm_orchestrator):
    """Create a SolutionSuggestionAgent with LLM orchestrator."""
    return SolutionSuggestionAgent(llm_orchestrator=mock_llm_orchestrator)


@pytest.fixture
def sample_finding():
    """Create a sample static analysis finding."""
    return {
        'rule_id': 'pdb_set_trace',
        'message': 'pdb.set_trace() call detected',
        'line': 5,
        'category': 'debugging',
        'severity': 'high',
        'file_path': 'test.py'
    }


@pytest.fixture
def sample_code_snippet():
    """Create a sample code snippet."""
    return """def test_function():
    print("Starting test")
    pdb.set_trace()
    result = some_calculation()
    return result"""


def test_init_without_orchestrator(solution_agent):
    """Test SolutionSuggestionAgent initialization without orchestrator."""
    assert solution_agent.llm_orchestrator is None


def test_init_with_orchestrator(solution_agent_with_orchestrator, mock_llm_orchestrator):
    """Test SolutionSuggestionAgent initialization with orchestrator."""
    assert solution_agent_with_orchestrator.llm_orchestrator == mock_llm_orchestrator


def test_construct_solution_prompt(solution_agent, sample_finding, sample_code_snippet):
    """Test solution prompt construction."""
    prompt = solution_agent._construct_solution_prompt(sample_finding, sample_code_snippet)
    
    # Verify prompt contains all necessary components
    assert 'pdb_set_trace' in prompt
    assert 'pdb.set_trace() call detected' in prompt
    assert 'debugging' in prompt
    assert 'high' in prompt
    assert 'Line**: 5' in prompt
    assert sample_code_snippet in prompt
    assert '### Explanation' in prompt
    assert '### Impact' in prompt
    assert '### Solution' in prompt
    assert '### Suggested Code' in prompt
    assert '### Best Practices' in prompt


def test_parse_llm_response_structured(solution_agent):
    """Test parsing of structured LLM response."""
    llm_response = """
### Explanation
This is a debugging statement that should not be in production.

### Impact
Could expose sensitive information or cause performance issues.

### Solution
1. Remove the pdb.set_trace() statement
2. Add proper logging instead

### Suggested Code
```python
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug point reached")
```

### Best Practices
Use logging framework with appropriate levels.
"""
    
    parsed = solution_agent._parse_llm_response(llm_response)
    
    assert 'debugging statement' in parsed['explanation']
    assert 'sensitive information' in parsed['impact']
    assert 'Remove the pdb.set_trace()' in parsed['solution']
    assert 'import logging' in parsed['suggested_code']
    assert 'logging framework' in parsed['best_practices']


def test_parse_llm_response_unstructured(solution_agent):
    """Test parsing of unstructured LLM response."""
    llm_response = "This is just a plain text response without sections."
    
    parsed = solution_agent._parse_llm_response(llm_response)
    
    assert parsed['explanation'] == llm_response
    assert parsed['impact'] == ''
    assert parsed['solution'] == ''
    assert parsed['suggested_code'] == ''
    assert parsed['best_practices'] == ''


def test_refine_llm_solution_success(solution_agent, sample_finding, sample_code_snippet, mock_llm_orchestrator):
    """Test successful solution refinement."""
    solution = solution_agent.refine_llm_solution(
        finding=sample_finding,
        code_snippet=sample_code_snippet,
        llm_orchestrator=mock_llm_orchestrator
    )
    
    # Verify solution structure
    assert solution['finding_id'] == 'pdb_set_trace'
    assert solution['category'] == 'debugging'
    assert solution['severity'] == 'high'
    assert solution['line'] == 5
    assert solution['original_message'] == 'pdb.set_trace() call detected'
    assert 'test issue' in solution['explanation']
    assert 'debugging statements' in solution['impact']
    assert 'Remove the pdb.set_trace()' in solution['solution_steps']
    assert 'import logging' in solution['suggested_code']
    assert 'logging instead of print' in solution['best_practices']
    assert solution['confidence'] == 'high'
    assert 'generated_at' in solution
    
    # Verify LLM was called
    mock_llm_orchestrator.invoke_llm.assert_called_once()


def test_refine_llm_solution_no_orchestrator(solution_agent, sample_finding, sample_code_snippet):
    """Test solution refinement without orchestrator."""
    with pytest.raises(ValueError, match="No LLMOrchestratorAgent provided"):
        solution_agent.refine_llm_solution(
            finding=sample_finding,
            code_snippet=sample_code_snippet
        )


def test_refine_llm_solution_with_instance_orchestrator(solution_agent_with_orchestrator, sample_finding, sample_code_snippet):
    """Test solution refinement using instance orchestrator."""
    solution = solution_agent_with_orchestrator.refine_llm_solution(
        finding=sample_finding,
        code_snippet=sample_code_snippet
    )
    
    assert solution['finding_id'] == 'pdb_set_trace'
    assert solution['confidence'] == 'high'


def test_refine_llm_solution_error_handling(solution_agent, sample_finding, sample_code_snippet):
    """Test error handling in solution refinement."""
    # Mock orchestrator that raises an exception
    mock_orchestrator = Mock()
    mock_orchestrator.invoke_llm.side_effect = Exception("LLM API error")
    
    solution = solution_agent.refine_llm_solution(
        finding=sample_finding,
        code_snippet=sample_code_snippet,
        llm_orchestrator=mock_orchestrator
    )
    
    # Verify fallback solution
    assert solution['finding_id'] == 'pdb_set_trace'
    assert solution['confidence'] == 'low'
    assert 'Unable to generate detailed solution' in solution['explanation']
    assert 'error' in solution
    assert solution['solution_steps'] == 'Manual review required'


def test_refine_multiple_solutions(solution_agent, mock_llm_orchestrator):
    """Test refining multiple findings into solutions."""
    findings = [
        {
            'rule_id': 'pdb_set_trace',
            'message': 'pdb.set_trace() detected',
            'line': 5,
            'category': 'debugging',
            'severity': 'high',
            'file_path': 'test.py'
        },
        {
            'rule_id': 'print_statement',
            'message': 'print() statement detected',
            'line': 10,
            'category': 'logging',
            'severity': 'medium',
            'file_path': 'test.py'
        }
    ]
    
    code_files = {
        'test.py': """def test_function():
    print("Starting test")
    pdb.set_trace()
    result = some_calculation()
    print("Result:", result)
    return result"""
    }
    
    solutions = solution_agent.refine_multiple_solutions(
        findings=findings,
        code_files=code_files,
        llm_orchestrator=mock_llm_orchestrator
    )
    
    assert len(solutions) == 2
    assert solutions[0]['finding_id'] == 'pdb_set_trace'
    assert solutions[1]['finding_id'] == 'print_statement'
    
    # Verify LLM was called for each finding
    assert mock_llm_orchestrator.invoke_llm.call_count == 2


def test_refine_multiple_solutions_missing_file(solution_agent, mock_llm_orchestrator):
    """Test refining solutions when code file is missing."""
    findings = [{
        'rule_id': 'test_rule',
        'message': 'Test issue',
        'line': 1,
        'category': 'test',
        'severity': 'low',
        'file_path': 'missing.py'
    }]
    
    code_files = {}
    
    solutions = solution_agent.refine_multiple_solutions(
        findings=findings,
        code_files=code_files,
        llm_orchestrator=mock_llm_orchestrator
    )
    
    assert len(solutions) == 1
    assert solutions[0]['finding_id'] == 'test_rule'
    
    # Verify LLM was still called with "Code snippet not available"
    mock_llm_orchestrator.invoke_llm.assert_called_once()


def test_get_agent_info(solution_agent):
    """Test getting agent information."""
    info = solution_agent.get_agent_info()
    
    assert info['agent_name'] == 'SolutionSuggestionAgent'
    assert info['version'] == '1.0.0'
    assert info['has_llm_orchestrator'] is False
    assert 'solution_refinement' in info['capabilities']
    assert 'code_suggestion' in info['capabilities']
    assert 'explanation_generation' in info['capabilities']
    assert 'best_practice_recommendations' in info['capabilities']


def test_get_agent_info_with_orchestrator(solution_agent_with_orchestrator):
    """Test getting agent information with orchestrator."""
    info = solution_agent_with_orchestrator.get_agent_info()
    
    assert info['has_llm_orchestrator'] is True


def test_prompt_construction_edge_cases(solution_agent):
    """Test prompt construction with missing finding data."""
    finding = {}  # Empty finding
    code_snippet = "def test(): pass"
    
    prompt = solution_agent._construct_solution_prompt(finding, code_snippet)
    
    # Should handle missing data gracefully
    assert 'Unknown Issue' in prompt
    assert 'No description available' in prompt
    assert 'general' in prompt
    assert 'medium' in prompt
    assert code_snippet in prompt


def test_multiple_code_blocks_in_response(solution_agent):
    """Test parsing response with multiple code blocks."""
    llm_response = """
### Explanation
Here's the issue explanation.

### Solution
First, here's some example code:
```python
# Example 1
print("test")
```

And here's the actual solution:
```python
# Solution code
import logging
logger = logging.getLogger(__name__)
logger.info("test")
```
"""
    
    parsed = solution_agent._parse_llm_response(llm_response)
    
    # Should take the last code block as suggested code
    assert 'import logging' in parsed['suggested_code']
    assert 'logger.info("test")' in parsed['suggested_code']
    assert 'print("test")' not in parsed['suggested_code'] 