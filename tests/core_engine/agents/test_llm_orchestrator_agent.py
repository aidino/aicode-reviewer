"""
Unit tests for LLMOrchestratorAgent.

This module contains comprehensive tests for the LLMOrchestratorAgent class,
including tests for mock LLM behavior, prompt construction, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.core_engine.agents.llm_orchestrator_agent import LLMOrchestratorAgent


class TestLLMOrchestratorAgent:
    """Test cases for LLMOrchestratorAgent class."""
    
    def test_init_mock_provider(self):
        """Test initialization with mock provider."""
        agent = LLMOrchestratorAgent(llm_provider='mock')
        
        assert agent.llm_provider == 'mock'
        assert agent.model_name == 'mock-gpt-4'
        assert agent.api_key is None
        assert 'mock' in agent.supported_providers
    
    def test_init_openai_provider(self):
        """Test initialization with OpenAI provider."""
        agent = LLMOrchestratorAgent(
            llm_provider='openai', 
            api_key='test-key', 
            model_name='gpt-4-turbo'
        )
        
        assert agent.llm_provider == 'openai'
        assert agent.model_name == 'gpt-4-turbo'
        assert agent.api_key == 'test-key'
    
    def test_init_openai_provider_no_key(self):
        """Test initialization with OpenAI provider but no API key."""
        with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
            agent = LLMOrchestratorAgent(llm_provider='openai')
            
            assert agent.llm_provider == 'openai'
            assert agent.model_name == 'gpt-4'
            mock_logger.warning.assert_called_with("OpenAI API key not provided. LLM calls will fail.")
    
    def test_init_local_provider(self):
        """Test initialization with local provider."""
        agent = LLMOrchestratorAgent(llm_provider='local', model_name='llama-2-7b')
        
        assert agent.llm_provider == 'local'
        assert agent.model_name == 'llama-2-7b'
    
    def test_init_anthropic_provider(self):
        """Test initialization with Anthropic provider."""
        agent = LLMOrchestratorAgent(
            llm_provider='anthropic', 
            api_key='test-key', 
            model_name='claude-3-opus'
        )
        
        assert agent.llm_provider == 'anthropic'
        assert agent.model_name == 'claude-3-opus'
        assert agent.api_key == 'test-key'
    
    def test_init_google_provider(self):
        """Test initialization with Google provider."""
        agent = LLMOrchestratorAgent(
            llm_provider='google', 
            api_key='test-key', 
            model_name='gemini-pro-vision'
        )
        
        assert agent.llm_provider == 'google'
        assert agent.model_name == 'gemini-pro-vision'
        assert agent.api_key == 'test-key'
    
    def test_init_unsupported_provider(self):
        """Test initialization with unsupported provider."""
        with pytest.raises(ValueError, match="Unsupported LLM provider: invalid"):
            LLMOrchestratorAgent(llm_provider='invalid')
    
    def test_construct_analysis_prompt_basic(self):
        """Test basic prompt construction."""
        agent = LLMOrchestratorAgent()
        
        prompt = agent._construct_analysis_prompt("Analyze this code")
        
        assert "# Code Review Analysis Request" in prompt
        assert "Analyze this code" in prompt
        assert "## Analysis Instructions:" in prompt
        assert "Code Quality Assessment" in prompt
    
    def test_construct_analysis_prompt_with_code(self):
        """Test prompt construction with code snippet."""
        agent = LLMOrchestratorAgent()
        code = "def hello():\n    print('Hello, World!')"
        
        prompt = agent._construct_analysis_prompt("Analyze this function", code)
        
        assert "## Code to Analyze:" in prompt
        assert "```python" in prompt
        assert code in prompt
    
    def test_construct_analysis_prompt_with_findings(self):
        """Test prompt construction with static analysis findings."""
        agent = LLMOrchestratorAgent()
        findings = [
            {
                'rule_id': 'PRINT_STATEMENT_FOUND',
                'line': 2,
                'message': 'print() statement found',
                'suggestion': 'Use logging instead'
            },
            {
                'rule_id': 'FUNCTION_TOO_LONG',
                'line': 10,
                'message': 'Function is too long'
            }
        ]
        
        prompt = agent._construct_analysis_prompt("Review findings", None, findings)
        
        assert "## Static Analysis Findings:" in prompt
        assert "PRINT_STATEMENT_FOUND" in prompt
        assert "Line 2" in prompt
        assert "Use logging instead" in prompt
        assert "FUNCTION_TOO_LONG" in prompt
        assert "Line 10" in prompt
    
    def test_construct_analysis_prompt_complete(self):
        """Test prompt construction with all components."""
        agent = LLMOrchestratorAgent()
        code = "def test(): pass"
        findings = [{'rule_id': 'TEST_RULE', 'line': 1, 'message': 'Test finding'}]
        
        prompt = agent._construct_analysis_prompt("Complete analysis", code, findings)
        
        assert "Complete analysis" in prompt
        assert "## Code to Analyze:" in prompt
        assert "## Static Analysis Findings:" in prompt
        assert "## Analysis Instructions:" in prompt
    
    def test_generate_mock_response_basic(self):
        """Test basic mock response generation."""
        agent = LLMOrchestratorAgent()
        
        response = agent._generate_mock_response("Analyze code")
        
        assert "# Mock LLM Analysis Results" in response
        assert "## Code Quality Assessment" in response
        assert "## Security Considerations" in response
        assert "## Performance Analysis" in response
        assert "## Best Practices" in response
        assert "## Architectural Insights" in response
        assert "## Specific Recommendations" in response
        assert "## Summary" in response
    
    def test_generate_mock_response_with_code(self):
        """Test mock response generation with code snippet."""
        agent = LLMOrchestratorAgent()
        code = "def hello(): print('Hello')"
        
        response = agent._generate_mock_response("Analyze", code)
        
        assert "well-organized with clear function definitions" in response
        assert "Variable naming follows Python conventions" in response
    
    def test_generate_mock_response_with_findings(self):
        """Test mock response generation with static findings."""
        agent = LLMOrchestratorAgent()
        findings = [
            {
                'rule_id': 'PDB_TRACE_FOUND',
                'category': 'debugging',
                'suggestion': 'Remove pdb.set_trace()'
            },
            {
                'rule_id': 'PRINT_STATEMENT_FOUND',
                'category': 'logging',
                'suggestion': 'Use proper logging'
            },
            {
                'rule_id': 'FUNCTION_TOO_LONG',
                'category': 'complexity',
                'suggestion': 'Break down function'
            }
        ]
        
        response = agent._generate_mock_response("Analyze", None, findings)
        
        assert "Security Alert" in response
        assert "Debugging statements detected" in response
        assert "Logging Issue" in response
        assert "print statements detected" in response
        assert "Performance Concern" in response
        assert "complexity issues detected" in response
        assert "Based on 3 static analysis findings" in response
    
    def test_generate_mock_response_with_imports(self):
        """Test mock response generation with import findings."""
        agent = LLMOrchestratorAgent()
        findings = [
            {
                'rule_id': 'POTENTIALLY_UNUSED_IMPORT',
                'category': 'imports',
                'suggestion': 'Remove unused import'
            }
        ]
        
        response = agent._generate_mock_response("Analyze", None, findings)
        
        assert "Import Optimization" in response
        assert "potentially unused imports" in response
    
    def test_invoke_llm_mock_provider(self):
        """Test LLM invocation with mock provider."""
        agent = LLMOrchestratorAgent(llm_provider='mock')
        
        response = agent.invoke_llm("Analyze this code")
        
        assert isinstance(response, str)
        assert "Mock LLM Analysis Results" in response
        assert len(response) > 100  # Should be a substantial response
    
    def test_invoke_llm_mock_with_code_and_findings(self):
        """Test LLM invocation with code and findings."""
        agent = LLMOrchestratorAgent(llm_provider='mock')
        code = "def test(): print('test')"
        findings = [{'rule_id': 'PRINT_FOUND', 'category': 'logging'}]
        
        response = agent.invoke_llm("Review code", code, findings)
        
        assert "Mock LLM Analysis Results" in response
        assert "well-organized" in response  # Should mention code structure
        assert "Logging Issue" in response  # Should address findings
    
    def test_invoke_llm_openai_fallback(self):
        """Test LLM invocation with OpenAI provider falls back to mock."""
        agent = LLMOrchestratorAgent(llm_provider='openai', api_key='test-key')
        
        with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
            response = agent.invoke_llm("Test prompt")
            
            assert "Mock LLM Analysis Results" in response
            mock_logger.warning.assert_called_with(
                "OpenAI integration not yet implemented, using mock response"
            )
    
    def test_invoke_llm_local_fallback(self):
        """Test LLM invocation with local provider falls back to mock."""
        agent = LLMOrchestratorAgent(llm_provider='local')
        
        with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
            response = agent.invoke_llm("Test prompt")
            
            assert "Mock LLM Analysis Results" in response
            mock_logger.warning.assert_called_with(
                "Local model integration not yet implemented, using mock response"
            )
    
    def test_invoke_llm_anthropic_fallback(self):
        """Test LLM invocation with Anthropic provider falls back to mock."""
        agent = LLMOrchestratorAgent(llm_provider='anthropic', api_key='test-key')
        
        with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
            response = agent.invoke_llm("Test prompt")
            
            assert "Mock LLM Analysis Results" in response
            mock_logger.warning.assert_called_with(
                "Anthropic integration not yet implemented, using mock response"
            )
    
    def test_invoke_llm_google_fallback(self):
        """Test LLM invocation with Google provider falls back to mock."""
        agent = LLMOrchestratorAgent(llm_provider='google', api_key='test-key')
        
        with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
            response = agent.invoke_llm("Test prompt")
            
            assert "Mock LLM Analysis Results" in response
            mock_logger.warning.assert_called_with(
                "Google integration not yet implemented, using mock response"
            )
    
    def test_invoke_llm_error_handling(self):
        """Test LLM invocation error handling."""
        agent = LLMOrchestratorAgent(llm_provider='mock')
        
        # Mock the entire try block to raise an exception before the fallback
        with patch.object(agent, 'llm_provider', 'invalid_provider'):
            with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
                response = agent.invoke_llm("Test prompt")
                
                # Should still return a response (fallback to mock)
                assert isinstance(response, str)
                assert "Mock LLM Analysis Results" in response
                # Should log the error
                mock_logger.error.assert_called()
    
    def test_analyze_code_with_context(self):
        """Test analyzing multiple code files with context."""
        agent = LLMOrchestratorAgent(llm_provider='mock')
        code_files = {
            'main.py': 'def main(): pass',
            'utils.py': 'def helper(): return True'
        }
        findings = [{'rule_id': 'TEST_RULE', 'message': 'Test finding'}]
        
        response = agent.analyze_code_with_context(code_files, findings)
        
        assert isinstance(response, str)
        assert "Mock LLM Analysis Results" in response
        # The response should be a valid mock response
        assert len(response) > 100
    
    def test_analyze_pr_diff(self):
        """Test analyzing PR diff."""
        agent = LLMOrchestratorAgent(llm_provider='mock')
        pr_diff = """
        diff --git a/test.py b/test.py
        +def new_function():
        +    print("Hello")
        """
        findings = [{'rule_id': 'PRINT_FOUND', 'category': 'logging'}]
        
        response = agent.analyze_pr_diff(pr_diff, findings)
        
        assert isinstance(response, str)
        assert "Mock LLM Analysis Results" in response
    
    def test_get_provider_info(self):
        """Test getting provider information."""
        agent = LLMOrchestratorAgent(
            llm_provider='openai', 
            api_key='test-key', 
            model_name='gpt-4'
        )
        
        info = agent.get_provider_info()
        
        assert info['provider'] == 'openai'
        assert info['model_name'] == 'gpt-4'
        assert info['has_api_key'] is True
        assert 'mock' in info['supported_providers']
    
    def test_get_provider_info_no_key(self):
        """Test getting provider information without API key."""
        agent = LLMOrchestratorAgent(llm_provider='local')
        
        info = agent.get_provider_info()
        
        assert info['provider'] == 'local'
        assert info['has_api_key'] is False
    
    def test_is_provider_available_mock(self):
        """Test provider availability check for mock."""
        agent = LLMOrchestratorAgent(llm_provider='mock')
        
        assert agent.is_provider_available() is True
    
    def test_is_provider_available_openai_with_key(self):
        """Test provider availability check for OpenAI with API key."""
        agent = LLMOrchestratorAgent(llm_provider='openai', api_key='test-key')
        
        assert agent.is_provider_available() is True
    
    def test_is_provider_available_openai_no_key(self):
        """Test provider availability check for OpenAI without API key."""
        agent = LLMOrchestratorAgent(llm_provider='openai')
        
        assert agent.is_provider_available() is False
    
    def test_is_provider_available_local(self):
        """Test provider availability check for local."""
        agent = LLMOrchestratorAgent(llm_provider='local')
        
        assert agent.is_provider_available() is True
    
    def test_is_provider_available_anthropic_with_key(self):
        """Test provider availability check for Anthropic with API key."""
        agent = LLMOrchestratorAgent(llm_provider='anthropic', api_key='test-key')
        
        assert agent.is_provider_available() is True
    
    def test_is_provider_available_anthropic_no_key(self):
        """Test provider availability check for Anthropic without API key."""
        agent = LLMOrchestratorAgent(llm_provider='anthropic')
        
        assert agent.is_provider_available() is False
    
    def test_is_provider_available_google_with_key(self):
        """Test provider availability check for Google with API key."""
        agent = LLMOrchestratorAgent(llm_provider='google', api_key='test-key')
        
        assert agent.is_provider_available() is True
    
    def test_is_provider_available_google_no_key(self):
        """Test provider availability check for Google without API key."""
        agent = LLMOrchestratorAgent(llm_provider='google')
        
        assert agent.is_provider_available() is False
    
    def test_mock_response_timestamp(self):
        """Test that mock response includes timestamp."""
        agent = LLMOrchestratorAgent(llm_provider='mock')
        
        response = agent._generate_mock_response("Test")
        
        # Should contain a timestamp in the summary
        assert "Mock analysis completed at" in response
        # Should contain current year
        current_year = datetime.now().year
        assert str(current_year) in response
    
    def test_mock_response_contextual_findings(self):
        """Test that mock response is contextual based on findings."""
        agent = LLMOrchestratorAgent(llm_provider='mock')
        
        # Test with no findings
        response_no_findings = agent._generate_mock_response("Test")
        assert "No specific security issues identified" in response_no_findings
        
        # Test with security findings
        security_findings = [{'rule_id': 'PDB_TRACE_FOUND', 'category': 'debugging'}]
        response_security = agent._generate_mock_response("Test", None, security_findings)
        assert "Security Alert" in response_security
        
        # Test with complexity findings
        complexity_findings = [{'rule_id': 'FUNCTION_TOO_LONG', 'category': 'complexity'}]
        response_complexity = agent._generate_mock_response("Test", None, complexity_findings)
        assert "Performance Concern" in response_complexity
    
    def test_mock_response_findings_limit(self):
        """Test that mock response limits displayed findings."""
        agent = LLMOrchestratorAgent(llm_provider='mock')
        
        # Create more than 3 findings
        findings = [
            {'rule_id': f'RULE_{i}', 'suggestion': f'Fix issue {i}'}
            for i in range(5)
        ]
        
        response = agent._generate_mock_response("Test", None, findings)
        
        assert "Based on 5 static analysis findings" in response
        assert "and 2 additional issues to address" in response
    
    def test_analyze_empty_code_files(self):
        """Test analyzing empty code files dictionary."""
        agent = LLMOrchestratorAgent(llm_provider='mock')
        
        response = agent.analyze_code_with_context({}, [])
        
        assert isinstance(response, str)
        assert "Mock LLM Analysis Results" in response 