"""
ProjectScanningAgent for AI Code Review System.

This module implements the ProjectScanningAgent responsible for scanning entire projects,
performing hierarchical code summarization, and providing project-wide architectural analysis.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from collections import defaultdict
import json

from .llm_orchestrator_agent import LLMOrchestratorAgent
from .rag_context_agent import RAGContextAgent

# Configure logging
logger = logging.getLogger(__name__)


class ProjectScanningAgent:
    """
    Agent responsible for comprehensive project-level code analysis.
    
    This agent handles:
    - Hierarchical code summarization for large projects
    - Project-wide context building using RAG
    - LLM-based architectural analysis and risk assessment
    - Full project report generation with structural insights
    """
    
    def __init__(
        self, 
        llm_orchestrator: Optional[LLMOrchestratorAgent] = None,
        rag_agent: Optional[RAGContextAgent] = None,
        max_files_for_direct_analysis: int = 50,
        max_lines_per_summary: int = 500
    ):
        """
        Initialize the ProjectScanningAgent.
        
        Args:
            llm_orchestrator (Optional[LLMOrchestratorAgent]): LLM agent for analysis
            rag_agent (Optional[RAGContextAgent]): RAG agent for context retrieval
            max_files_for_direct_analysis (int): Max files before using hierarchical summarization
            max_lines_per_summary (int): Max lines to include in each summary
        """
        self.llm_orchestrator = llm_orchestrator or LLMOrchestratorAgent()
        self.rag_agent = rag_agent or RAGContextAgent()
        self.max_files_for_direct_analysis = max_files_for_direct_analysis
        self.max_lines_per_summary = max_lines_per_summary
        
        logger.info(f"ProjectScanningAgent initialized with max_files: {max_files_for_direct_analysis}")
    
    def _group_files_by_directory(self, code_files: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """
        Group files by their directory structure for hierarchical analysis.
        
        Args:
            code_files (Dict[str, str]): Dictionary mapping file paths to code content
            
        Returns:
            Dict[str, Dict[str, str]]: Files grouped by directory
        """
        directory_groups = defaultdict(dict)
        
        for file_path, content in code_files.items():
            # Get directory path
            dir_path = str(Path(file_path).parent)
            if dir_path == '.':
                dir_path = 'root'
            
            directory_groups[dir_path][file_path] = content
        
        return dict(directory_groups)
    
    def _calculate_complexity_metrics(self, code_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Calculate basic complexity metrics for the project.
        
        Args:
            code_files (Dict[str, str]): Dictionary mapping file paths to code content
            
        Returns:
            Dict[str, Any]: Complexity metrics
        """
        metrics = {
            'total_files': len(code_files),
            'total_lines': 0,
            'total_size_bytes': 0,
            'languages': defaultdict(int),
            'largest_files': [],
            'average_file_size': 0
        }
        
        file_sizes = []
        
        for file_path, content in code_files.items():
            lines = len(content.split('\n'))
            size_bytes = len(content.encode('utf-8'))
            
            metrics['total_lines'] += lines
            metrics['total_size_bytes'] += size_bytes
            file_sizes.append((file_path, lines, size_bytes))
            
            # Detect language by extension
            ext = Path(file_path).suffix.lower()
            if ext == '.py':
                metrics['languages']['python'] += 1
            elif ext == '.java':
                metrics['languages']['java'] += 1
            elif ext in ['.kt', '.kts']:
                metrics['languages']['kotlin'] += 1
            else:
                metrics['languages']['other'] += 1
        
        # Calculate average file size
        if len(code_files) > 0:
            metrics['average_file_size'] = metrics['total_lines'] / len(code_files)
        
        # Get top 10 largest files
        file_sizes.sort(key=lambda x: x[1], reverse=True)
        metrics['largest_files'] = [
            {'file': f[0], 'lines': f[1], 'bytes': f[2]} 
            for f in file_sizes[:10]
        ]
        
        return metrics
    
    def _hierarchical_summarize(
        self, 
        code_files: Dict[str, str], 
        level: str = "file"
    ) -> Dict[str, str]:
        """
        Perform hierarchical summarization of code using LLM.
        
        Args:
            code_files (Dict[str, str]): Dictionary mapping file paths to code content
            level (str): Summarization level ('file', 'directory', 'project')
            
        Returns:
            Dict[str, str]: Dictionary mapping paths to their summaries
        """
        summaries = {}
        
        try:
            if level == "file":
                # Summarize individual files
                for file_path, content in code_files.items():
                    if len(content.split('\n')) > self.max_lines_per_summary:
                        # File is too large, summarize it
                        summary = self._summarize_large_file(file_path, content)
                        summaries[file_path] = summary
                    else:
                        # File is small enough to include directly
                        summaries[file_path] = content
                        
            elif level == "directory":
                # Group files by directory and summarize each directory
                directory_groups = self._group_files_by_directory(code_files)
                
                for dir_path, dir_files in directory_groups.items():
                    # First, get file-level summaries
                    file_summaries = self._hierarchical_summarize(dir_files, "file")
                    
                    # Then summarize the directory
                    dir_summary = self._summarize_directory(dir_path, file_summaries)
                    summaries[dir_path] = dir_summary
                    
            elif level == "project":
                # Create project-level summary from directory summaries
                dir_summaries = self._hierarchical_summarize(code_files, "directory")
                project_summary = self._summarize_project(dir_summaries)
                summaries["project"] = project_summary
                
        except Exception as e:
            logger.error(f"Error in hierarchical summarization at level '{level}': {str(e)}")
            # Fallback: return simplified summaries
            summaries = self._create_fallback_summaries(code_files, level)
        
        return summaries
    
    def _summarize_large_file(self, file_path: str, content: str) -> str:
        """
        Summarize a large file using LLM.
        
        Args:
            file_path (str): Path to the file
            content (str): File content
            
        Returns:
            str: Summary of the file
        """
        try:
            prompt = f"""Analyze and summarize this code file: {file_path}

Please provide a concise summary including:
1. Main purpose and functionality
2. Key classes/functions/components
3. Important dependencies and imports
4. Potential issues or code quality concerns
5. Architectural role in the project

Keep the summary under 200 words but include all critical information for understanding the file's role in the project.

Code to analyze:
{content[:3000]}{'...' if len(content) > 3000 else ''}
"""
            
            response = self.llm_orchestrator.invoke_llm(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error summarizing file {file_path}: {str(e)}")
            # Fallback: create simple summary
            lines = content.split('\n')
            return f"File: {file_path}\nLines: {len(lines)}\nSummary: Large file requiring detailed analysis."
    
    def _summarize_directory(self, dir_path: str, file_summaries: Dict[str, str]) -> str:
        """
        Summarize a directory based on its file summaries.
        
        Args:
            dir_path (str): Directory path
            file_summaries (Dict[str, str]): Summaries of files in the directory
            
        Returns:
            str: Summary of the directory
        """
        try:
            # Combine file summaries
            combined_summaries = "\n\n".join([
                f"File: {file_path}\n{summary}" 
                for file_path, summary in file_summaries.items()
            ])
            
            prompt = f"""Analyze this directory and its files: {dir_path}

Please provide a directory-level summary including:
1. Purpose and role of this directory in the project
2. Main components and their relationships
3. Architecture patterns used
4. Dependencies between files in this directory
5. Potential architectural concerns or improvements

File summaries in this directory:
{combined_summaries[:4000]}{'...' if len(combined_summaries) > 4000 else ''}
"""
            
            response = self.llm_orchestrator.invoke_llm(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error summarizing directory {dir_path}: {str(e)}")
            # Fallback: create simple summary
            file_count = len(file_summaries)
            return f"Directory: {dir_path}\nFiles: {file_count}\nSummary: Directory containing {file_count} files requiring analysis."
    
    def _summarize_project(self, directory_summaries: Dict[str, str]) -> str:
        """
        Create project-level summary from directory summaries.
        
        Args:
            directory_summaries (Dict[str, str]): Summaries of project directories
            
        Returns:
            str: Project-level summary
        """
        try:
            # Combine directory summaries
            combined_summaries = "\n\n".join([
                f"Directory: {dir_path}\n{summary}" 
                for dir_path, summary in directory_summaries.items()
            ])
            
            prompt = f"""Analyze this entire project based on directory summaries:

Please provide a comprehensive project-level analysis including:
1. Overall project architecture and design patterns
2. Technology stack and frameworks used
3. Module organization and dependency structure
4. Code quality and maintainability assessment
5. Security considerations and potential vulnerabilities
6. Performance considerations and optimization opportunities
7. Scalability and architectural concerns
8. Recommendations for improvements

Directory summaries:
{combined_summaries[:5000]}{'...' if len(combined_summaries) > 5000 else ''}
"""
            
            response = self.llm_orchestrator.invoke_llm(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error creating project summary: {str(e)}")
            # Fallback: create simple summary
            dir_count = len(directory_summaries)
            return f"Project Summary\nDirectories: {dir_count}\nSummary: Large project requiring comprehensive analysis."
    
    def _create_fallback_summaries(self, code_files: Dict[str, str], level: str) -> Dict[str, str]:
        """
        Create fallback summaries when LLM analysis fails.
        
        Args:
            code_files (Dict[str, str]): Code files to summarize
            level (str): Summarization level
            
        Returns:
            Dict[str, str]: Fallback summaries
        """
        summaries = {}
        
        if level == "file":
            for file_path, content in code_files.items():
                lines = len(content.split('\n'))
                summaries[file_path] = f"File: {file_path} ({lines} lines)"
        elif level == "directory":
            directory_groups = self._group_files_by_directory(code_files)
            for dir_path, dir_files in directory_groups.items():
                file_count = len(dir_files)
                total_lines = sum(len(content.split('\n')) for content in dir_files.values())
                summaries[dir_path] = f"Directory: {dir_path} ({file_count} files, {total_lines} lines)"
        elif level == "project":
            total_files = len(code_files)
            total_lines = sum(len(content.split('\n')) for content in code_files.values())
            summaries["project"] = f"Project: {total_files} files, {total_lines} lines total"
        
        return summaries
    
    def scan_entire_project(
        self, 
        code_files: Dict[str, str],
        static_findings: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive project-level scanning and analysis.
        
        Args:
            code_files (Dict[str, str]): Dictionary mapping file paths to code content
            static_findings (Optional[List[Dict]]): Static analysis findings
            
        Returns:
            Dict[str, Any]: Comprehensive project analysis report
        """
        logger.info(f"Starting project scan for {len(code_files)} files")
        
        try:
            # Calculate project complexity metrics
            complexity_metrics = self._calculate_complexity_metrics(code_files)
            logger.info(f"Project metrics: {complexity_metrics['total_files']} files, "
                       f"{complexity_metrics['total_lines']} lines")
            
            # Build RAG knowledge base for project-wide context
            logger.info("Building RAG knowledge base")
            self.rag_agent.build_knowledge_base(code_files)
            
            # Determine if hierarchical summarization is needed
            use_hierarchical = len(code_files) > self.max_files_for_direct_analysis
            
            if use_hierarchical:
                logger.info("Using hierarchical summarization for large project")
                # Use hierarchical summarization for large projects
                file_summaries = self._hierarchical_summarize(code_files, "file")
                directory_summaries = self._hierarchical_summarize(code_files, "directory")
                project_summary = self._hierarchical_summarize(code_files, "project")
            else:
                logger.info("Using direct analysis for smaller project")
                # For smaller projects, analyze directly
                file_summaries = {path: content for path, content in code_files.items()}
                directory_summaries = {}
                project_summary = {}
            
            # Query RAG for project-wide context and insights
            logger.info("Querying RAG for architectural insights")
            rag_context = self._get_project_rag_context(complexity_metrics)
            
            # Perform LLM analysis for overall project architecture and risks
            logger.info("Performing LLM architectural analysis")
            architectural_analysis = self._analyze_project_architecture(
                complexity_metrics, 
                file_summaries, 
                directory_summaries, 
                project_summary,
                static_findings,
                rag_context
            )
            
            # Generate risk assessment
            logger.info("Generating risk assessment")
            risk_assessment = self._assess_project_risks(
                complexity_metrics,
                architectural_analysis,
                static_findings
            )
            
            # Compile final project report
            project_report = {
                'scan_type': 'project',
                'complexity_metrics': complexity_metrics,
                'use_hierarchical_analysis': use_hierarchical,
                'file_summaries': file_summaries if not use_hierarchical else {},
                'directory_summaries': directory_summaries,
                'project_summary': project_summary,
                'rag_context': rag_context,
                'architectural_analysis': architectural_analysis,
                'risk_assessment': risk_assessment,
                'static_findings_summary': self._summarize_static_findings(static_findings),
                'recommendations': self._generate_project_recommendations(
                    complexity_metrics, architectural_analysis, risk_assessment
                )
            }
            
            logger.info("Project scan completed successfully")
            return project_report
            
        except Exception as e:
            logger.error(f"Error during project scan: {str(e)}")
            # Return error report
            return {
                'scan_type': 'project',
                'error': str(e),
                'partial_results': {
                    'complexity_metrics': self._calculate_complexity_metrics(code_files)
                }
            }
    
    def _get_project_rag_context(self, complexity_metrics: Dict[str, Any]) -> List[Dict]:
        """
        Query RAG for project-wide context and architectural insights.
        
        Args:
            complexity_metrics (Dict[str, Any]): Project complexity metrics
            
        Returns:
            List[Dict]: RAG context results
        """
        try:
            # Create queries based on project characteristics
            queries = [
                "architectural patterns and design decisions",
                "main entry points and application structure",
                "dependency relationships and module coupling",
                "configuration and setup components"
            ]
            
            # Add language-specific queries
            languages = complexity_metrics.get('languages', {})
            if languages.get('python', 0) > 0:
                queries.append("Python specific patterns and frameworks")
            if languages.get('java', 0) > 0:
                queries.append("Java specific patterns and frameworks")
            if languages.get('kotlin', 0) > 0:
                queries.append("Kotlin specific patterns and Android components")
            
            # Collect RAG results
            all_context = []
            for query in queries:
                context_results = self.rag_agent.query_knowledge_base(query, top_k=3)
                all_context.extend(context_results)
            
            # Remove duplicates and sort by score
            unique_context = {}
            for ctx in all_context:
                key = f"{ctx['file_path']}_{ctx['chunk_index']}"
                if key not in unique_context or ctx['score'] > unique_context[key]['score']:
                    unique_context[key] = ctx
            
            # Return top 15 most relevant contexts
            sorted_context = sorted(unique_context.values(), key=lambda x: x['score'], reverse=True)
            return sorted_context[:15]
            
        except Exception as e:
            logger.error(f"Error querying RAG context: {str(e)}")
            return []
    
    def _analyze_project_architecture(
        self,
        complexity_metrics: Dict[str, Any],
        file_summaries: Dict[str, str],
        directory_summaries: Dict[str, str],
        project_summary: Dict[str, str],
        static_findings: Optional[List[Dict]],
        rag_context: List[Dict]
    ) -> str:
        """
        Perform LLM-based architectural analysis of the project.
        
        Args:
            complexity_metrics (Dict[str, Any]): Project complexity metrics
            file_summaries (Dict[str, str]): File-level summaries
            directory_summaries (Dict[str, str]): Directory-level summaries
            project_summary (Dict[str, str]): Project-level summary
            static_findings (Optional[List[Dict]]): Static analysis findings
            rag_context (List[Dict]): RAG context results
            
        Returns:
            str: Architectural analysis from LLM
        """
        try:
            # Build comprehensive prompt for architectural analysis
            prompt = f"""Perform a comprehensive architectural analysis of this software project:

## Project Overview
- Total files: {complexity_metrics.get('total_files', 0)}
- Total lines of code: {complexity_metrics.get('total_lines', 0)}
- Languages: {dict(complexity_metrics.get('languages', {}))}
- Average file size: {complexity_metrics.get('average_file_size', 0):.1f} lines

## Largest Files (potential complexity hotspots):
{self._format_largest_files(complexity_metrics.get('largest_files', []))}

## Static Analysis Findings Summary:
{self._format_static_findings_summary(static_findings)}

## Project Structure Context:
{self._format_directory_summaries(directory_summaries)}

## RAG Context (Key architectural components):
{self._format_rag_context(rag_context)}

Please provide a detailed architectural analysis including:

1. **Architecture Overview**: Overall design patterns, architectural style, and structure
2. **Module Organization**: How components are organized and their relationships
3. **Technology Stack**: Frameworks, libraries, and technologies used
4. **Dependency Analysis**: Dependencies between modules and potential coupling issues
5. **Design Quality**: Code organization, separation of concerns, maintainability
6. **Scalability Assessment**: How well the architecture scales and potential bottlenecks
7. **Security Architecture**: Security considerations and potential vulnerabilities
8. **Performance Considerations**: Performance implications of the current architecture
9. **Technical Debt**: Areas where technical debt may be accumulating
10. **Improvement Opportunities**: Specific recommendations for architectural improvements

Focus on providing actionable insights and specific recommendations for improvement.
"""
            
            response = self.llm_orchestrator.invoke_llm(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error in architectural analysis: {str(e)}")
            return f"Architectural analysis failed: {str(e)}"
    
    def _assess_project_risks(
        self,
        complexity_metrics: Dict[str, Any],
        architectural_analysis: str,
        static_findings: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """
        Assess project-level risks based on metrics and analysis.
        
        Args:
            complexity_metrics (Dict[str, Any]): Project complexity metrics
            architectural_analysis (str): LLM architectural analysis
            static_findings (Optional[List[Dict]]): Static analysis findings
            
        Returns:
            Dict[str, Any]: Risk assessment results
        """
        risks = {
            'overall_risk_level': 'low',
            'risk_factors': [],
            'security_risks': [],
            'maintainability_risks': [],
            'performance_risks': [],
            'scalability_risks': [],
            'security_issues_count': 0
        }
        
        try:
            # Assess complexity risks
            total_files = complexity_metrics.get('total_files', 0)
            if total_files > 100:
                risks['risk_factors'].append({
                    'category': 'complexity',
                    'level': 'medium',
                    'description': f"Large project with {total_files} files"
                })
            
            average_file_size = complexity_metrics.get('average_file_size', 0)
            if average_file_size > 300:
                risks['maintainability_risks'].append({
                    'level': 'medium',
                    'description': f"Large average file size ({average_file_size:.1f} lines)"
                })
            
            # Assess static findings risks
            if static_findings:
                high_severity_count = sum(1 for f in static_findings if f.get('severity') == 'high')
                if high_severity_count > 10:
                    risks['overall_risk_level'] = 'high'
                    risks['risk_factors'].append({
                        'category': 'code_quality',
                        'level': 'high',
                        'description': f"{high_severity_count} high-severity static analysis issues"
                    })
                elif high_severity_count > 5:
                    risks['overall_risk_level'] = 'medium'
                
                # Check for security-related findings
                security_findings = [f for f in static_findings if 'security' in f.get('category', '').lower()]
                risks['security_issues_count'] = len(security_findings)
                if security_findings:
                    risks['security_risks'].extend([
                        {
                            'level': 'high' if len(security_findings) > 3 else 'medium',
                            'description': f"{len(security_findings)} security-related issues found"
                        }
                    ])
            
            # Use LLM for advanced risk assessment
            risk_analysis = self._llm_risk_analysis(complexity_metrics, architectural_analysis, static_findings)
            if risk_analysis:
                risks['llm_risk_analysis'] = risk_analysis
            
        except Exception as e:
            logger.error(f"Error in risk assessment: {str(e)}")
            risks['error'] = str(e)
        
        return risks
    
    def _llm_risk_analysis(
        self,
        complexity_metrics: Dict[str, Any],
        architectural_analysis: str,
        static_findings: Optional[List[Dict]]
    ) -> str:
        """
        Use LLM for advanced risk analysis.
        
        Args:
            complexity_metrics (Dict[str, Any]): Project complexity metrics
            architectural_analysis (str): Architectural analysis
            static_findings (Optional[List[Dict]]): Static analysis findings
            
        Returns:
            str: LLM risk analysis
        """
        try:
            prompt = f"""Based on the following project analysis, assess the overall project risks:

## Project Metrics:
- Files: {complexity_metrics.get('total_files', 0)}
- Lines: {complexity_metrics.get('total_lines', 0)}
- Languages: {dict(complexity_metrics.get('languages', {}))}

## Architectural Analysis:
{architectural_analysis[:2000]}{'...' if len(architectural_analysis) > 2000 else ''}

## Static Analysis Issues:
{len(static_findings) if static_findings else 0} total issues found

Please provide a risk assessment focusing on:
1. **Immediate Risks**: Critical issues that need immediate attention
2. **Medium-term Risks**: Issues that could become problems if not addressed
3. **Long-term Risks**: Architectural or design issues that affect future development
4. **Security Risks**: Potential security vulnerabilities or concerns
5. **Business Impact**: How these risks could affect the business or users

Provide specific, actionable recommendations for risk mitigation.
"""
            
            response = self.llm_orchestrator.invoke_llm(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error in LLM risk analysis: {str(e)}")
            return "LLM risk analysis unavailable"
    
    def _summarize_static_findings(self, static_findings: Optional[List[Dict]]) -> Dict[str, Any]:
        """
        Summarize static analysis findings for project report.
        
        Args:
            static_findings (Optional[List[Dict]]): Static analysis findings
            
        Returns:
            Dict[str, Any]: Summary of static findings
        """
        if not static_findings:
            return {'total': 0, 'by_severity': {}, 'by_category': {}}
        
        summary = {
            'total': len(static_findings),
            'by_severity': defaultdict(int),
            'by_category': defaultdict(int),
            'top_issues': []
        }
        
        for finding in static_findings:
            severity = finding.get('severity', 'unknown')
            category = finding.get('category', 'unknown')
            
            summary['by_severity'][severity] += 1
            summary['by_category'][category] += 1
        
        # Get top 10 most severe issues
        sorted_findings = sorted(
            static_findings, 
            key=lambda x: {'high': 3, 'medium': 2, 'low': 1}.get(x.get('severity'), 0), 
            reverse=True
        )
        summary['top_issues'] = sorted_findings[:10]
        
        return dict(summary)
    
    def _generate_project_recommendations(
        self,
        complexity_metrics: Dict[str, Any],
        architectural_analysis: str,
        risk_assessment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate project-level recommendations.
        
        Args:
            complexity_metrics (Dict[str, Any]): Project complexity metrics
            architectural_analysis (str): Architectural analysis
            risk_assessment (Dict[str, Any]): Risk assessment
            
        Returns:
            List[Dict[str, Any]]: List of recommendations
        """
        recommendations = []
        
        # Add complexity-based recommendations
        if complexity_metrics['total_files'] > 50:
            recommendations.append({
                'category': 'organization',
                'priority': 'medium',
                'title': 'Consider modular organization',
                'description': 'Large project would benefit from clear module boundaries and dependency management'
            })
        
        if complexity_metrics['average_file_size'] > 200:
            recommendations.append({
                'category': 'maintainability',
                'priority': 'medium',
                'title': 'Reduce file sizes',
                'description': 'Large average file size suggests opportunities for refactoring into smaller, focused modules'
            })
        
        # Add risk-based recommendations
        overall_risk = risk_assessment.get('overall_risk_level', 'low')
        if overall_risk == 'high':
            recommendations.append({
                'category': 'risk_mitigation',
                'priority': 'high',
                'title': 'Address high-risk issues immediately',
                'description': 'Multiple high-severity issues require immediate attention to prevent project risks'
            })
        
        # Add security-based recommendations
        security_issues_count = risk_assessment.get('security_issues_count', 0)
        if security_issues_count > 0:
            recommendations.append({
                'category': 'security',
                'priority': 'high',
                'title': 'Address security vulnerabilities',
                'description': f'Found {security_issues_count} security-related issues that need immediate attention'
            })
        
        # Add language-specific recommendations
        languages = complexity_metrics.get('languages', {})
        if languages.get('python', 0) > 10:
            recommendations.append({
                'category': 'python',
                'priority': 'low',
                'title': 'Consider Python code quality tools',
                'description': 'Large Python codebase would benefit from tools like black, mypy, and pytest'
            })
        
        return recommendations
    
    # Helper formatting methods
    def _format_largest_files(self, largest_files: List[Dict]) -> str:
        """Format largest files for prompt."""
        if not largest_files:
            return "No large files identified."
        
        lines = []
        for file_info in largest_files[:5]:  # Top 5
            lines.append(f"- {file_info['file']}: {file_info['lines']} lines")
        return "\n".join(lines)
    
    def _format_static_findings_summary(self, static_findings: Optional[List[Dict]]) -> str:
        """Format static findings summary for prompt."""
        if not static_findings:
            return "No static analysis findings provided."
        
        summary = self._summarize_static_findings(static_findings)
        return f"Total: {summary['total']}, By severity: {dict(summary['by_severity'])}"
    
    def _format_directory_summaries(self, directory_summaries: Dict[str, str]) -> str:
        """Format directory summaries for prompt."""
        if not directory_summaries:
            return "No directory summaries available."
        
        lines = []
        for dir_path, summary in list(directory_summaries.items())[:5]:  # Top 5
            lines.append(f"**{dir_path}**: {summary[:200]}{'...' if len(summary) > 200 else ''}")
        return "\n".join(lines)
    
    def _format_rag_context(self, rag_context: List[Dict]) -> str:
        """Format RAG context for prompt."""
        if not rag_context:
            return "No RAG context available."
        
        lines = []
        for ctx in rag_context[:5]:  # Top 5
            lines.append(f"- {ctx['file_path']}: {ctx['content'][:150]}{'...' if len(ctx['content']) > 150 else ''}")
        return "\n".join(lines) 