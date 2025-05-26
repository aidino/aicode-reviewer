"""
Risk Prediction Module for AI Code Review System.

This module implements comprehensive risk prediction capabilities, combining
code complexity metrics with static analysis findings to assess project health
and predict potential maintenance risks.
"""

import logging
import math
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from collections import defaultdict, Counter
import tempfile
import os

try:
    from radon.complexity import cc_visit, cc_rank
    from radon.metrics import mi_visit, mi_rank
    from radon.raw import analyze
    RADON_AVAILABLE = True
except ImportError:
    RADON_AVAILABLE = False
    logging.warning("Radon not available. Code complexity metrics will use fallback calculations.")

# Configure logging
logger = logging.getLogger(__name__)


class RiskPredictor:
    """
    Predicts project risk scores based on code complexity metrics and static analysis findings.
    
    This class combines various metrics including:
    - Cyclomatic complexity (radon)
    - Maintainability index (radon)
    - Raw code metrics (lines of code, etc.)
    - Static analysis findings density
    - Code quality patterns
    """
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize the RiskPredictor.
        
        Args:
            weights (Optional[Dict[str, float]]): Custom weights for risk calculation components
        """
        # Default weights for different risk factors
        self.weights = weights or {
            'complexity': 0.25,      # Cyclomatic complexity impact
            'maintainability': 0.20, # Maintainability index impact
            'size': 0.15,           # Code size impact
            'findings_density': 0.25, # Static analysis findings density
            'security_issues': 0.10, # Security-related findings
            'code_smells': 0.05     # Code smell findings
        }
        
        self.radon_available = RADON_AVAILABLE
        logger.info(f"RiskPredictor initialized with radon available: {self.radon_available}")
    
    def calculate_code_metrics(self, code_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Calculate comprehensive code metrics for project files.
        
        Args:
            code_files (Dict[str, str]): Dictionary mapping file paths to code content
            
        Returns:
            Dict[str, Any]: Comprehensive code metrics including complexity, maintainability, and size metrics
        """
        logger.info(f"Calculating code metrics for {len(code_files)} files")
        
        metrics = {
            'total_files': len(code_files),
            'total_lines': 0,
            'total_blank_lines': 0,
            'total_comment_lines': 0,
            'total_logical_lines': 0,
            'complexity': {
                'total_cyclomatic_complexity': 0,
                'average_complexity_per_function': 0,
                'max_complexity': 0,
                'high_complexity_functions': [],
                'complexity_distribution': {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0}
            },
            'maintainability': {
                'average_maintainability_index': 0,
                'low_maintainability_files': [],
                'maintainability_distribution': {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0}
            },
            'size_metrics': {
                'largest_files': [],
                'average_file_size': 0,
                'files_over_threshold': 0  # Files over 500 lines
            },
            'language_distribution': defaultdict(int),
            'file_metrics': {}
        }
        
        function_complexities = []
        file_maintainabilities = []
        file_sizes = []
        
        for file_path, content in code_files.items():
            file_metrics = self._calculate_file_metrics(file_path, content)
            metrics['file_metrics'][file_path] = file_metrics
            
            # Aggregate metrics
            metrics['total_lines'] += file_metrics['lines_of_code']
            metrics['total_blank_lines'] += file_metrics['blank_lines']
            metrics['total_comment_lines'] += file_metrics['comment_lines']
            metrics['total_logical_lines'] += file_metrics['logical_lines']
            
            # Complexity metrics
            if file_metrics['cyclomatic_complexity']:
                metrics['complexity']['total_cyclomatic_complexity'] += file_metrics['cyclomatic_complexity']['total']
                function_complexities.extend(file_metrics['cyclomatic_complexity']['functions'])
                
                # Track complexity distribution
                for func in file_metrics['cyclomatic_complexity']['functions']:
                    rank = cc_rank(func['complexity']) if self.radon_available else self._fallback_complexity_rank(func['complexity'])
                    metrics['complexity']['complexity_distribution'][rank] += 1
                    
                    if func['complexity'] > 10:  # High complexity threshold
                        metrics['complexity']['high_complexity_functions'].append({
                            'file': file_path,
                            'function': func['name'],
                            'complexity': func['complexity'],
                            'rank': rank
                        })
            
            # Maintainability metrics
            if file_metrics['maintainability_index'] is not None:
                file_maintainabilities.append(file_metrics['maintainability_index'])
                rank = mi_rank(file_metrics['maintainability_index']) if self.radon_available else self._fallback_maintainability_rank(file_metrics['maintainability_index'])
                metrics['maintainability']['maintainability_distribution'][rank] += 1
                
                if file_metrics['maintainability_index'] < 20:  # Low maintainability threshold
                    metrics['maintainability']['low_maintainability_files'].append({
                        'file': file_path,
                        'index': file_metrics['maintainability_index'],
                        'rank': rank
                    })
            
            # Size metrics
            file_sizes.append((file_path, file_metrics['lines_of_code']))
            if file_metrics['lines_of_code'] > 500:
                metrics['size_metrics']['files_over_threshold'] += 1
            
            # Language distribution
            ext = Path(file_path).suffix.lower()
            if ext == '.py':
                metrics['language_distribution']['python'] += 1
            elif ext == '.java':
                metrics['language_distribution']['java'] += 1
            elif ext in ['.kt', '.kts']:
                metrics['language_distribution']['kotlin'] += 1
            else:
                metrics['language_distribution']['other'] += 1
        
        # Calculate averages and summaries
        if function_complexities:
            metrics['complexity']['average_complexity_per_function'] = sum(f['complexity'] for f in function_complexities) / len(function_complexities)
            metrics['complexity']['max_complexity'] = max(f['complexity'] for f in function_complexities)
        
        if file_maintainabilities:
            metrics['maintainability']['average_maintainability_index'] = sum(file_maintainabilities) / len(file_maintainabilities)
        
        if file_sizes:
            metrics['size_metrics']['average_file_size'] = sum(size for _, size in file_sizes) / len(file_sizes)
            # Sort by size and get top 10 largest files
            file_sizes.sort(key=lambda x: x[1], reverse=True)
            metrics['size_metrics']['largest_files'] = [
                {'file': path, 'lines': size} for path, size in file_sizes[:10]
            ]
        
        logger.info(f"Code metrics calculated: {metrics['total_lines']} total lines, "
                   f"{metrics['complexity']['total_cyclomatic_complexity']} total complexity")
        
        return metrics
    
    def _calculate_file_metrics(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Calculate metrics for a single file.
        
        Args:
            file_path (str): Path to the file
            content (str): File content
            
        Returns:
            Dict[str, Any]: File-specific metrics
        """
        file_metrics = {
            'lines_of_code': 0,
            'blank_lines': 0,
            'comment_lines': 0,
            'logical_lines': 0,
            'cyclomatic_complexity': None,
            'maintainability_index': None
        }
        
        try:
            if self.radon_available:
                # Use radon for accurate metrics
                file_metrics.update(self._calculate_radon_metrics(file_path, content))
            else:
                # Use fallback calculations
                file_metrics.update(self._calculate_fallback_metrics(file_path, content))
                
        except Exception as e:
            logger.warning(f"Error calculating metrics for {file_path}: {str(e)}")
            # Use basic line count as fallback
            if content is not None:
                lines = content.split('\n')
                file_metrics['lines_of_code'] = len(lines)
                file_metrics['logical_lines'] = len([line for line in lines if line.strip()])
            else:
                file_metrics['lines_of_code'] = 0
                file_metrics['logical_lines'] = 0
        
        return file_metrics
    
    def _calculate_radon_metrics(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Calculate metrics using radon library.
        
        Args:
            file_path (str): Path to the file
            content (str): File content
            
        Returns:
            Dict[str, Any]: Radon-calculated metrics
        """
        metrics = {}
        
        try:
            # Raw metrics (lines of code, etc.)
            raw_metrics = analyze(content)
            metrics.update({
                'lines_of_code': raw_metrics.loc,
                'blank_lines': raw_metrics.blank,
                'comment_lines': raw_metrics.comments,
                'logical_lines': raw_metrics.lloc
            })
            
            # Cyclomatic complexity
            if Path(file_path).suffix.lower() == '.py':
                complexity_results = cc_visit(content)
                if complexity_results:
                    functions = []
                    total_complexity = 0
                    
                    for result in complexity_results:
                        func_complexity = {
                            'name': result.name,
                            'complexity': result.complexity,
                            'line_number': result.lineno,
                            'rank': cc_rank(result.complexity)
                        }
                        functions.append(func_complexity)
                        total_complexity += result.complexity
                    
                    metrics['cyclomatic_complexity'] = {
                        'total': total_complexity,
                        'functions': functions,
                        'average': total_complexity / len(functions) if functions else 0
                    }
                
                # Maintainability index
                mi_results = mi_visit(content, multi=True)
                if mi_results:
                    # Use the overall maintainability index
                    metrics['maintainability_index'] = mi_results.mi
                    
        except Exception as e:
            logger.warning(f"Error in radon metrics calculation for {file_path}: {str(e)}")
            # Fall back to basic calculations
            metrics.update(self._calculate_fallback_metrics(file_path, content))
        
        return metrics
    
    def _calculate_fallback_metrics(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Calculate basic metrics without radon (fallback).
        
        Args:
            file_path (str): Path to the file
            content (str): File content
            
        Returns:
            Dict[str, Any]: Basic calculated metrics
        """
        if content is None:
            return {
                'lines_of_code': 0,
                'blank_lines': 0,
                'comment_lines': 0,
                'logical_lines': 0,
                'cyclomatic_complexity': None,
                'maintainability_index': None
            }
            
        lines = content.split('\n')
        
        blank_lines = 0
        comment_lines = 0
        logical_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith('#') or stripped.startswith('//'):
                comment_lines += 1
            else:
                logical_lines += 1
        
        # Basic complexity estimation for Python files
        complexity_estimate = None
        if Path(file_path).suffix.lower() == '.py':
            # Count decision points as a rough complexity estimate
            decision_keywords = ['if', 'elif', 'for', 'while', 'except', 'and', 'or']
            complexity_count = 1  # Base complexity
            for line in lines:
                stripped = line.strip()
                for keyword in decision_keywords:
                    complexity_count += stripped.count(f' {keyword} ') + stripped.count(f'{keyword} ')
            
            complexity_estimate = {
                'total': complexity_count,
                'functions': [{'name': 'estimated', 'complexity': complexity_count, 'line_number': 1}],
                'average': complexity_count
            }
        
        # Basic maintainability estimate (simplified formula)
        maintainability_estimate = None
        if logical_lines > 0:
            # Simplified maintainability: higher for smaller files with fewer comments
            comment_ratio = comment_lines / logical_lines if logical_lines > 0 else 0
            size_penalty = max(0, 100 - logical_lines / 10)  # Penalty for large files
            maintainability_estimate = min(100, size_penalty + comment_ratio * 20)
        
        return {
            'lines_of_code': len(lines),
            'blank_lines': blank_lines,
            'comment_lines': comment_lines,
            'logical_lines': logical_lines,
            'cyclomatic_complexity': complexity_estimate,
            'maintainability_index': maintainability_estimate
        }
    
    def _fallback_complexity_rank(self, complexity: int) -> str:
        """Fallback complexity ranking when radon is not available."""
        if complexity <= 5:
            return 'A'
        elif complexity <= 10:
            return 'B'
        elif complexity <= 20:
            return 'C'
        elif complexity <= 30:
            return 'D'
        elif complexity <= 40:
            return 'E'
        else:
            return 'F'
    
    def _fallback_maintainability_rank(self, mi: float) -> str:
        """Fallback maintainability ranking when radon is not available."""
        if mi >= 85:
            return 'A'
        elif mi >= 70:
            return 'B'
        elif mi >= 50:
            return 'C'
        elif mi >= 30:
            return 'D'
        elif mi >= 10:
            return 'E'
        else:
            return 'F'
    
    def predict_risk_score(
        self,
        code_metrics: Dict[str, Any],
        static_findings: Optional[List[Dict]] = None,
        architectural_analysis: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predict project risk score based on code metrics and static analysis findings.
        
        Args:
            code_metrics (Dict[str, Any]): Code metrics from calculate_code_metrics
            static_findings (Optional[List[Dict]]): Static analysis findings
            architectural_analysis (Optional[str]): LLM architectural analysis text
            
        Returns:
            Dict[str, Any]: Risk assessment including overall score and component scores
        """
        logger.info("Calculating project risk score")
        
        # Initialize component scores
        component_scores = {
            'complexity_score': 0.0,
            'maintainability_score': 0.0,
            'size_score': 0.0,
            'findings_density_score': 0.0,
            'security_score': 0.0,
            'code_smell_score': 0.0
        }
        
        # Calculate complexity score (0-100, higher = more risk)
        component_scores['complexity_score'] = self._calculate_complexity_risk(code_metrics)
        
        # Calculate maintainability score (0-100, higher = more risk)
        component_scores['maintainability_score'] = self._calculate_maintainability_risk(code_metrics)
        
        # Calculate size-based risk score (0-100, higher = more risk)
        component_scores['size_score'] = self._calculate_size_risk(code_metrics)
        
        # Calculate findings-based risk scores
        if static_findings:
            findings_analysis = self._analyze_static_findings(static_findings)
            component_scores['findings_density_score'] = findings_analysis['density_score']
            component_scores['security_score'] = findings_analysis['security_score']
            component_scores['code_smell_score'] = findings_analysis['code_smell_score']
        
        # Calculate weighted overall risk score
        overall_score = sum(
            component_scores[component] * self.weights[component.replace('_score', '')]
            for component in component_scores
            if component.replace('_score', '') in self.weights
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_score)
        
        # Generate risk factors and recommendations
        risk_factors = self._identify_risk_factors(code_metrics, static_findings, component_scores)
        recommendations = self._generate_risk_recommendations(component_scores, risk_factors)
        
        risk_assessment = {
            'overall_risk_score': round(overall_score, 2),
            'risk_level': risk_level,
            'component_scores': {k: round(v, 2) for k, v in component_scores.items()},
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'weights_used': self.weights.copy(),
            'calculation_metadata': {
                'total_files_analyzed': code_metrics.get('total_files', 0),
                'total_lines_analyzed': code_metrics.get('total_lines', 0),
                'static_findings_count': len(static_findings) if static_findings else 0,
                'radon_available': self.radon_available
            }
        }
        
        logger.info(f"Risk assessment complete: {risk_level} risk (score: {overall_score:.2f})")
        return risk_assessment
    
    def _calculate_complexity_risk(self, code_metrics: Dict[str, Any]) -> float:
        """Calculate risk score based on cyclomatic complexity."""
        complexity_data = code_metrics.get('complexity', {})
        
        if not complexity_data.get('total_cyclomatic_complexity'):
            return 0.0
        
        total_complexity = complexity_data.get('total_cyclomatic_complexity', 0)
        total_functions = len(complexity_data.get('high_complexity_functions', []))
        avg_complexity = complexity_data.get('average_complexity_per_function', 0)
        max_complexity = complexity_data.get('max_complexity', 0)
        
        # Normalize scores (0-100)
        avg_complexity_score = min(100, (avg_complexity / 20) * 100)  # 20+ avg complexity = 100% risk
        max_complexity_score = min(100, (max_complexity / 50) * 100)  # 50+ max complexity = 100% risk
        high_complexity_ratio = (total_functions / code_metrics.get('total_files', 1)) * 100
        
        # Weighted combination
        complexity_risk = (avg_complexity_score * 0.4 + max_complexity_score * 0.4 + high_complexity_ratio * 0.2)
        return min(100, complexity_risk)
    
    def _calculate_maintainability_risk(self, code_metrics: Dict[str, Any]) -> float:
        """Calculate risk score based on maintainability index."""
        maintainability_data = code_metrics.get('maintainability', {})
        
        avg_mi = maintainability_data.get('average_maintainability_index', 100)
        low_mi_files = len(maintainability_data.get('low_maintainability_files', []))
        
        if avg_mi is None:
            return 0.0
        
        # Invert maintainability index (higher MI = lower risk)
        avg_mi_risk = max(0, 100 - avg_mi)
        total_files = code_metrics.get('total_files', 1)
        low_mi_ratio = (low_mi_files / max(1, total_files)) * 100
        
        # Weighted combination
        maintainability_risk = (avg_mi_risk * 0.7 + low_mi_ratio * 0.3)
        return min(100, maintainability_risk)
    
    def _calculate_size_risk(self, code_metrics: Dict[str, Any]) -> float:
        """Calculate risk score based on project size metrics."""
        size_data = code_metrics.get('size_metrics', {})
        
        total_lines = code_metrics.get('total_lines', 0)
        avg_file_size = size_data.get('average_file_size', 0)
        large_files_count = size_data.get('files_over_threshold', 0)
        total_files = code_metrics.get('total_files', 1)
        
        # Size-based risk factors
        total_lines_risk = min(100, (total_lines / 100000) * 100)  # 100k+ lines = 100% risk
        avg_file_size_risk = min(100, (avg_file_size / 1000) * 100)  # 1000+ avg lines = 100% risk
        large_files_ratio = (large_files_count / max(1, total_files)) * 100
        
        # Weighted combination
        size_risk = (total_lines_risk * 0.3 + avg_file_size_risk * 0.4 + large_files_ratio * 0.3)
        return min(100, size_risk)
    
    def _analyze_static_findings(self, static_findings: List[Dict]) -> Dict[str, float]:
        """Analyze static analysis findings for risk scoring."""
        if not static_findings:
            return {'density_score': 0.0, 'security_score': 0.0, 'code_smell_score': 0.0}
        
        total_findings = len(static_findings)
        severity_counts = Counter(finding.get('severity', 'low') for finding in static_findings)
        category_counts = Counter(finding.get('category', 'other') for finding in static_findings)
        
        # Calculate findings density (findings per 1000 lines)
        # Assuming this will be called with code_metrics available
        findings_per_1k_lines = (total_findings / max(1, self._estimated_lines)) * 1000 if hasattr(self, '_estimated_lines') else total_findings
        density_score = min(100, findings_per_1k_lines * 10)  # 10+ findings per 1k lines = 100% risk
        
        # Security risk score
        security_findings = sum(1 for finding in static_findings 
                              if 'security' in finding.get('category', '').lower() or 
                                 'vulnerability' in finding.get('message', '').lower())
        security_score = min(100, (security_findings / max(1, total_findings)) * 200)  # 50%+ security findings = 100% risk
        
        # Code smell score (based on code quality categories)
        code_smell_categories = ['style', 'complexity', 'duplication', 'maintainability']
        code_smell_findings = sum(1 for finding in static_findings 
                                if any(cat in finding.get('category', '').lower() for cat in code_smell_categories))
        code_smell_score = min(100, (code_smell_findings / max(1, total_findings)) * 150)  # 67%+ code smells = 100% risk
        
        return {
            'density_score': density_score,
            'security_score': security_score,
            'code_smell_score': code_smell_score
        }
    
    def _determine_risk_level(self, overall_score: float) -> str:
        """Determine risk level based on overall score."""
        if overall_score >= 80:
            return 'CRITICAL'
        elif overall_score >= 60:
            return 'HIGH'
        elif overall_score >= 40:
            return 'MEDIUM'
        elif overall_score >= 20:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _identify_risk_factors(
        self, 
        code_metrics: Dict[str, Any], 
        static_findings: Optional[List[Dict]], 
        component_scores: Dict[str, float]
    ) -> List[str]:
        """Identify specific risk factors contributing to the overall score."""
        risk_factors = []
        
        # Complexity risks
        if component_scores['complexity_score'] > 60:
            complexity_data = code_metrics.get('complexity', {})
            high_complexity_funcs = len(complexity_data.get('high_complexity_functions', []))
            if high_complexity_funcs > 0:
                risk_factors.append(f"High cyclomatic complexity: {high_complexity_funcs} functions with complexity > 10")
        
        # Maintainability risks
        if component_scores['maintainability_score'] > 60:
            maintainability_data = code_metrics.get('maintainability', {})
            low_mi_files = len(maintainability_data.get('low_maintainability_files', []))
            if low_mi_files > 0:
                risk_factors.append(f"Low maintainability: {low_mi_files} files with maintainability index < 20")
        
        # Size risks
        if component_scores['size_score'] > 60:
            size_data = code_metrics.get('size_metrics', {})
            large_files = size_data.get('files_over_threshold', 0)
            if large_files > 0:
                risk_factors.append(f"Large files: {large_files} files exceed 500 lines")
        
        # Static analysis risks
        if static_findings and component_scores['findings_density_score'] > 40:
            risk_factors.append(f"High issue density: {len(static_findings)} static analysis findings detected")
        
        if static_findings and component_scores['security_score'] > 40:
            security_count = sum(1 for f in static_findings if 'security' in f.get('category', '').lower())
            if security_count > 0:
                risk_factors.append(f"Security concerns: {security_count} potential security issues found")
        
        return risk_factors
    
    def _generate_risk_recommendations(
        self, 
        component_scores: Dict[str, float], 
        risk_factors: List[str]
    ) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on risk assessment."""
        recommendations = []
        
        # Complexity recommendations
        if component_scores['complexity_score'] > 40:
            recommendations.append({
                'category': 'Complexity',
                'priority': 'HIGH' if component_scores['complexity_score'] > 60 else 'MEDIUM',
                'recommendation': 'Refactor high-complexity functions to improve readability and maintainability',
                'action': 'Break down complex functions into smaller, single-purpose functions'
            })
        
        # Maintainability recommendations
        if component_scores['maintainability_score'] > 40:
            recommendations.append({
                'category': 'Maintainability',
                'priority': 'HIGH' if component_scores['maintainability_score'] > 60 else 'MEDIUM',
                'recommendation': 'Improve code maintainability through better documentation and structure',
                'action': 'Add comprehensive docstrings, reduce code duplication, and improve naming conventions'
            })
        
        # Size recommendations
        if component_scores['size_score'] > 40:
            recommendations.append({
                'category': 'Code Organization',
                'priority': 'MEDIUM',
                'recommendation': 'Split large files and reorganize code structure',
                'action': 'Break large files into smaller modules and extract reusable components'
            })
        
        # Security recommendations
        if component_scores['security_score'] > 30:
            recommendations.append({
                'category': 'Security',
                'priority': 'CRITICAL' if component_scores['security_score'] > 60 else 'HIGH',
                'recommendation': 'Address security vulnerabilities and implement security best practices',
                'action': 'Review and fix security issues, add input validation, and follow secure coding guidelines'
            })
        
        # Code quality recommendations
        if component_scores['code_smell_score'] > 40:
            recommendations.append({
                'category': 'Code Quality',
                'priority': 'MEDIUM',
                'recommendation': 'Improve overall code quality and consistency',
                'action': 'Apply consistent coding standards, remove code duplication, and improve error handling'
            })
        
        return recommendations 