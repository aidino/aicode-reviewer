"""
SolutionSuggestionAgent for AI Code Review System.

This module implements the SolutionSuggestionAgent responsible for refining
LLM outputs into specific, actionable code suggestions and solutions.
"""

import logging
import re
from typing import Dict, Optional, Any
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class SolutionSuggestionAgent:
    """
    Agent responsible for refining LLM outputs into actionable solutions.
    
    This agent takes findings from static analysis and initial LLM insights,
    then uses the LLM to generate specific, implementable code suggestions
    with clear explanations of why changes are needed.
    """
    
    def __init__(self, llm_orchestrator=None):
        """
        Initialize the SolutionSuggestionAgent.
        
        Args:
            llm_orchestrator: Optional LLMOrchestratorAgent instance to use.
                            If None, expects one to be passed to methods.
        """
        self.llm_orchestrator = llm_orchestrator
        logger.info("SolutionSuggestionAgent initialized")
    
    def _construct_solution_prompt(self, finding: Dict, code_snippet: str) -> str:
        """
        Construct a specific prompt for generating actionable solutions.
        
        Args:
            finding (Dict): Static analysis finding or LLM insight
            code_snippet (str): Relevant code snippet
            
        Returns:
            str: Constructed prompt for solution generation
        """
        rule_id = finding.get('rule_id', 'Unknown Issue')
        message = finding.get('message', 'No description available')
        line = finding.get('line', 'Unknown')
        category = finding.get('category', 'general')
        severity = finding.get('severity', 'medium')
        
        prompt = f"""# Code Issue Solution Request

## Issue Details
- **Rule ID**: {rule_id}
- **Category**: {category}
- **Severity**: {severity}
- **Line**: {line}
- **Description**: {message}

## Code to Analyze
```python
{code_snippet}
```

## Task with XAI Requirements
Please provide a detailed solution for this code issue with EXPLAINABLE AI requirements:

CRITICAL: You MUST include for every recommendation:
- **Reasoning**: WHY this solution is recommended
- **Confidence**: Numerical confidence score 0.0-1.0
- **Evidence**: Specific code patterns or principles supporting this solution
- **Alternatives**: Other possible approaches if confidence < 0.8

Your response should include:
1. **WHY**: Explain clearly why this is an issue and what problems it could cause
2. **WHAT**: Describe exactly what needs to be changed
3. **HOW**: Provide specific, actionable code changes or suggestions
4. **BEST_PRACTICE**: Include any relevant best practices or patterns

## Response Format
Please structure your response as follows:

### Explanation
[Clear explanation of why this is an issue]
**Reasoning:** [Why you identified this as problematic]
**Confidence:** [0.0-1.0]
**Evidence:** [Specific patterns or violations observed]

### Impact
[What problems this could cause if not fixed]
**Reasoning:** [Why these consequences would occur]
**Confidence:** [0.0-1.0]
**Evidence:** [Supporting principles or examples]

### Solution
[Specific steps to fix the issue]
**Reasoning:** [Why this approach is best]
**Confidence:** [0.0-1.0]
**Evidence:** [Best practices or patterns supporting this solution]
**Alternatives:** [Other viable approaches if confidence < 0.8]

### Suggested Code
```python
[Provide the corrected code or specific changes]
```
**Reasoning:** [Why this specific code change]
**Confidence:** [0.0-1.0]

### Best Practices
[Additional recommendations and best practices]
**Reasoning:** [Why these practices are important]
**Confidence:** [0.0-1.0]

Focus on being specific and actionable. INCLUDE reasoning and confidence for ALL suggestions.
"""
        
        return prompt
    
    def _parse_llm_response(self, llm_response: str) -> Dict[str, str]:
        """
        Parse LLM response into structured components with XAI data.
        
        Args:
            llm_response (str): Raw LLM response
            
        Returns:
            Dict[str, str]: Parsed response components including reasoning and confidence
        """
        parsed = {
            'explanation': '',
            'impact': '',
            'solution': '',
            'suggested_code': '',
            'best_practices': '',
            'reasoning': '',
            'confidence_scores': {},
            'evidence': '',
            'alternatives': '',
            'raw_response': llm_response
        }
        
        try:
            # Extract sections using regex patterns
            sections = {
                'explanation': r'### Explanation\s*\n(.*?)(?=###|\Z)',
                'impact': r'### Impact\s*\n(.*?)(?=###|\Z)',
                'solution': r'### Solution\s*\n(.*?)(?=###|\Z)',
                'best_practices': r'### Best Practices\s*\n(.*?)(?=###|\Z)'
            }
            
            for key, pattern in sections.items():
                match = re.search(pattern, llm_response, re.DOTALL | re.IGNORECASE)
                if match:
                    parsed[key] = match.group(1).strip()
            
            # Extract suggested code from code blocks
            code_pattern = r'```python\s*\n(.*?)```'
            code_matches = re.findall(code_pattern, llm_response, re.DOTALL)
            if code_matches:
                # Take the last code block as the suggested code
                parsed['suggested_code'] = code_matches[-1].strip()
            
            # Extract XAI specific elements
            # Extract confidence scores
            confidence_pattern = r'\*\*Confidence:\*\*\s*(\d+\.?\d*)'
            confidence_matches = re.findall(confidence_pattern, llm_response, re.IGNORECASE)
            if confidence_matches:
                parsed['confidence_scores'] = {
                    'overall': float(confidence_matches[0]) if confidence_matches else 0.5,
                    'all_scores': [float(score) for score in confidence_matches]
                }
            
            # Extract reasoning
            reasoning_pattern = r'\*\*Reasoning:\*\*\s*(.*?)(?=\*\*|\n\n|\Z)'
            reasoning_matches = re.findall(reasoning_pattern, llm_response, re.DOTALL | re.IGNORECASE)
            if reasoning_matches:
                parsed['reasoning'] = ' | '.join(match.strip() for match in reasoning_matches)
            
            # Extract evidence
            evidence_pattern = r'\*\*Evidence:\*\*\s*(.*?)(?=\*\*|\n\n|\Z)'
            evidence_matches = re.findall(evidence_pattern, llm_response, re.DOTALL | re.IGNORECASE)
            if evidence_matches:
                parsed['evidence'] = ' | '.join(match.strip() for match in evidence_matches)
            
            # Extract alternatives
            alternatives_pattern = r'\*\*Alternatives:\*\*\s*(.*?)(?=\*\*|\n\n|\Z)'
            alternatives_matches = re.findall(alternatives_pattern, llm_response, re.DOTALL | re.IGNORECASE)
            if alternatives_matches:
                parsed['alternatives'] = ' | '.join(match.strip() for match in alternatives_matches)
            
            # If no structured sections found, try to extract basic content
            if not any(parsed[key] for key in ['explanation', 'solution']):
                # Fallback: use the entire response as explanation
                parsed['explanation'] = llm_response.strip()
                
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            parsed['explanation'] = llm_response.strip()
        
        return parsed
    
    def refine_llm_solution(self, finding: Dict, code_snippet: str, 
                          llm_orchestrator=None) -> Dict:
        """
        Refine a finding into a specific, actionable solution using LLM.
        
        Args:
            finding (Dict): Static analysis finding or initial insight
            code_snippet (str): Relevant code snippet to analyze
            llm_orchestrator: LLMOrchestratorAgent instance to use
            
        Returns:
            Dict: Refined solution with explanation and suggested code
        """
        # Use provided orchestrator or instance variable
        orchestrator = llm_orchestrator or self.llm_orchestrator
        if not orchestrator:
            raise ValueError("No LLMOrchestratorAgent provided")
        
        try:
            # Construct specific prompt for solution generation
            prompt = self._construct_solution_prompt(finding, code_snippet)
            
            logger.info(f"Generating solution for finding: {finding.get('rule_id', 'Unknown')}")
            
            # Get LLM response
            llm_response = orchestrator.invoke_llm(
                prompt="Generate specific solution for code issue",
                code_snippet=prompt  # Pass the full prompt as code_snippet
            )
            
            # Parse response into structured format
            parsed_solution = self._parse_llm_response(llm_response)
            
            # Add metadata with XAI data
            solution = {
                'finding_id': finding.get('rule_id', 'unknown'),
                'category': finding.get('category', 'general'),
                'severity': finding.get('severity', 'medium'),
                'line': finding.get('line'),
                'original_message': finding.get('message', ''),
                'explanation': parsed_solution['explanation'],
                'impact': parsed_solution['impact'],
                'solution_steps': parsed_solution['solution'],
                'suggested_code': parsed_solution['suggested_code'],
                'best_practices': parsed_solution['best_practices'],
                # XAI specific fields
                'xai_reasoning': parsed_solution['reasoning'],
                'xai_confidence_scores': parsed_solution['confidence_scores'],
                'xai_evidence': parsed_solution['evidence'],
                'xai_alternatives': parsed_solution['alternatives'],
                'confidence': parsed_solution['confidence_scores'].get('overall', 0.7) if parsed_solution['confidence_scores'] else 0.7,
                'generated_at': datetime.now().isoformat(),
                'raw_llm_response': parsed_solution['raw_response']
            }
            
            logger.info(f"Successfully generated solution for {finding.get('rule_id', 'Unknown')}")
            return solution
            
        except Exception as e:
            logger.error(f"Error refining solution: {str(e)}")
            
            # Return fallback solution
            return {
                'finding_id': finding.get('rule_id', 'unknown'),
                'category': finding.get('category', 'general'),
                'severity': finding.get('severity', 'medium'),
                'line': finding.get('line'),
                'original_message': finding.get('message', ''),
                'explanation': f"Unable to generate detailed solution: {str(e)}",
                'impact': 'Could not determine impact',
                'solution_steps': 'Manual review required',
                'suggested_code': '',
                'best_practices': '',
                'confidence': 'low',
                'generated_at': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def refine_multiple_solutions(self, findings: list, code_files: Dict[str, str],
                                llm_orchestrator=None) -> list:
        """
        Refine multiple findings into actionable solutions.
        
        Args:
            findings (list): List of static analysis findings
            code_files (Dict[str, str]): Dictionary of file paths to code content
            llm_orchestrator: LLMOrchestratorAgent instance to use
            
        Returns:
            list: List of refined solutions
        """
        solutions = []
        
        for finding in findings:
            try:
                # Get relevant code snippet
                file_path = finding.get('file_path', '')
                line_number = finding.get('line', 1)
                
                if file_path in code_files:
                    code_lines = code_files[file_path].split('\n')
                    # Get context around the issue (5 lines before and after)
                    start_line = max(0, line_number - 5)
                    end_line = min(len(code_lines), line_number + 5)
                    code_snippet = '\n'.join(code_lines[start_line:end_line])
                else:
                    code_snippet = "# Code snippet not available"
                
                # Generate solution
                solution = self.refine_llm_solution(
                    finding=finding,
                    code_snippet=code_snippet,
                    llm_orchestrator=llm_orchestrator
                )
                
                solutions.append(solution)
                
            except Exception as e:
                logger.error(f"Error processing finding {finding.get('rule_id', 'Unknown')}: {str(e)}")
                # Add error solution
                solutions.append({
                    'finding_id': finding.get('rule_id', 'unknown'),
                    'error': str(e),
                    'generated_at': datetime.now().isoformat()
                })
        
        logger.info(f"Generated {len(solutions)} solutions from {len(findings)} findings")
        return solutions
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the agent configuration.
        
        Returns:
            Dict[str, Any]: Agent information
        """
        return {
            'agent_name': 'SolutionSuggestionAgent',
            'version': '1.0.0',
            'has_llm_orchestrator': self.llm_orchestrator is not None,
            'capabilities': [
                'solution_refinement',
                'code_suggestion',
                'explanation_generation',
                'best_practice_recommendations'
            ]
        } 