"""
Unit tests for LLMOrchestratorAgent.

This module contains comprehensive tests for the LLMOrchestratorAgent class,
including tests for mock LLM behavior, OpenAI integration, Google Gemini integration,
prompt construction, and error handling.
"""

import pytest
import os
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
    
    def test_init_google_gemini_provider(self):
        """Test initialization with Google Gemini provider."""
        agent = LLMOrchestratorAgent(
            llm_provider='google_gemini', 
            api_key='test-key', 
            model_name='gemini-pro-vision'
        )
        
        assert agent.llm_provider == 'google_gemini'
        assert agent.model_name == 'gemini-pro-vision'
        assert agent.api_key == 'test-key'
    
    def test_init_legacy_google_provider(self):
        """Test initialization with legacy Google provider name."""
        with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
            agent = LLMOrchestratorAgent(
                llm_provider='google', 
                api_key='test-key'
            )
            
            assert agent.llm_provider == 'google_gemini'
            mock_logger.warning.assert_called_with("Provider 'google' is deprecated. Use 'google_gemini' instead.")
    
    def test_init_unsupported_provider(self):
        """Test initialization with unsupported provider."""
        with pytest.raises(ValueError, match="Unsupported LLM provider: invalid"):
            LLMOrchestratorAgent(llm_provider='invalid')
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatOpenAI')
    def test_init_openai_with_mock_instance(self, mock_chat_openai):
        """Test initialization with OpenAI provider using mocked ChatOpenAI."""
        mock_llm_instance = Mock()
        mock_chat_openai.return_value = mock_llm_instance
        
        agent = LLMOrchestratorAgent(
            llm_provider='openai', 
            api_key='test-key',
            model_name='gpt-4-turbo'
        )
        
        assert agent.llm_provider == 'openai'
        assert agent.model_name == 'gpt-4-turbo'
        assert agent.api_key == 'test-key'
        assert agent.llm_instance == mock_llm_instance
        
        # Verify ChatOpenAI was called with correct parameters
        mock_chat_openai.assert_called_once_with(
            model='gpt-4-turbo',
            api_key='test-key',
            temperature=0.1
        )
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatGoogleGenerativeAI')
    def test_init_google_gemini_with_mock_instance(self, mock_chat_google):
        """Test initialization with Google Gemini provider using mocked ChatGoogleGenerativeAI."""
        mock_llm_instance = Mock()
        mock_chat_google.return_value = mock_llm_instance
        
        agent = LLMOrchestratorAgent(
            llm_provider='google_gemini', 
            api_key='test-key',
            model_name='gemini-pro'
        )
        
        assert agent.llm_provider == 'google_gemini'
        assert agent.model_name == 'gemini-pro'
        assert agent.api_key == 'test-key'
        assert agent.llm_instance == mock_llm_instance
        
        # Verify ChatGoogleGenerativeAI was called with correct parameters
        mock_chat_google.assert_called_once_with(
            model='gemini-pro',
            google_api_key='test-key',
            temperature=0.1
        )
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatOpenAI', None)
    def test_init_openai_missing_dependency(self):
        """Test initialization with OpenAI provider when langchain-openai is not installed."""
        with pytest.raises(ImportError, match="langchain-openai is required for OpenAI provider"):
            LLMOrchestratorAgent(llm_provider='openai', api_key='test-key')
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatGoogleGenerativeAI', None)
    def test_init_google_gemini_missing_dependency(self):
        """Test initialization with Google Gemini provider when langchain-google-genai is not installed."""
        with pytest.raises(ImportError, match="langchain-google-genai is required for Google Gemini provider"):
            LLMOrchestratorAgent(llm_provider='google_gemini', api_key='test-key')
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatOpenAI')
    def test_init_openai_with_env_var(self, mock_chat_openai):
        """Test initialization with OpenAI provider using environment variable for API key."""
        mock_llm_instance = Mock()
        mock_chat_openai.return_value = mock_llm_instance
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'env-api-key'}):
            agent = LLMOrchestratorAgent(llm_provider='openai')
            
            assert agent.llm_provider == 'openai'
            assert agent.model_name == 'gpt-4'
            assert agent.llm_instance == mock_llm_instance
            
            # Verify ChatOpenAI was called with env API key
            mock_chat_openai.assert_called_once_with(
                model='gpt-4',
                api_key='env-api-key',
                temperature=0.1
            )
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatGoogleGenerativeAI')
    def test_init_google_gemini_with_env_var(self, mock_chat_google):
        """Test initialization with Google Gemini provider using environment variable for API key."""
        mock_llm_instance = Mock()
        mock_chat_google.return_value = mock_llm_instance
        
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'env-api-key'}):
            agent = LLMOrchestratorAgent(llm_provider='google_gemini')
            
            assert agent.llm_provider == 'google_gemini'
            assert agent.model_name == 'gemini-pro'
            assert agent.llm_instance == mock_llm_instance
            
            # Verify ChatGoogleGenerativeAI was called with env API key
            mock_chat_google.assert_called_once_with(
                model='gemini-pro',
                google_api_key='env-api-key',
                temperature=0.1
            )
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatOpenAI')
    def test_init_openai_initialization_error(self, mock_chat_openai):
        """Test initialization with OpenAI provider when ChatOpenAI initialization fails."""
        mock_chat_openai.side_effect = Exception("API initialization failed")
        
        with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
            agent = LLMOrchestratorAgent(llm_provider='openai', api_key='test-key')
            
            assert agent.llm_provider == 'openai'
            assert agent.llm_instance is None
            mock_logger.error.assert_called_with("Failed to initialize OpenAI LLM: API initialization failed")
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatGoogleGenerativeAI')
    def test_init_google_gemini_initialization_error(self, mock_chat_google):
        """Test initialization with Google Gemini provider when ChatGoogleGenerativeAI initialization fails."""
        mock_chat_google.side_effect = Exception("API initialization failed")
        
        with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
            agent = LLMOrchestratorAgent(llm_provider='google_gemini', api_key='test-key')
            
            assert agent.llm_provider == 'google_gemini'
            assert agent.llm_instance is None
            mock_logger.error.assert_called_with("Failed to initialize Google Gemini LLM: API initialization failed")
    
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
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatOpenAI')
    def test_invoke_llm_openai_with_llm_instance(self, mock_chat_openai):
        """Test LLM invocation with OpenAI provider using actual LLM instance."""
        # Setup mock LLM instance and response
        mock_llm_instance = Mock()
        mock_response = Mock()
        mock_response.content = "This is OpenAI's analysis of the code."
        mock_llm_instance.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm_instance
        
        agent = LLMOrchestratorAgent(llm_provider='openai', api_key='test-key')
        
        response = agent.invoke_llm("Analyze this code", "def test(): pass")
        
        assert response == "This is OpenAI's analysis of the code."
        assert mock_llm_instance.invoke.call_count == 1
        
        # Verify the prompt was constructed properly
        call_args = mock_llm_instance.invoke.call_args[0][0]
        assert "# Code Review Analysis Request" in call_args
        assert "Analyze this code" in call_args
        assert "def test(): pass" in call_args
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatGoogleGenerativeAI')
    def test_invoke_llm_google_gemini_with_llm_instance(self, mock_chat_google):
        """Test LLM invocation with Google Gemini provider using actual LLM instance."""
        # Setup mock LLM instance and response
        mock_llm_instance = Mock()
        mock_response = Mock()
        mock_response.content = "This is Google Gemini's analysis of the code."
        mock_llm_instance.invoke.return_value = mock_response
        mock_chat_google.return_value = mock_llm_instance
        
        agent = LLMOrchestratorAgent(llm_provider='google_gemini', api_key='test-key')
        
        response = agent.invoke_llm("Review this function", "def hello(): print('hi')")
        
        assert response == "This is Google Gemini's analysis of the code."
        assert mock_llm_instance.invoke.call_count == 1
        
        # Verify the prompt was constructed properly
        call_args = mock_llm_instance.invoke.call_args[0][0]
        assert "# Code Review Analysis Request" in call_args
        assert "Review this function" in call_args
        assert "def hello(): print('hi')" in call_args
    
    def test_invoke_llm_openai_no_instance(self):
        """Test LLM invocation with OpenAI provider when LLM instance is not available."""
        agent = LLMOrchestratorAgent(llm_provider='openai')
        agent.llm_instance = None  # Simulate failed initialization
        
        with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
            response = agent.invoke_llm("Test prompt")
            
            assert "Error: LLM instance not available for provider openai" in response
            mock_logger.error.assert_called_with("LLM instance not initialized for provider: openai")
    
    def test_invoke_llm_google_gemini_no_instance(self):
        """Test LLM invocation with Google Gemini provider when LLM instance is not available."""
        agent = LLMOrchestratorAgent(llm_provider='google_gemini')
        agent.llm_instance = None  # Simulate failed initialization
        
        with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
            response = agent.invoke_llm("Test prompt")
            
            assert "Error: LLM instance not available for provider google_gemini" in response
            mock_logger.error.assert_called_with("LLM instance not initialized for provider: google_gemini")
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatOpenAI')
    def test_invoke_llm_openai_api_error(self, mock_chat_openai):
        """Test LLM invocation with OpenAI provider when API call fails."""
        # Setup mock LLM instance that raises an error
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.side_effect = Exception("API rate limit exceeded")
        mock_chat_openai.return_value = mock_llm_instance
        
        agent = LLMOrchestratorAgent(llm_provider='openai', api_key='test-key')
        
        with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
            response = agent.invoke_llm("Test prompt")
            
            assert "Error calling openai API: API rate limit exceeded" in response
            mock_logger.error.assert_called_with("Error calling openai API: API rate limit exceeded")
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatGoogleGenerativeAI')
    def test_invoke_llm_google_gemini_api_error(self, mock_chat_google):
        """Test LLM invocation with Google Gemini provider when API call fails."""
        # Setup mock LLM instance that raises an error
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.side_effect = Exception("Quota exceeded")
        mock_chat_google.return_value = mock_llm_instance
        
        agent = LLMOrchestratorAgent(llm_provider='google_gemini', api_key='test-key')
        
        with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
            response = agent.invoke_llm("Test prompt")
            
            assert "Error calling google_gemini API: Quota exceeded" in response
            mock_logger.error.assert_called_with("Error calling google_gemini API: Quota exceeded")
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatOpenAI')
    def test_invoke_llm_openai_response_without_content(self, mock_chat_openai):
        """Test LLM invocation with OpenAI provider when response doesn't have content attribute."""
        # Setup mock LLM instance that returns a response without content attribute
        mock_llm_instance = Mock()
        mock_response = "Raw response string"
        mock_llm_instance.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm_instance
        
        agent = LLMOrchestratorAgent(llm_provider='openai', api_key='test-key')
        
        response = agent.invoke_llm("Test prompt")
        
        assert response == "Raw response string"
        assert mock_llm_instance.invoke.call_count == 1
    
    def test_invoke_llm_local_fallback(self):
        """Test LLM invocation with local provider when no instance available."""
        agent = LLMOrchestratorAgent(llm_provider='local')
        
        with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
            response = agent.invoke_llm("Test prompt")
            
            assert "Error: LLM instance not available for provider local" in response
            mock_logger.error.assert_called_with("LLM instance not initialized for provider: local")
    
    def test_invoke_llm_anthropic_fallback(self):
        """Test LLM invocation with Anthropic provider when no instance available."""
        agent = LLMOrchestratorAgent(llm_provider='anthropic', api_key='test-key')
        
        with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
            response = agent.invoke_llm("Test prompt")
            
            assert "Error: LLM instance not available for provider anthropic" in response
            mock_logger.error.assert_called_with("LLM instance not initialized for provider: anthropic")
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatGoogleGenerativeAI')
    def test_invoke_llm_legacy_google_provider(self, mock_chat_google):
        """Test LLM invocation with legacy 'google' provider name."""
        # Setup mock LLM instance and response
        mock_llm_instance = Mock()
        mock_response = Mock()
        mock_response.content = "Analysis from Google Gemini"
        mock_llm_instance.invoke.return_value = mock_response
        mock_chat_google.return_value = mock_llm_instance
        
        with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
            agent = LLMOrchestratorAgent(llm_provider='google', api_key='test-key')
            response = agent.invoke_llm("Test prompt")
            
            # Should redirect to google_gemini and work properly
            assert response == "Analysis from Google Gemini"
            assert agent.llm_provider == 'google_gemini'
            mock_logger.warning.assert_called_with("Provider 'google' is deprecated. Use 'google_gemini' instead.")
    
    def test_invoke_llm_error_handling(self):
        """Test LLM invocation error handling."""
        agent = LLMOrchestratorAgent(llm_provider='mock')
        
        # Mock the entire try block to raise an exception before the fallback
        with patch.object(agent, 'llm_provider', 'invalid_provider'):
            with patch('src.core_engine.agents.llm_orchestrator_agent.logger') as mock_logger:
                response = agent.invoke_llm("Test prompt")
                
                # Should return an error message since no mock fallback for invalid providers
                assert isinstance(response, str)
                assert "Error: LLM instance not available for provider invalid_provider" in response
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
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatOpenAI')
    def test_is_provider_available_openai_with_key(self, mock_chat_openai):
        """Test provider availability check for OpenAI with API key."""
        mock_chat_openai.return_value = Mock()
        agent = LLMOrchestratorAgent(llm_provider='openai', api_key='test-key')
        
        assert agent.is_provider_available() is True
    
    def test_is_provider_available_openai_no_key(self):
        """Test provider availability check for OpenAI without API key."""
        agent = LLMOrchestratorAgent(llm_provider='openai')
        agent.llm_instance = None  # Simulate failed initialization
        
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
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatGoogleGenerativeAI')
    def test_is_provider_available_google_gemini_with_key(self, mock_chat_google):
        """Test provider availability check for Google Gemini with API key."""
        mock_chat_google.return_value = Mock()
        agent = LLMOrchestratorAgent(llm_provider='google_gemini', api_key='test-key')
        
        assert agent.is_provider_available() is True
    
    def test_is_provider_available_google_gemini_no_key(self):
        """Test provider availability check for Google Gemini without API key."""
        agent = LLMOrchestratorAgent(llm_provider='google_gemini')
        agent.llm_instance = None  # Simulate failed initialization
        
        assert agent.is_provider_available() is False
    
    @patch('src.core_engine.agents.llm_orchestrator_agent.ChatGoogleGenerativeAI')
    def test_is_provider_available_google_gemini_with_instance(self, mock_chat_google):
        """Test provider availability check for Google Gemini with successful instance creation."""
        mock_chat_google.return_value = Mock()
        agent = LLMOrchestratorAgent(llm_provider='google_gemini')
        # Even without API key, if instance is available, provider is available
        assert agent.is_provider_available() is True
    
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
        
        # When no files are provided, the response should be empty string
        assert isinstance(response, str)
        assert response == "" 