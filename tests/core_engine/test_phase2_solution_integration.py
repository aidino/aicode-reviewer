"""Integration tests for SolutionSuggestionAgent with LLMOrchestratorAgent."""

import pytest
from unittest.mock import Mock, patch

from src.core_engine.agents.solution_suggestion_agent import SolutionSuggestionAgent
from src.core_engine.agents.llm_orchestrator_agent import LLMOrchestratorAgent


@pytest.fixture
def llm_orchestrator():
    """Create LLMOrchestratorAgent with mock provider."""
    return LLMOrchestratorAgent(llm_provider='mock')


@pytest.fixture
def solution_agent():
    """Create SolutionSuggestionAgent."""
    return SolutionSuggestionAgent()


@pytest.fixture
def sample_findings():
    """Create sample static analysis findings."""
    return [
        {
            'rule_id': 'pdb_set_trace',
            'message': 'pdb.set_trace() call detected',
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


@pytest.fixture
def sample_code_files():
    """Create sample code files."""
    return {
        'test.py': """def test_function():
    print("Starting test")
    pdb.set_trace()
    result = some_calculation()
    print("Result:", result)
    return result

def another_function():
    # TODO: Implement this function
    pass"""
    }


def test_solution_integration_single_finding(solution_agent, llm_orchestrator, sample_findings, sample_code_files):
    """Test integration between SolutionSuggestionAgent and LLMOrchestratorAgent for single finding."""
    finding = sample_findings[0]  # pdb_set_trace finding
    code_snippet = sample_code_files['test.py']
    
    # Generate solution using integration
    solution = solution_agent.refine_llm_solution(
        finding=finding,
        code_snippet=code_snippet,
        llm_orchestrator=llm_orchestrator
    )
    
    # Verify solution structure
    assert solution['finding_id'] == 'pdb_set_trace'
    assert solution['category'] == 'debugging'
    assert solution['severity'] == 'high'
    assert solution['confidence'] == 'high'
    assert 'explanation' in solution
    assert 'solution_steps' in solution
    assert 'suggested_code' in solution
    assert 'generated_at' in solution


def test_solution_integration_multiple_findings(solution_agent, llm_orchestrator, sample_findings, sample_code_files):
    """Test integration for multiple findings."""
    solutions = solution_agent.refine_multiple_solutions(
        findings=sample_findings,
        code_files=sample_code_files,
        llm_orchestrator=llm_orchestrator
    )
    
    # Verify all findings were processed
    assert len(solutions) == len(sample_findings)
    
    # Verify solution structures
    for i, solution in enumerate(solutions):
        assert solution['finding_id'] == sample_findings[i]['rule_id']
        assert solution['category'] == sample_findings[i]['category']
        assert solution['severity'] == sample_findings[i]['severity']
        assert 'explanation' in solution
        assert 'solution_steps' in solution


def test_solution_integration_prompt_construction(solution_agent, llm_orchestrator):
    """Test that proper prompts are constructed for LLM."""
    finding = {
        'rule_id': 'magic_number',
        'message': 'Magic number detected',
        'line': 15,
        'category': 'maintainability',
        'severity': 'low',
        'file_path': 'calc.py'
    }
    
    code_snippet = "result = value * 3.14159"
    
    # Capture the prompt that would be sent to LLM
    prompt = solution_agent._construct_solution_prompt(finding, code_snippet)
    
    # Verify prompt contains all necessary information
    assert 'magic_number' in prompt
    assert 'Magic number detected' in prompt
    assert 'maintainability' in prompt
    assert 'low' in prompt
    assert 'Line**: 15' in prompt
    assert 'result = value * 3.14159' in prompt
    
    # Verify structured format
    assert '### Explanation' in prompt
    assert '### Impact' in prompt
    assert '### Solution' in prompt
    assert '### Suggested Code' in prompt
    assert '### Best Practices' in prompt


def test_solution_integration_error_recovery(solution_agent, llm_orchestrator):
    """Test error recovery when LLM fails."""
    finding = {
        'rule_id': 'test_rule',
        'message': 'Test issue',
        'line': 1,
        'category': 'test',
        'severity': 'medium',
        'file_path': 'test.py'
    }
    
    # Mock LLM to raise an exception
    llm_orchestrator.invoke_llm = Mock(side_effect=Exception("LLM API error"))
    
    solution = solution_agent.refine_llm_solution(
        finding=finding,
        code_snippet="def test(): pass",
        llm_orchestrator=llm_orchestrator
    )
    
    # Verify fallback solution is generated
    assert solution['finding_id'] == 'test_rule'
    assert solution['confidence'] == 'low'
    assert 'Unable to generate detailed solution' in solution['explanation']
    assert 'error' in solution
    assert solution['solution_steps'] == 'Manual review required'


def test_solution_integration_with_rag_enabled():
    """Test solution generation with RAG-enabled LLM orchestrator."""
    # Create LLM orchestrator with RAG enabled (but mocked)
    with patch('src.core_engine.agents.llm_orchestrator_agent.RAGContextAgent'):
        llm_orchestrator = LLMOrchestratorAgent(llm_provider='mock', use_rag=True)
        solution_agent = SolutionSuggestionAgent()
        
        finding = {
            'rule_id': 'unused_import',
            'message': 'Unused import detected',
            'line': 1,
            'category': 'optimization',
            'severity': 'low',
            'file_path': 'main.py'
        }
        
        code_snippet = "import os\nimport sys\n\ndef main():\n    print('hello')"
        
        solution = solution_agent.refine_llm_solution(
            finding=finding,
            code_snippet=code_snippet,
            llm_orchestrator=llm_orchestrator
        )
        
        # Verify solution was generated even with RAG enabled
        assert solution['finding_id'] == 'unused_import'
        assert solution['confidence'] == 'high'
        assert 'explanation' in solution


def test_solution_integration_end_to_end():
    """Test end-to-end integration from findings to refined solutions."""
    # Create agents
    llm_orchestrator = LLMOrchestratorAgent(llm_provider='mock')
    solution_agent = SolutionSuggestionAgent(llm_orchestrator=llm_orchestrator)
    
    # Sample workflow data
    findings = [
        {
            'rule_id': 'function_too_long',
            'message': 'Function exceeds recommended length',
            'line': 1,
            'category': 'complexity',
            'severity': 'medium',
            'file_path': 'utils.py'
        }
    ]
    
    code_files = {
        'utils.py': """def complex_function():
    # This is a very long function
    step1 = True
    step2 = False
    # ... many more lines
    return step1 and step2"""
    }
    
    # Generate refined solutions
    solutions = solution_agent.refine_multiple_solutions(
        findings=findings,
        code_files=code_files
    )
    
    # Verify end-to-end processing
    assert len(solutions) == 1
    solution = solutions[0]
    
    assert solution['finding_id'] == 'function_too_long'
    assert solution['category'] == 'complexity'
    assert solution['severity'] == 'medium'
    assert solution['confidence'] == 'high'
    
    # Verify solution content
    assert len(solution['explanation']) > 0
    # Note: solution_steps might be empty if mock response doesn't contain structured sections
    assert 'solution_steps' in solution
    assert 'generated_at' in solution
    
    # Verify metadata
    agent_info = solution_agent.get_agent_info()
    assert agent_info['agent_name'] == 'SolutionSuggestionAgent'
    assert agent_info['has_llm_orchestrator'] is True 