"""
LLMOrchestratorAgent for AI Code Review System.

This module implements the LLMOrchestratorAgent responsible for managing
interactions with Large Language Models (LLMs) for semantic code analysis.
Supports mock LLM behavior, OpenAI GPT models, and Google Gemini models.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

from .rag_context_agent import RAGContextAgent

# Configure logging
logger = logging.getLogger(__name__)


class LLMOrchestratorAgent:
    """
    Agent responsible for orchestrating LLM interactions for code analysis.
    
    This agent handles:
    - Managing LLM provider configurations (mock, OpenAI, local models, etc.)
    - Constructing prompts for code analysis
    - Invoking LLM APIs and handling responses
    - Processing and structuring LLM outputs
    - Error handling and fallback mechanisms
    """
    
    def __init__(self, llm_provider: str = 'mock', api_key: str = None, model_name: str = None,
                 use_rag: bool = False):
        """
        Initialize the LLMOrchestratorAgent.
        
        Args:
            llm_provider (str): LLM provider type ('mock', 'openai', 'google_gemini', 'local', etc.)
            api_key (str): API key for commercial LLM providers (if needed)
            model_name (str): Specific model name to use
            use_rag (bool): Whether to use RAG for context enhancement
        """
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.model_name = model_name
        self.supported_providers = ['mock', 'openai', 'google_gemini', 'local', 'anthropic', 'google']
        
        # Initialize RAG context agent if enabled
        self.use_rag = use_rag
        self.rag_agent = RAGContextAgent() if use_rag else None
        
        # Initialize LLM instance
        self.llm_instance = None
        
        # Initialize provider-specific configurations
        self._initialize_provider()
        
        logger.info(f"LLMOrchestratorAgent initialized with provider: {llm_provider}, RAG: {use_rag}")
    
    def _initialize_provider(self) -> None:
        """
        Initialize provider-specific configurations and validate settings.
        
        Raises:
            ValueError: If provider is not supported or configuration is invalid
        """
        if self.llm_provider not in self.supported_providers:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}. "
                           f"Supported providers: {self.supported_providers}")
        
        if self.llm_provider == 'mock':
            # Mock provider setup
            self.model_name = self.model_name or 'mock-gpt-4'
            logger.info("Initialized mock LLM provider for testing")
            
        elif self.llm_provider == 'openai':
            # OpenAI provider setup
            if ChatOpenAI is None:
                raise ImportError("langchain-openai is required for OpenAI provider. Install with: pip install langchain-openai")
            
            # Get API key from parameter or environment variable
            api_key = self.api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.warning("OpenAI API key not provided. LLM calls will fail.")
                
            self.model_name = self.model_name or 'gpt-4'
            
            # Initialize OpenAI LLM instance
            try:
                self.llm_instance = ChatOpenAI(
                    model=self.model_name,
                    api_key=api_key,
                    temperature=0.1  # Lower temperature for more consistent code analysis
                )
                logger.info(f"Initialized OpenAI provider with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI LLM: {str(e)}")
                self.llm_instance = None
            
        elif self.llm_provider == 'local':
            # Local model setup (placeholder for future implementation)
            self.model_name = self.model_name or 'local-code-llama'
            logger.info(f"Initialized local LLM provider with model: {self.model_name}")
            
        elif self.llm_provider == 'anthropic':
            # Anthropic Claude setup (placeholder for future implementation)
            if not self.api_key:
                logger.warning("Anthropic API key not provided. LLM calls will fail.")
            self.model_name = self.model_name or 'claude-3-sonnet'
            logger.info(f"Initialized Anthropic provider with model: {self.model_name}")
            
        elif self.llm_provider == 'google_gemini':
            # Google Gemini provider setup
            if ChatGoogleGenerativeAI is None:
                raise ImportError("langchain-google-genai is required for Google Gemini provider. Install with: pip install langchain-google-genai")
            
            # Get API key from parameter or environment variable
            api_key = self.api_key or os.getenv('GOOGLE_API_KEY')
            if not api_key:
                logger.warning("Google API key not provided. LLM calls will fail.")
                
            self.model_name = self.model_name or 'gemini-pro'
            
            # Initialize Google Gemini LLM instance
            try:
                self.llm_instance = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=api_key,
                    temperature=0.1  # Lower temperature for more consistent code analysis
                )
                logger.info(f"Initialized Google Gemini provider with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Google Gemini LLM: {str(e)}")
                self.llm_instance = None
        
        elif self.llm_provider == 'google':
            # Legacy Google provider name - redirect to google_gemini
            logger.warning("Provider 'google' is deprecated. Use 'google_gemini' instead.")
            self.llm_provider = 'google_gemini'
            self._initialize_provider()  # Re-initialize with correct provider
    
    def _construct_analysis_prompt(self, prompt: str, code_snippet: str = None, 
                                 static_findings: List[Dict] = None,
                                 rag_context: List[Dict] = None) -> str:
        """
        Construct a comprehensive prompt for code analysis.
        
        Args:
            prompt (str): Base prompt or analysis request
            code_snippet (str): Code to analyze (optional)
            static_findings (List[Dict]): Static analysis findings (optional)
            rag_context (List[Dict]): Retrieved context from RAG (optional)
            
        Returns:
            str: Constructed prompt for LLM analysis
        """
        full_prompt = f"# Code Review Analysis Request\n\n{prompt}\n\n"
        
        # Add code snippet if provided
        if code_snippet:
            full_prompt += f"## Code to Analyze:\n```python\n{code_snippet}\n```\n\n"
        
        # Add RAG context if available
        if rag_context:
            full_prompt += "## Relevant Code Context:\n"
            for i, ctx in enumerate(rag_context, 1):
                full_prompt += f"### Context {i} (from {ctx['file_path']}, score: {ctx['score']:.2f}):\n"
                full_prompt += f"```python\n{ctx['content']}\n```\n\n"
        
        # Add static analysis findings if provided
        if static_findings:
            full_prompt += "## Static Analysis Findings:\n"
            for i, finding in enumerate(static_findings, 1):
                full_prompt += f"{i}. **{finding.get('rule_id', 'Unknown')}** "
                full_prompt += f"(Line {finding.get('line', 'N/A')}): "
                full_prompt += f"{finding.get('message', 'No message')}\n"
                if finding.get('suggestion'):
                    full_prompt += f"   - Suggestion: {finding['suggestion']}\n"
            full_prompt += "\n"
        
        # Add analysis instructions
        full_prompt += """## Analysis Instructions:
Please provide a comprehensive code review analysis including:

1. **Code Quality Assessment**: Overall structure, readability, maintainability
2. **Security Considerations**: Potential vulnerabilities or security issues
3. **Performance Analysis**: Efficiency concerns and optimization opportunities
4. **Best Practices**: Adherence to coding standards and conventions
5. **Architectural Insights**: Design patterns and structural recommendations
6. **Specific Recommendations**: Actionable suggestions for improvement

Consider both the code being analyzed and any provided context from the codebase.
Please format your response in clear sections and provide specific, actionable feedback.
"""
        
        return full_prompt
    
    def _generate_mock_response(self, prompt: str, code_snippet: str = None, 
                              static_findings: List[Dict] = None,
                              rag_context: List[Dict] = None) -> str:
        """
        Generate a mock LLM response for testing purposes.
        
        Args:
            prompt (str): Analysis prompt
            code_snippet (str): Code snippet being analyzed
            static_findings (List[Dict]): Static analysis findings
            rag_context (List[Dict]): Retrieved context from RAG
            
        Returns:
            str: Mock LLM response
        """
        # Analyze the inputs to generate contextual mock responses
        has_code = code_snippet is not None
        has_findings = static_findings and len(static_findings) > 0
        has_rag = rag_context and len(rag_context) > 0
        findings_count = len(static_findings) if static_findings else 0
        
        # Generate contextual mock response
        mock_response = f"""# Mock LLM Analysis Results

## Code Quality Assessment
"""
        
        if has_code:
            # Extract function/class names from code snippet
            code_elements = []
            if 'def ' in code_snippet:
                for line in code_snippet.split('\n'):
                    if 'def ' in line:
                        func_name = line.split('def ')[1].split('(')[0]
                        code_elements.append(func_name)
            elif 'class ' in code_snippet:
                for line in code_snippet.split('\n'):
                    if 'class ' in line:
                        class_name = line.split('class ')[1].split(':')[0]
                        code_elements.append(class_name)
            
            mock_response += """- The code structure appears well-organized with clear function definitions
- Variable naming follows Python conventions and is descriptive
- Code readability is good with appropriate spacing and indentation
"""
            # Include analyzed code elements
            if code_elements:
                mock_response += f"- Analyzed elements: {', '.join(code_elements)}\n"
        else:
            mock_response += """- Unable to assess code structure without specific code snippets
- Recommend providing code samples for detailed analysis
"""
        
        mock_response += "\n## Security Considerations\n"
        
        if has_findings:
            # Check for security-related findings
            security_findings = [f for f in static_findings if 'pdb' in f.get('rule_id', '').lower() 
                               or 'debug' in f.get('category', '').lower()]
            if security_findings:
                mock_response += "- **Security Alert**: Debugging statements detected that should not be in production\n"
                mock_response += "- Remove all pdb.set_trace() calls before deployment\n"
            else:
                mock_response += "- No obvious security vulnerabilities detected in static analysis\n"
        else:
            mock_response += "- No specific security issues identified\n"
        
        mock_response += "- Recommend implementing input validation for user-facing functions\n"
        mock_response += "- Consider adding authentication and authorization checks where appropriate\n\n"
        
        mock_response += "## Performance Analysis\n"
        
        if has_findings:
            # Check for complexity-related findings
            complexity_findings = [f for f in static_findings if 'complexity' in f.get('category', '').lower()]
            if complexity_findings:
                mock_response += f"- **Performance Concern**: {len(complexity_findings)} complexity issues detected\n"
                mock_response += "- Large functions/classes may impact performance and maintainability\n"
                mock_response += "- Consider refactoring into smaller, more focused components\n"
            else:
                mock_response += "- Code complexity appears manageable\n"
        else:
            mock_response += "- No specific performance issues identified\n"
        
        mock_response += "- Consider implementing caching for frequently accessed data\n"
        mock_response += "- Review database queries for optimization opportunities\n\n"
        
        mock_response += "## Best Practices\n"
        
        if has_findings:
            # Check for logging-related findings
            logging_findings = [f for f in static_findings if 'logging' in f.get('category', '').lower()]
            if logging_findings:
                mock_response += f"- **Logging Issue**: {len(logging_findings)} print statements detected\n"
                mock_response += "- Replace print() statements with proper logging (logger.info, logger.debug)\n"
                mock_response += "- Implement structured logging with appropriate log levels\n"
            
            # Check for import-related findings
            import_findings = [f for f in static_findings if 'import' in f.get('category', '').lower()]
            if import_findings:
                mock_response += f"- **Import Optimization**: {len(import_findings)} potentially unused imports\n"
                mock_response += "- Clean up unused imports to improve code clarity\n"
        
        mock_response += "- Follow PEP 8 style guidelines consistently\n"
        mock_response += "- Add comprehensive docstrings for all public functions and classes\n"
        mock_response += "- Implement proper error handling with specific exception types\n\n"
        
        # Add RAG context analysis if available
        if has_rag:
            mock_response += "## Related Code Context Analysis\n"
            for ctx in rag_context:
                mock_response += f"- Found related code in {ctx['file_path']} (similarity: {ctx['score']:.2f}):\n"
                mock_response += f"```python\n{ctx['content']}\n```\n"
                # Extract function/class names from context
                if 'def ' in ctx['content']:
                    func_name = ctx['content'].split('def ')[1].split('(')[0]
                    mock_response += f"  - Related function: {func_name}\n"
                elif 'class ' in ctx['content']:
                    class_name = ctx['content'].split('class ')[1].split(':')[0]
                    mock_response += f"  - Related class: {class_name}\n"
        
        mock_response += "\n## Architectural Insights\n"
        mock_response += "- Consider implementing dependency injection for better testability\n"
        mock_response += "- Separate business logic from presentation concerns\n"
        mock_response += "- Use design patterns (Strategy, Factory) where appropriate\n"
        mock_response += "- Consider implementing interfaces for better abstraction\n\n"
        
        mock_response += "## Specific Recommendations\n"
        
        if has_findings:
            mock_response += f"Based on {findings_count} static analysis findings:\n\n"
            for i, finding in enumerate(static_findings[:3], 1):  # Show top 3 findings
                mock_response += f"{i}. **{finding.get('rule_id', 'Issue')}**: "
                mock_response += f"{finding.get('suggestion', 'Review and fix this issue')}\n"
            
            if findings_count > 3:
                mock_response += f"... and {findings_count - 3} additional issues to address\n"
        else:
            mock_response += "1. Add comprehensive unit tests for all functions\n"
            mock_response += "2. Implement continuous integration and automated testing\n"
            mock_response += "3. Add type hints for better code documentation\n"
        
        mock_response += "\n## Summary\n"
        mock_response += f"Mock analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. "
        
        if has_findings:
            mock_response += f"Identified {findings_count} areas for improvement. "
        
        mock_response += "This is a simulated response for testing purposes. "
        mock_response += "Real LLM integration will provide more detailed and context-aware analysis."
        
        return mock_response
    
    def invoke_llm(self, prompt: str, code_snippet: str = None, 
                   static_findings: List[Dict] = None) -> str:
        """
        Invoke the LLM with a constructed prompt and return the response.
        
        Args:
            prompt (str): Base prompt or analysis request
            code_snippet (str): Code to analyze (optional)
            static_findings (List[Dict]): Static analysis findings (optional)
            
        Returns:
            str: LLM response with analysis
        """
        try:
            # Get RAG context if enabled
            rag_context = None
            if self.use_rag and code_snippet:
                try:
                    rag_context = self.rag_agent.query_knowledge_base(code_snippet)
                except Exception as e:
                    logger.warning(f"Failed to get RAG context: {str(e)}")
            
            # Construct full prompt
            full_prompt = self._construct_analysis_prompt(
                prompt=prompt,
                code_snippet=code_snippet,
                static_findings=static_findings,
                rag_context=rag_context
            )
            
            # For mock provider, use mock response
            if self.llm_provider == 'mock':
                return self._generate_mock_response(
                    prompt=prompt,
                    code_snippet=code_snippet,
                    static_findings=static_findings,
                    rag_context=rag_context
                )
            
            # For real LLM providers, use the LangChain instance
            if self.llm_instance is None:
                logger.error(f"LLM instance not initialized for provider: {self.llm_provider}")
                return f"Error: LLM instance not available for provider {self.llm_provider}"
            
            try:
                # Use LangChain LLM instance to invoke the model
                response = self.llm_instance.invoke(full_prompt)
                
                # Extract content from response
                if hasattr(response, 'content'):
                    return response.content
                else:
                    return str(response)
                    
            except Exception as e:
                logger.error(f"Error calling {self.llm_provider} API: {str(e)}")
                return f"Error calling {self.llm_provider} API: {str(e)}"
            
        except Exception as e:
            logger.error(f"Error invoking LLM: {str(e)}")
            return f"Error analyzing code: {str(e)}"
    
    def analyze_code_with_context(self, code_files: Dict[str, str], 
                                static_findings: List[Dict] = None) -> str:
        """
        Analyze multiple code files with their context.
        
        Args:
            code_files (Dict[str, str]): Dictionary mapping file paths to code content
            static_findings (List[Dict]): Static analysis findings (optional)
            
        Returns:
            str: LLM analysis of the code files
        """
        try:
            # Build RAG knowledge base if enabled
            if self.use_rag:
                try:
                    self.rag_agent.build_knowledge_base(code_files)
                except Exception as e:
                    logger.warning(f"Failed to build RAG knowledge base: {str(e)}")
            
            # Analyze each file
            analyses = []
            for file_path, code in code_files.items():
                file_findings = [f for f in (static_findings or []) 
                               if f.get('file_path') == file_path]
                
                analysis = self.invoke_llm(
                    prompt=f"Analyze code file: {file_path}",
                    code_snippet=code,
                    static_findings=file_findings
                )
                analyses.append(f"# Analysis for {file_path}\n\n{analysis}")
            
            return "\n\n".join(analyses)
            
        except Exception as e:
            logger.error(f"Error analyzing code files: {str(e)}")
            return f"Error analyzing code files: {str(e)}"
    
    def analyze_pr_diff(self, pr_diff: str, static_findings: List[Dict] = None) -> str:
        """
        Analyze a Pull Request diff.
        
        Args:
            pr_diff (str): PR diff content
            static_findings (List[Dict]): Static analysis findings for the PR
            
        Returns:
            str: LLM analysis of the PR changes
        """
        logger.info("Analyzing PR diff with LLM")
        
        prompt = ("Please analyze the following Pull Request diff and provide insights on "
                 "the changes, potential issues, and recommendations:")
        
        return self.invoke_llm(prompt, pr_diff, static_findings)
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the current LLM provider configuration.
        
        Returns:
            Dict[str, Any]: Provider configuration information
        """
        return {
            "provider": self.llm_provider,
            "model_name": self.model_name,
            "has_api_key": self.api_key is not None,
            "supported_providers": self.supported_providers
        }
    
    def is_provider_available(self) -> bool:
        """
        Check if the current LLM provider is available and properly configured.
        
        Returns:
            bool: True if provider is available, False otherwise
        """
        if self.llm_provider == 'mock':
            return True
        elif self.llm_provider in ['openai', 'anthropic', 'google_gemini']:
            return self.api_key is not None or self.llm_instance is not None
        elif self.llm_provider == 'local':
            # TODO: Add actual local model availability check
            return True
        else:
            return False 