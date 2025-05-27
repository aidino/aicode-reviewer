"""
Enhanced SolutionSuggestionAgent for AI Code Review System.

This module implements an enhanced version of SolutionSuggestionAgent with:
- Explainable AI (XAI) capabilities with reasoning and evidence
- Multiple solution alternatives with pros/cons analysis  
- Advanced confidence scoring and evidence tracking
- Comprehensive error handling and recovery
- Diverse suggestion types and better prompt engineering
"""

import logging
import re
import uuid
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .models.solution_suggestion_models import (
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

# Configure logging
logger = logging.getLogger(__name__)


class EnhancedSolutionSuggestionAgent:
    """
    Enhanced agent for generating actionable, explainable code solutions.
    
    This agent provides:
    - Multiple solution alternatives with detailed reasoning
    - Explainable AI with confidence scoring and evidence
    - Comprehensive error handling and fallback strategies
    - Diverse suggestion types (security, performance, best practices, etc.)
    - Rich metadata and analytics for continuous improvement
    """
    
    def __init__(self, llm_orchestrator=None, enable_alternatives: bool = True, 
                 max_alternatives: int = 3, confidence_threshold: float = 0.6):
        """
        Initialize the EnhancedSolutionSuggestionAgent.
        
        Args:
            llm_orchestrator: Optional LLMOrchestratorAgent instance
            enable_alternatives: Whether to generate alternative solutions
            max_alternatives: Maximum number of alternative solutions
            confidence_threshold: Minimum confidence for primary solution
        """
        self.llm_orchestrator = llm_orchestrator
        self.enable_alternatives = enable_alternatives
        self.max_alternatives = max_alternatives
        self.confidence_threshold = confidence_threshold
        
        # Performance tracking
        self.metrics = {
            'total_suggestions': 0,
            'successful_suggestions': 0,
            'failed_suggestions': 0,
            'average_confidence': 0.0,
            'generation_times': []
        }
        
        logger.info(f"EnhancedSolutionSuggestionAgent initialized - alternatives: {enable_alternatives}, "
                   f"max_alternatives: {max_alternatives}, confidence_threshold: {confidence_threshold}")
    
    def _classify_suggestion_type(self, finding: Dict) -> SuggestionType:
        """
        Classify the type of suggestion based on finding characteristics.
        
        Args:
            finding (Dict): Static analysis finding
            
        Returns:
            SuggestionType: Classified suggestion type
        """
        category = finding.get('category', '').lower()
        rule_id = finding.get('rule_id', '').lower()
        message = finding.get('message', '').lower()
        severity = finding.get('severity', '').lower()
        
        # Security-related patterns
        if any(term in category for term in ['security', 'vulnerability', 'injection', 'xss', 'csrf']):
            return SuggestionType.SECURITY_FIX
        if any(term in rule_id for term in ['security', 'auth', 'crypto', 'password']):
            return SuggestionType.SECURITY_FIX
        if any(term in message for term in ['security', 'vulnerable', 'exploit', 'injection']):
            return SuggestionType.SECURITY_FIX
            
        # Performance-related patterns
        if any(term in category for term in ['performance', 'optimization', 'efficiency']):
            return SuggestionType.PERFORMANCE_OPTIMIZATION
        if any(term in rule_id for term in ['perf', 'slow', 'memory', 'cpu']):
            return SuggestionType.PERFORMANCE_OPTIMIZATION
        if any(term in message for term in ['slow', 'performance', 'optimize', 'inefficient']):
            return SuggestionType.PERFORMANCE_OPTIMIZATION
            
        # Testing-related patterns
        if any(term in category for term in ['test', 'coverage', 'mock']):
            return SuggestionType.TESTING
        if any(term in rule_id for term in ['test', 'assert', 'mock']):
            return SuggestionType.TESTING
            
        # Documentation patterns
        if any(term in category for term in ['doc', 'comment']):
            return SuggestionType.DOCUMENTATION
        if any(term in rule_id for term in ['doc', 'comment', 'missing_doc']):
            return SuggestionType.DOCUMENTATION
            
        # Architecture patterns
        if any(term in category for term in ['architecture', 'design', 'pattern']):
            return SuggestionType.ARCHITECTURE
        if any(term in rule_id for term in ['coupling', 'cohesion', 'solid']):
            return SuggestionType.ARCHITECTURE
            
        # Bug fix patterns
        if severity in ['high', 'critical']:
            return SuggestionType.BUG_FIX
        if any(term in message for term in ['error', 'exception', 'bug', 'null', 'undefined']):
            return SuggestionType.BUG_FIX
            
        # Default to best practice for code style, conventions, etc.
        return SuggestionType.BEST_PRACTICE
    
    def _construct_enhanced_prompt(self, finding: Dict, code_snippet: str, 
                                 suggestion_type: SuggestionType) -> str:
        """
        Construct an enhanced prompt for generating diverse, explainable solutions.
        
        Args:
            finding (Dict): Static analysis finding
            code_snippet (str): Relevant code snippet
            suggestion_type (SuggestionType): Type of suggestion to generate
            
        Returns:
            str: Enhanced prompt for LLM
        """
        rule_id = finding.get('rule_id', 'Unknown Issue')
        message = finding.get('message', 'No description available')
        line = finding.get('line', 'Unknown')
        category = finding.get('category', 'general')
        severity = finding.get('severity', 'medium')
        file_path = finding.get('file_path', 'unknown')
        
        # Generate context-specific guidance based on suggestion type
        type_guidance = {
            SuggestionType.SECURITY_FIX: """
SECURITY FOCUS: This is a security-related issue. Your suggestions must prioritize:
- Eliminating vulnerabilities and attack vectors
- Following secure coding practices
- Implementing proper input validation and sanitization
- Using established security frameworks and libraries
- Considering defense in depth principles""",
            
            SuggestionType.PERFORMANCE_OPTIMIZATION: """
PERFORMANCE FOCUS: This is a performance-related issue. Your suggestions must prioritize:
- Reducing computational complexity and resource usage
- Optimizing algorithms and data structures
- Minimizing memory allocations and I/O operations
- Leveraging caching and lazy loading where appropriate
- Measuring and benchmarking improvements""",
            
            SuggestionType.BEST_PRACTICE: """
BEST PRACTICE FOCUS: This is a code quality/style issue. Your suggestions must prioritize:
- Following language-specific conventions and idioms
- Improving code readability and maintainability
- Applying SOLID principles and design patterns
- Ensuring consistent naming and structure
- Following team/project coding standards""",
            
            SuggestionType.BUG_FIX: """
BUG FIX FOCUS: This is a potential bug or error. Your suggestions must prioritize:
- Eliminating null pointer exceptions and runtime errors
- Fixing logical errors and edge cases
- Ensuring proper error handling and validation
- Adding defensive programming practices
- Verifying correct algorithm implementation""",
            
            SuggestionType.TESTING: """
TESTING FOCUS: This is a testing-related issue. Your suggestions must prioritize:
- Improving test coverage and quality
- Following testing best practices (AAA pattern, etc.)
- Creating maintainable and reliable tests
- Using appropriate mocking and stubbing
- Ensuring tests are fast and deterministic""",
        }
        
        guidance = type_guidance.get(suggestion_type, "")
        
        prompt = f"""# Enhanced Code Issue Solution Request

## Issue Context
- **Rule ID**: {rule_id}
- **Category**: {category}
- **Severity**: {severity}
- **Line**: {line}
- **File**: {file_path}
- **Description**: {message}
- **Suggestion Type**: {suggestion_type.value}

{guidance}

## Code to Analyze
```python
{code_snippet}
```

## Enhanced XAI Requirements

You MUST provide a comprehensive solution with MULTIPLE ALTERNATIVES and EXPLAINABLE AI reasoning.

### Required Response Structure:

## PRIMARY SOLUTION

### Approach Name
[Give this approach a clear, descriptive name]

### Description
[Detailed description of this approach]

### Reasoning
**Primary Reason:** [Main reason why this is the best approach]
**Supporting Reasons:** [List 2-3 additional supporting reasons]
**Confidence Score:** [0.0-1.0]
**Evidence:** [List specific evidence supporting this approach]
**Assumptions:** [Any assumptions made]
**Limitations:** [Known limitations of this approach]

### Pros and Cons
**Pros:**
- [Advantage 1]
- [Advantage 2]
- [Advantage 3]

**Cons:**
- [Disadvantage 1]
- [Disadvantage 2]

**Trade-offs:**
- [Trade-off 1]
- [Trade-off 2]

**Risk Assessment:** [Overall risk assessment]

### Implementation Complexity
[low/medium/high] - [Brief explanation]

### Code Suggestion
```python
# Title: [Brief title for this code change]
# Description: [What this code does]
[Your suggested code here]
```

**Impact Assessment:** [Assessment of impact if this code is applied]

### Implementation Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## ALTERNATIVE SOLUTION 1

[Follow the same structure as primary solution]

## ALTERNATIVE SOLUTION 2

[Follow the same structure as primary solution]

## OVERALL ANALYSIS

### Impact Analysis
[Analysis of potential impact of implementing any of these solutions]

### Context Considerations
- [Important context factor 1]
- [Important context factor 2]
- [Important context factor 3]

### Best Practices
- [Related best practice 1]
- [Related best practice 2]
- [Related best practice 3]

### Confidence Breakdown
- **Solution Accuracy:** [0.0-1.0]
- **Implementation Feasibility:** [0.0-1.0]
- **Impact Assessment:** [0.0-1.0]
- **Risk Analysis:** [0.0-1.0]

## CRITICAL REQUIREMENTS:
1. Provide EXACTLY 1 primary solution and {self.max_alternatives} alternatives
2. Include numerical confidence scores (0.0-1.0) for ALL reasoning
3. Provide specific, actionable code suggestions
4. Include detailed pros/cons for each approach
5. Explain WHY each solution works and what evidence supports it
6. Consider real-world implementation constraints
7. Focus specifically on {suggestion_type.value} concerns
"""
        
        return prompt
    
    def _parse_enhanced_response(self, llm_response: str, suggestion_type: SuggestionType) -> Dict[str, Any]:
        """
        Parse enhanced LLM response into structured components.
        
        Args:
            llm_response (str): Raw LLM response
            suggestion_type (SuggestionType): Type of suggestion
            
        Returns:
            Dict[str, Any]: Parsed response with primary and alternative solutions
        """
        parsed = {
            'primary_solution': None,
            'alternative_solutions': [],
            'overall_analysis': {},
            'confidence_breakdown': {},
            'raw_response': llm_response
        }
        
        try:
            # Extract primary solution
            primary_match = re.search(
                r'## PRIMARY SOLUTION\s*\n(.*?)(?=## ALTERNATIVE SOLUTION|## OVERALL ANALYSIS|\Z)',
                llm_response, re.DOTALL | re.IGNORECASE
            )
            
            if primary_match:
                parsed['primary_solution'] = self._parse_solution_section(
                    primary_match.group(1), suggestion_type, is_primary=True
                )
            
            # Extract alternative solutions
            alt_pattern = r'## ALTERNATIVE SOLUTION (\d+)\s*\n(.*?)(?=## ALTERNATIVE SOLUTION|## OVERALL ANALYSIS|\Z)'
            alt_matches = re.findall(alt_pattern, llm_response, re.DOTALL | re.IGNORECASE)
            
            for alt_num, alt_content in alt_matches:
                alt_solution = self._parse_solution_section(alt_content, suggestion_type, is_primary=False)
                if alt_solution:
                    parsed['alternative_solutions'].append(alt_solution)
            
            # Extract overall analysis
            overall_match = re.search(
                r'## OVERALL ANALYSIS\s*\n(.*?)(?=\Z)',
                llm_response, re.DOTALL | re.IGNORECASE
            )
            
            if overall_match:
                parsed['overall_analysis'] = self._parse_overall_analysis(overall_match.group(1))
            
        except Exception as e:
            logger.error(f"Error parsing enhanced LLM response: {str(e)}")
            # Provide fallback parsing
            parsed['primary_solution'] = self._create_fallback_solution(llm_response, suggestion_type)
        
        # Ensure primary_solution is not None for fallback cases
        if parsed['primary_solution'] is None:
            parsed['primary_solution'] = self._create_fallback_solution(llm_response, suggestion_type)
        
        return parsed
    
    def _parse_solution_section(self, content: str, suggestion_type: SuggestionType, 
                              is_primary: bool = True) -> Optional[Dict[str, Any]]:
        """
        Parse a single solution section (primary or alternative).
        
        Args:
            content (str): Content of the solution section
            suggestion_type (SuggestionType): Type of suggestion
            is_primary (bool): Whether this is the primary solution
            
        Returns:
            Optional[Dict[str, Any]]: Parsed solution data
        """
        try:
            solution = {
                'approach_name': '',
                'description': '',
                'reasoning': {},
                'pros_cons': {},
                'implementation_complexity': '',
                'code_suggestions': [],
                'implementation_steps': []
            }
            
            # Extract approach name
            name_match = re.search(r'### Approach Name\s*\n([^\n]+)', content, re.IGNORECASE)
            if name_match:
                solution['approach_name'] = name_match.group(1).strip()
            
            # Extract description
            desc_match = re.search(r'### Description\s*\n(.*?)(?=###|\Z)', content, re.DOTALL | re.IGNORECASE)
            if desc_match:
                solution['description'] = desc_match.group(1).strip()
            
            # Extract reasoning
            reasoning_match = re.search(r'### Reasoning\s*\n(.*?)(?=###|\Z)', content, re.DOTALL | re.IGNORECASE)
            if reasoning_match:
                solution['reasoning'] = self._parse_reasoning_section(reasoning_match.group(1))
            
            # Extract pros and cons
            proscons_match = re.search(r'### Pros and Cons\s*\n(.*?)(?=###|\Z)', content, re.DOTALL | re.IGNORECASE)
            if proscons_match:
                solution['pros_cons'] = self._parse_pros_cons_section(proscons_match.group(1))
            
            # Extract implementation complexity
            complexity_match = re.search(r'### Implementation Complexity\s*\n([^\n]+)', content, re.IGNORECASE)
            if complexity_match:
                solution['implementation_complexity'] = complexity_match.group(1).strip()
            
            # Extract code suggestions
            code_match = re.search(r'### Code Suggestion\s*\n(.*?)(?=###|\Z)', content, re.DOTALL | re.IGNORECASE)
            if code_match:
                solution['code_suggestions'] = self._parse_code_suggestion(code_match.group(1))
            
            # Extract implementation steps
            steps_match = re.search(r'### Implementation Steps\s*\n(.*?)(?=###|\Z)', content, re.DOTALL | re.IGNORECASE)
            if steps_match:
                solution['implementation_steps'] = self._parse_implementation_steps(steps_match.group(1))
            
            return solution if solution['approach_name'] else None
            
        except Exception as e:
            logger.error(f"Error parsing solution section: {str(e)}")
            return None
    
    def _parse_reasoning_section(self, content: str) -> Dict[str, Any]:
        """Parse reasoning section into structured data."""
        reasoning = {
            'primary_reason': '',
            'supporting_reasons': [],
            'confidence_score': 0.5,
            'evidence': [],
            'assumptions': [],
            'limitations': []
        }
        
        # Extract primary reason
        primary_match = re.search(r'\*\*Primary Reason:\*\*\s*(.*?)(?=\*\*|\n\n|\Z)', content, re.DOTALL)
        if primary_match:
            reasoning['primary_reason'] = primary_match.group(1).strip()
        
        # Extract confidence score
        conf_match = re.search(r'\*\*Confidence Score:\*\*\s*(\d+\.?\d*)', content)
        if conf_match:
            reasoning['confidence_score'] = float(conf_match.group(1))
        
        # Extract supporting reasons
        support_match = re.search(r'\*\*Supporting Reasons:\*\*\s*(.*?)(?=\*\*|\n\n|\Z)', content, re.DOTALL)
        if support_match:
            reasons_text = support_match.group(1).strip()
            reasoning['supporting_reasons'] = [r.strip('- ').strip() for r in reasons_text.split('\n') if r.strip() and r.strip() != '-']
        
        # Extract evidence
        evidence_match = re.search(r'\*\*Evidence:\*\*\s*(.*?)(?=\*\*|\n\n|\Z)', content, re.DOTALL)
        if evidence_match:
            evidence_text = evidence_match.group(1).strip()
            reasoning['evidence'] = [e.strip('- ').strip() for e in evidence_text.split('\n') if e.strip() and e.strip() != '-']
        
        # Extract assumptions
        assumptions_match = re.search(r'\*\*Assumptions:\*\*\s*(.*?)(?=\*\*|\n\n|\Z)', content, re.DOTALL)
        if assumptions_match:
            assumptions_text = assumptions_match.group(1).strip()
            reasoning['assumptions'] = [a.strip('- ').strip() for a in assumptions_text.split('\n') if a.strip() and a.strip() != '-']
        
        # Extract limitations
        limitations_match = re.search(r'\*\*Limitations:\*\*\s*(.*?)(?=\*\*|\n\n|\Z)', content, re.DOTALL)
        if limitations_match:
            limitations_text = limitations_match.group(1).strip()
            reasoning['limitations'] = [l.strip('- ').strip() for l in limitations_text.split('\n') if l.strip() and l.strip() != '-']
        
        return reasoning
    
    def _parse_pros_cons_section(self, content: str) -> Dict[str, Any]:
        """Parse pros and cons section."""
        pros_cons = {
            'pros': [],
            'cons': [],
            'trade_offs': [],
            'risk_assessment': ''
        }
        
        # Extract pros
        pros_match = re.search(r'\*\*Pros:\*\*\s*(.*?)(?=\*\*|\Z)', content, re.DOTALL)
        if pros_match:
            pros_text = pros_match.group(1).strip()
            pros_cons['pros'] = [p.strip('- ').strip() for p in pros_text.split('\n') if p.strip() and p.strip() != '-']
        
        # Extract cons
        cons_match = re.search(r'\*\*Cons:\*\*\s*(.*?)(?=\*\*|\Z)', content, re.DOTALL)
        if cons_match:
            cons_text = cons_match.group(1).strip()
            pros_cons['cons'] = [c.strip('- ').strip() for c in cons_text.split('\n') if c.strip() and c.strip() != '-']
        
        # Extract risk assessment
        risk_match = re.search(r'\*\*Risk Assessment:\*\*\s*(.*?)(?=\*\*|\n\n|\Z)', content, re.DOTALL)
        if risk_match:
            pros_cons['risk_assessment'] = risk_match.group(1).strip()
        
        return pros_cons
    
    def _parse_code_suggestion(self, content: str) -> List[Dict[str, Any]]:
        """Parse code suggestion section."""
        suggestions = []
        
        # Extract code blocks
        code_pattern = r'```python\s*\n(.*?)```'
        code_matches = re.findall(code_pattern, content, re.DOTALL)
        
        # Extract title and description
        title_match = re.search(r'# Title:\s*(.*?)(?=\n|$)', content)
        desc_match = re.search(r'# Description:\s*(.*?)(?=\n|$)', content)
        impact_match = re.search(r'\*\*Impact Assessment:\*\*\s*(.*?)(?=\*\*|\n\n|\Z)', content, re.DOTALL)
        
        if code_matches:
            for code in code_matches:
                suggestion = {
                    'title': title_match.group(1).strip() if title_match else 'Code Suggestion',
                    'description': desc_match.group(1).strip() if desc_match else '',
                    'suggested_code': code.strip(),
                    'impact_assessment': impact_match.group(1).strip() if impact_match else ''
                }
                suggestions.append(suggestion)
        
        return suggestions
    
    def _parse_implementation_steps(self, content: str) -> List[str]:
        """Parse implementation steps."""
        steps = []
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '*')) or line[0].isdigit()):
                # Remove numbering and bullet points
                clean_step = re.sub(r'^\d+\.\s*|^[-*]\s*', '', line).strip()
                if clean_step:
                    steps.append(clean_step)
        
        return steps
    
    def _parse_overall_analysis(self, content: str) -> Dict[str, Any]:
        """Parse overall analysis section."""
        analysis = {
            'impact_analysis': '',
            'context_considerations': [],
            'best_practices': [],
            'confidence_breakdown': {}
        }
        
        # Extract impact analysis
        impact_match = re.search(r'### Impact Analysis\s*\n(.*?)(?=###|\Z)', content, re.DOTALL | re.IGNORECASE)
        if impact_match:
            analysis['impact_analysis'] = impact_match.group(1).strip()
        
        # Extract context considerations
        context_match = re.search(r'### Context Considerations\s*\n(.*?)(?=###|\Z)', content, re.DOTALL | re.IGNORECASE)
        if context_match:
            context_text = context_match.group(1).strip()
            analysis['context_considerations'] = [c.strip('- ').strip() for c in context_text.split('\n') if c.strip() and c.strip() != '-']
        
        # Extract best practices
        practices_match = re.search(r'### Best Practices\s*\n(.*?)(?=###|\Z)', content, re.DOTALL | re.IGNORECASE)
        if practices_match:
            practices_text = practices_match.group(1).strip()
            analysis['best_practices'] = [p.strip('- ').strip() for p in practices_text.split('\n') if p.strip() and p.strip() != '-']
        
        # Extract confidence breakdown
        conf_match = re.search(r'### Confidence Breakdown\s*\n(.*?)(?=###|\Z)', content, re.DOTALL | re.IGNORECASE)
        if conf_match:
            conf_text = conf_match.group(1).strip()
            analysis['confidence_breakdown'] = self._parse_confidence_breakdown(conf_text)
        
        return analysis
    
    def _parse_confidence_breakdown(self, content: str) -> Dict[str, float]:
        """Parse confidence breakdown scores."""
        breakdown = {}
        
        # Find all confidence score patterns
        pattern = r'- \*\*([^:]+):\*\*\s*(\d+\.?\d*)'
        matches = re.findall(pattern, content)
        
        for key, score in matches:
            try:
                breakdown[key.strip()] = float(score)
            except ValueError:
                continue
        
        return breakdown
    
    def _create_fallback_solution(self, response: str, suggestion_type: SuggestionType) -> Dict[str, Any]:
        """Create a fallback solution when parsing fails."""
        return {
            'approach_name': f'Fallback {suggestion_type.value.replace("_", " ").title()} Solution',
            'description': 'Generated fallback solution due to parsing issues',
            'reasoning': {
                'primary_reason': 'Fallback due to parsing failure',
                'supporting_reasons': [],
                'confidence_score': 0.3,
                'evidence': [],
                'assumptions': ['This is a fallback solution'],
                'limitations': ['Limited analysis due to parsing failure']
            },
            'pros_cons': {
                'pros': ['Provides basic guidance'],
                'cons': ['May not be fully optimized', 'Limited analysis'],
                'trade_offs': [],
                'risk_assessment': 'Medium risk due to limited analysis'
            },
            'implementation_complexity': 'medium',
            'code_suggestions': [{
                'title': 'Basic Code Suggestion',
                'description': 'Basic suggestion extracted from response',
                'suggested_code': '# See raw LLM response for details',
                'impact_assessment': 'Unknown impact'
            }],
            'implementation_steps': ['Review raw LLM response', 'Apply manual analysis']
        }
    
    def generate_enhanced_solution(self, finding: Dict, code_snippet: str, 
                                 llm_orchestrator=None) -> SolutionSuggestion:
        """
        Generate an enhanced solution with XAI capabilities and multiple alternatives.
        
        Args:
            finding (Dict): Static analysis finding
            code_snippet (str): Relevant code snippet
            llm_orchestrator: LLMOrchestratorAgent instance
            
        Returns:
            SolutionSuggestion: Enhanced solution with XAI data
        """
        start_time = time.time()
        orchestrator = llm_orchestrator or self.llm_orchestrator
        
        if not orchestrator:
            raise ValueError("No LLMOrchestratorAgent provided")
        
        try:
            # Classify suggestion type
            suggestion_type = self._classify_suggestion_type(finding)
            logger.info(f"Classified suggestion type: {suggestion_type.value} for finding: {finding.get('rule_id')}")
            
            # Construct enhanced prompt
            prompt = self._construct_enhanced_prompt(finding, code_snippet, suggestion_type)
            
            # Get LLM response
            logger.info(f"Generating enhanced solution for finding: {finding.get('rule_id')}")
            llm_response = orchestrator.invoke_llm(
                prompt="Generate enhanced solution with XAI capabilities",
                code_snippet=prompt
            )
            
            # Parse enhanced response
            parsed_data = self._parse_enhanced_response(llm_response, suggestion_type)
            
            # Build enhanced solution
            solution = self._build_solution_suggestion(
                finding=finding,
                suggestion_type=suggestion_type,
                parsed_data=parsed_data,
                llm_response=llm_response,
                prompt=prompt,
                processing_time=int((time.time() - start_time) * 1000)
            )
            
            # Update metrics
            self.metrics['total_suggestions'] += 1
            self.metrics['successful_suggestions'] += 1
            self.metrics['generation_times'].append(time.time() - start_time)
            
            logger.info(f"Successfully generated enhanced solution for {finding.get('rule_id')}")
            return solution
            
        except Exception as e:
            logger.error(f"Error generating enhanced solution: {str(e)}")
            self.metrics['total_suggestions'] += 1
            self.metrics['failed_suggestions'] += 1
            
            # Return fallback solution
            return self._create_fallback_solution_object(finding, str(e), int((time.time() - start_time) * 1000))
    
    def _build_solution_suggestion(self, finding: Dict, suggestion_type: SuggestionType,
                                 parsed_data: Dict, llm_response: str, prompt: str,
                                 processing_time: int) -> SolutionSuggestion:
        """Build a SolutionSuggestion object from parsed data."""
        
        # Build primary solution
        primary_data = parsed_data.get('primary_solution', {})
        primary_solution = self._build_alternative_solution(primary_data, suggestion_type)
        
        # Build alternative solutions
        alternative_solutions = []
        for alt_data in parsed_data.get('alternative_solutions', []):
            alt_solution = self._build_alternative_solution(alt_data, suggestion_type)
            if alt_solution:
                alternative_solutions.append(alt_solution)
        
        # Build overall reasoning
        overall_analysis = parsed_data.get('overall_analysis', {})
        primary_reasoning = primary_data.get('reasoning', {})
        
        overall_reasoning = XAIReasoning(
            primary_reason=overall_analysis.get('impact_analysis', 'Enhanced solution generated'),
            supporting_reasons=overall_analysis.get('context_considerations', []),
            confidence_score=primary_reasoning.get('confidence_score', 0.7),
            confidence_level=ConfidenceLevel.MEDIUM,
            evidence=[
                Evidence(
                    type=EvidenceType.CODE_PATTERN,
                    description=f"Analysis of {finding.get('rule_id', 'unknown')} pattern",
                    confidence=0.8
                )
            ],
            assumptions=primary_reasoning.get('assumptions', []),
            limitations=primary_reasoning.get('limitations', [])
        )
        
        return SolutionSuggestion(
            finding_id=finding.get('rule_id', 'unknown'),
            suggestion_type=suggestion_type,
            title=primary_solution.approach_name if primary_solution else f"{suggestion_type.value.replace('_', ' ').title()} Solution",
            summary=primary_solution.description if primary_solution else "Enhanced solution with multiple alternatives",
            primary_solution=primary_solution,
            alternative_solutions=alternative_solutions,
            overall_reasoning=overall_reasoning,
            confidence_breakdown=overall_analysis.get('confidence_breakdown', {}),
            impact_analysis=overall_analysis.get('impact_analysis', ''),
            context_considerations=overall_analysis.get('context_considerations', []),
            implementation_steps=primary_data.get('implementation_steps', []),
            best_practices=overall_analysis.get('best_practices', []),
            processing_time_ms=processing_time,
            raw_llm_response=llm_response,
            prompt_used=prompt
        )
    
    def _build_alternative_solution(self, solution_data: Dict, suggestion_type: SuggestionType) -> Optional[AlternativeSolution]:
        """Build an AlternativeSolution object from parsed data."""
        if not solution_data or not solution_data.get('approach_name'):
            return None
        
        try:
            # Build reasoning
            reasoning_data = solution_data.get('reasoning', {})
            reasoning = XAIReasoning(
                primary_reason=reasoning_data.get('primary_reason', 'Solution approach'),
                supporting_reasons=reasoning_data.get('supporting_reasons', []),
                confidence_score=reasoning_data.get('confidence_score', 0.6),
                confidence_level=ConfidenceLevel.MEDIUM,
                evidence=[
                    Evidence(
                        type=EvidenceType.CODE_PATTERN,
                        description=evidence,
                        confidence=0.7
                    ) for evidence in reasoning_data.get('evidence', [])
                ],
                assumptions=reasoning_data.get('assumptions', []),
                limitations=reasoning_data.get('limitations', [])
            )
            
            # Build pros/cons
            pros_cons_data = solution_data.get('pros_cons', {})
            pros_cons = ProsCons(
                pros=pros_cons_data.get('pros', []),
                cons=pros_cons_data.get('cons', []),
                trade_offs=pros_cons_data.get('trade_offs', []),
                risk_assessment=pros_cons_data.get('risk_assessment', '')
            )
            
            # Build code suggestions
            code_suggestions = []
            for code_data in solution_data.get('code_suggestions', []):
                code_suggestion = CodeSuggestion(
                    title=code_data.get('title', 'Code Change'),
                    description=code_data.get('description', ''),
                    suggested_code=code_data.get('suggested_code', ''),
                    reasoning=reasoning,  # Use same reasoning for simplicity
                    impact_assessment=code_data.get('impact_assessment', '')
                )
                code_suggestions.append(code_suggestion)
            
            return AlternativeSolution(
                approach_name=solution_data.get('approach_name', ''),
                description=solution_data.get('description', ''),
                code_suggestions=code_suggestions,
                pros_cons=pros_cons,
                reasoning=reasoning,
                implementation_complexity=solution_data.get('implementation_complexity', 'medium'),
                estimated_effort='',
                prerequisites=[]
            )
            
        except Exception as e:
            logger.error(f"Error building alternative solution: {str(e)}")
            return None
    
    def _create_fallback_solution_object(self, finding: Dict, error: str, processing_time: int) -> SolutionSuggestion:
        """Create a fallback SolutionSuggestion object when generation fails."""
        suggestion_type = self._classify_suggestion_type(finding)
        
        # Create fallback reasoning
        fallback_reasoning = XAIReasoning(
            primary_reason=f"Solution generation failed: {error}",
            supporting_reasons=[],
            confidence_score=0.2,
            confidence_level=ConfidenceLevel.VERY_LOW,
            evidence=[],
            assumptions=['Manual review required'],
            limitations=['Limited automated analysis due to error']
        )
        
        # Create fallback solution
        fallback_solution = AlternativeSolution(
            approach_name="Manual Review Required",
            description=f"Automated solution generation failed. Manual review is needed for this {suggestion_type.value} issue.",
            code_suggestions=[
                CodeSuggestion(
                    title="Manual Analysis Required",
                    description="Please review this finding manually",
                    suggested_code="# Manual review and solution required",
                    reasoning=fallback_reasoning,
                    impact_assessment="Unknown - requires manual assessment"
                )
            ],
            pros_cons=ProsCons(
                pros=["Ensures human oversight"],
                cons=["No immediate automated guidance", "Requires manual effort"],
                trade_offs=["Time vs. automation"],
                risk_assessment="Low risk - manual review ensures quality"
            ),
            reasoning=fallback_reasoning,
            implementation_complexity="unknown",
            estimated_effort="Manual assessment required"
        )
        
        return SolutionSuggestion(
            finding_id=finding.get('rule_id', 'unknown'),
            suggestion_type=suggestion_type,
            title="Manual Review Required",
            summary=f"Automated solution failed - manual review needed for {finding.get('rule_id', 'unknown')}",
            primary_solution=fallback_solution,
            alternative_solutions=[],
            overall_reasoning=fallback_reasoning,
            confidence_breakdown={'overall': 0.2},
            impact_analysis=f"Could not determine impact automatically. Error: {error}",
            context_considerations=["Manual review required", "Error in automated analysis"],
            implementation_steps=["Review finding manually", "Determine appropriate solution", "Implement fix"],
            best_practices=["Always review automated suggestions", "Test changes thoroughly"],
            processing_time_ms=processing_time,
            raw_llm_response=f"Error: {error}",
            prompt_used="N/A - Error occurred before prompt construction"
        )
    
    def generate_solution_batch(self, findings: List[Dict], code_files: Dict[str, str],
                               llm_orchestrator=None) -> SuggestionBatch:
        """
        Generate enhanced solutions for multiple findings.
        
        Args:
            findings (List[Dict]): List of static analysis findings
            code_files (Dict[str, str]): Dictionary of file paths to code content
            llm_orchestrator: LLMOrchestratorAgent instance
            
        Returns:
            SuggestionBatch: Batch of enhanced solutions
        """
        batch_id = str(uuid.uuid4())
        batch_start = datetime.now()
        
        logger.info(f"Starting enhanced solution batch {batch_id} for {len(findings)} findings")
        
        batch = SuggestionBatch(
            batch_id=batch_id,
            scan_id=findings[0].get('scan_id', 'unknown') if findings else 'unknown',
            total_findings=len(findings),
            batch_start_time=batch_start
        )
        
        for finding in findings:
            try:
                # Get code snippet
                file_path = finding.get('file_path', '')
                line_number = finding.get('line', 1)
                
                if file_path in code_files:
                    code_lines = code_files[file_path].split('\n')
                    start_line = max(0, line_number - 5)
                    end_line = min(len(code_lines), line_number + 5)
                    code_snippet = '\n'.join(code_lines[start_line:end_line])
                else:
                    code_snippet = "# Code snippet not available"
                
                # Generate enhanced solution
                solution = self.generate_enhanced_solution(
                    finding=finding,
                    code_snippet=code_snippet,
                    llm_orchestrator=llm_orchestrator
                )
                
                batch.suggestions.append(solution)
                batch.successful_suggestions += 1
                
                # Update suggestion types breakdown
                suggestion_type = solution.suggestion_type
                if suggestion_type not in batch.suggestion_types_breakdown:
                    batch.suggestion_types_breakdown[suggestion_type] = 0
                batch.suggestion_types_breakdown[suggestion_type] += 1
                
            except Exception as e:
                logger.error(f"Error processing finding {finding.get('rule_id', 'Unknown')}: {str(e)}")
                batch.failed_suggestions += 1
        
        # Finalize batch
        batch.batch_end_time = datetime.now()
        batch.total_processing_time_ms = int((batch.batch_end_time - batch.batch_start_time).total_seconds() * 1000)
        
        if batch.suggestions:
            confidence_scores = [s.overall_reasoning.confidence_score for s in batch.suggestions]
            batch.average_confidence = sum(confidence_scores) / len(confidence_scores)
        
        logger.info(f"Completed enhanced solution batch {batch_id}: "
                   f"{batch.successful_suggestions} successful, {batch.failed_suggestions} failed")
        
        return batch
    
    def get_metrics(self) -> SuggestionMetrics:
        """
        Get current metrics for the agent.
        
        Returns:
            SuggestionMetrics: Current performance metrics
        """
        if self.metrics['generation_times']:
            avg_time = sum(self.metrics['generation_times']) / len(self.metrics['generation_times'])
            avg_time_ms = avg_time * 1000
        else:
            avg_time_ms = 0.0
        
        success_rate = (
            self.metrics['successful_suggestions'] / self.metrics['total_suggestions']
            if self.metrics['total_suggestions'] > 0 else 0.0
        )
        
        return SuggestionMetrics(
            total_suggestions=self.metrics['total_suggestions'],
            average_confidence=self.metrics['average_confidence'],
            confidence_distribution={},  # Would need to track this separately
            average_generation_time_ms=avg_time_ms,
            success_rate=success_rate,
            suggestion_types_count={},  # Would need to track this separately
            period_start=datetime.now(),  # Would need to track this properly
            period_end=datetime.now()
        )
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get enhanced agent information."""
        return {
            'agent_name': 'EnhancedSolutionSuggestionAgent',
            'version': '2.0.0',
            'has_llm_orchestrator': self.llm_orchestrator is not None,
            'capabilities': [
                'xai_reasoning',
                'multiple_alternatives',
                'confidence_scoring',
                'evidence_tracking',
                'pros_cons_analysis',
                'diverse_suggestion_types',
                'error_recovery',
                'performance_metrics'
            ],
            'configuration': {
                'enable_alternatives': self.enable_alternatives,
                'max_alternatives': self.max_alternatives,
                'confidence_threshold': self.confidence_threshold
            },
            'metrics': self.metrics
        } 