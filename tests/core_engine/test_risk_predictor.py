"""
Unit tests for RiskPredictor class.

Tests comprehensive risk prediction capabilities including code metrics calculation
and risk score prediction.
"""

import pytest
import unittest.mock as mock
from typing import Dict, List, Any
from collections import defaultdict

from src.core_engine.risk_predictor import RiskPredictor


class TestRiskPredictorInitialization:
    """Test RiskPredictor initialization and basic functionality."""
    
    def test_init_with_default_weights(self):
        """Test initialization with default weights."""
        predictor = RiskPredictor()
        
        assert predictor.weights['complexity'] == 0.25
        assert predictor.weights['maintainability'] == 0.20
        assert predictor.weights['size'] == 0.15
        assert predictor.weights['findings_density'] == 0.25
        assert predictor.weights['security_issues'] == 0.10
        assert predictor.weights['code_smells'] == 0.05
        assert hasattr(predictor, 'radon_available')
    
    def test_init_with_custom_weights(self):
        """Test initialization with custom weights."""
        custom_weights = {
            'complexity': 0.30,
            'maintainability': 0.25,
            'size': 0.20,
            'findings_density': 0.15,
            'security_issues': 0.05,
            'code_smells': 0.05
        }
        
        predictor = RiskPredictor(weights=custom_weights)
        
        assert predictor.weights == custom_weights
    
    def test_fallback_complexity_rank(self):
        """Test fallback complexity ranking."""
        predictor = RiskPredictor()
        
        assert predictor._fallback_complexity_rank(3) == 'A'
        assert predictor._fallback_complexity_rank(8) == 'B'
        assert predictor._fallback_complexity_rank(15) == 'C'
        assert predictor._fallback_complexity_rank(25) == 'D'
        assert predictor._fallback_complexity_rank(35) == 'E'
        assert predictor._fallback_complexity_rank(50) == 'F'
    
    def test_fallback_maintainability_rank(self):
        """Test fallback maintainability ranking."""
        predictor = RiskPredictor()
        
        assert predictor._fallback_maintainability_rank(90) == 'A'
        assert predictor._fallback_maintainability_rank(75) == 'B'
        assert predictor._fallback_maintainability_rank(60) == 'C'
        assert predictor._fallback_maintainability_rank(40) == 'D'
        assert predictor._fallback_maintainability_rank(20) == 'E'
        assert predictor._fallback_maintainability_rank(5) == 'F'


class TestCodeMetricsCalculation:
    """Test code metrics calculation functionality."""
    
    def test_calculate_code_metrics_empty_files(self):
        """Test metrics calculation with empty file dictionary."""
        predictor = RiskPredictor()
        code_files = {}
        
        metrics = predictor.calculate_code_metrics(code_files)
        
        assert metrics['total_files'] == 0
        assert metrics['total_lines'] == 0
        assert metrics['total_blank_lines'] == 0
        assert metrics['total_comment_lines'] == 0
        assert metrics['total_logical_lines'] == 0
        assert metrics['complexity']['total_cyclomatic_complexity'] == 0
        assert metrics['maintainability']['average_maintainability_index'] == 0
        assert metrics['size_metrics']['average_file_size'] == 0
    
    def test_calculate_code_metrics_single_python_file(self):
        """Test metrics calculation with single Python file."""
        predictor = RiskPredictor()
        code_files = {
            'test.py': '''def hello_world():
    """A simple function."""
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()
'''
        }
        
        metrics = predictor.calculate_code_metrics(code_files)
        
        assert metrics['total_files'] == 1
        assert metrics['total_lines'] > 0
        assert metrics['language_distribution']['python'] == 1
        assert 'test.py' in metrics['file_metrics']
        assert metrics['file_metrics']['test.py']['lines_of_code'] > 0
    
    def test_calculate_code_metrics_multiple_languages(self):
        """Test metrics calculation with multiple programming languages."""
        predictor = RiskPredictor()
        code_files = {
            'main.py': 'print("Hello from Python")\n',
            'Main.java': 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello from Java");\n    }\n}\n',
            'app.kt': 'fun main() {\n    println("Hello from Kotlin")\n}\n',
            'README.md': '# Project\nDocumentation\n'
        }
        
        metrics = predictor.calculate_code_metrics(code_files)
        
        assert metrics['total_files'] == 4
        assert metrics['language_distribution']['python'] == 1
        assert metrics['language_distribution']['java'] == 1
        assert metrics['language_distribution']['kotlin'] == 1
        assert metrics['language_distribution']['other'] == 1
    
    @mock.patch('src.core_engine.risk_predictor.RADON_AVAILABLE', False)
    def test_calculate_file_metrics_fallback_mode(self):
        """Test file metrics calculation in fallback mode (without radon)."""
        predictor = RiskPredictor()
        predictor.radon_available = False
        
        python_code = '''# This is a comment
def complex_function(x, y):
    """A complex function with multiple conditions."""
    if x > 0:
        if y > 0:
            for i in range(10):
                if i % 2 == 0:
                    print(f"Even: {i}")
                elif i % 3 == 0:
                    print(f"Multiple of 3: {i}")
                else:
                    print(f"Other: {i}")
    return x + y
'''
        
        file_metrics = predictor._calculate_file_metrics('test.py', python_code)
        
        assert file_metrics['lines_of_code'] > 0
        assert file_metrics['blank_lines'] >= 0
        assert file_metrics['comment_lines'] >= 0
        assert file_metrics['logical_lines'] >= 0
        assert file_metrics['cyclomatic_complexity'] is not None
        assert file_metrics['maintainability_index'] is not None
    
    def test_calculate_fallback_metrics(self):
        """Test fallback metrics calculation."""
        predictor = RiskPredictor()
        
        python_code = '''# Comment line
def test_function():
    if True:
        return "test"
    else:
        return "fallback"

# Another comment
'''
        
        metrics = predictor._calculate_fallback_metrics('test.py', python_code)
        
        assert 'lines_of_code' in metrics
        assert 'blank_lines' in metrics
        assert 'comment_lines' in metrics
        assert 'logical_lines' in metrics
        assert 'cyclomatic_complexity' in metrics
        assert 'maintainability_index' in metrics
        
        # Should have complexity estimate for Python files
        assert metrics['cyclomatic_complexity'] is not None
        assert metrics['maintainability_index'] is not None


class TestRiskScorePrediction:
    """Test risk score prediction functionality."""
    
    def test_predict_risk_score_minimal_project(self):
        """Test risk prediction for minimal project."""
        predictor = RiskPredictor()
        
        # Minimal project metrics
        code_metrics = {
            'total_files': 5,
            'total_lines': 200,
            'complexity': {
                'total_cyclomatic_complexity': 15,
                'average_complexity_per_function': 3.0,
                'max_complexity': 8,
                'high_complexity_functions': []
            },
            'maintainability': {
                'average_maintainability_index': 80,
                'low_maintainability_files': []
            },
            'size_metrics': {
                'average_file_size': 40,
                'files_over_threshold': 0
            }
        }
        
        risk_assessment = predictor.predict_risk_score(code_metrics)
        
        assert 'overall_risk_score' in risk_assessment
        assert 'risk_level' in risk_assessment
        assert 'component_scores' in risk_assessment
        assert 'risk_factors' in risk_assessment
        assert 'recommendations' in risk_assessment
        assert risk_assessment['risk_level'] in ['MINIMAL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        assert 0 <= risk_assessment['overall_risk_score'] <= 100
    
    def test_predict_risk_score_high_risk_project(self):
        """Test risk prediction for high-risk project."""
        predictor = RiskPredictor()
        
        # High-risk project metrics
        code_metrics = {
            'total_files': 200,
            'total_lines': 150000,
            'complexity': {
                'total_cyclomatic_complexity': 5000,
                'average_complexity_per_function': 25.0,
                'max_complexity': 80,
                'high_complexity_functions': [
                    {'file': 'complex.py', 'function': 'massive_func', 'complexity': 80}
                ]
            },
            'maintainability': {
                'average_maintainability_index': 15,
                'low_maintainability_files': [
                    {'file': 'bad.py', 'index': 10}
                ]
            },
            'size_metrics': {
                'average_file_size': 750,
                'files_over_threshold': 50
            }
        }
        
        # High-severity static findings
        static_findings = [
            {'severity': 'high', 'category': 'security', 'message': 'SQL injection vulnerability'},
            {'severity': 'high', 'category': 'security', 'message': 'Hardcoded credentials'},
            {'severity': 'medium', 'category': 'complexity', 'message': 'Function too complex'},
            {'severity': 'high', 'category': 'style', 'message': 'Code duplication'}
        ] * 10  # 40 total findings
        
        risk_assessment = predictor.predict_risk_score(code_metrics, static_findings)
        
        assert risk_assessment['overall_risk_score'] > 50  # Should be high risk
        assert risk_assessment['risk_level'] in ['MEDIUM', 'HIGH', 'CRITICAL']
        assert len(risk_assessment['risk_factors']) > 0
        assert len(risk_assessment['recommendations']) > 0
    
    def test_predict_risk_score_with_static_findings(self):
        """Test risk prediction with various static analysis findings."""
        predictor = RiskPredictor()
        predictor._estimated_lines = 1000  # Set estimated lines for density calculation
        
        code_metrics = {
            'total_files': 10,
            'total_lines': 1000,
            'complexity': {'total_cyclomatic_complexity': 50},
            'maintainability': {'average_maintainability_index': 70},
            'size_metrics': {'average_file_size': 100, 'files_over_threshold': 0}
        }
        
        # Mixed severity findings
        static_findings = [
            {'severity': 'high', 'category': 'security', 'message': 'Security issue'},
            {'severity': 'medium', 'category': 'style', 'message': 'Style issue'},
            {'severity': 'low', 'category': 'complexity', 'message': 'Minor complexity'},
            {'severity': 'high', 'category': 'maintainability', 'message': 'Hard to maintain'}
        ]
        
        risk_assessment = predictor.predict_risk_score(code_metrics, static_findings)
        
        assert 'component_scores' in risk_assessment
        assert 'findings_density_score' in risk_assessment['component_scores']
        assert 'security_score' in risk_assessment['component_scores']
        assert 'code_smell_score' in risk_assessment['component_scores']
    
    def test_calculate_complexity_risk(self):
        """Test complexity risk calculation."""
        predictor = RiskPredictor()
        
        # High complexity metrics
        code_metrics = {
            'total_files': 50,
            'complexity': {
                'total_cyclomatic_complexity': 2000,
                'average_complexity_per_function': 30.0,
                'max_complexity': 60,
                'high_complexity_functions': [
                    {'complexity': 15}, {'complexity': 25}, {'complexity': 35}
                ]
            }
        }
        
        complexity_risk = predictor._calculate_complexity_risk(code_metrics)
        
        assert 0 <= complexity_risk <= 100
        assert complexity_risk > 50  # Should be high due to high complexity values
    
    def test_calculate_maintainability_risk(self):
        """Test maintainability risk calculation."""
        predictor = RiskPredictor()
        
        # Low maintainability metrics
        code_metrics = {
            'total_files': 20,
            'maintainability': {
                'average_maintainability_index': 25,  # Low maintainability
                'low_maintainability_files': [
                    {'file': 'bad1.py', 'index': 15},
                    {'file': 'bad2.py', 'index': 18}
                ]
            }
        }
        
        maintainability_risk = predictor._calculate_maintainability_risk(code_metrics)
        
        assert 0 <= maintainability_risk <= 100
        assert maintainability_risk > 50  # Should be high due to low maintainability
    
    def test_calculate_size_risk(self):
        """Test size-based risk calculation."""
        predictor = RiskPredictor()
        
        # Large project metrics
        code_metrics = {
            'total_files': 100,
            'total_lines': 120000,  # Large project
            'size_metrics': {
                'average_file_size': 1200,  # Large files
                'files_over_threshold': 30  # Many large files
            }
        }
        
        size_risk = predictor._calculate_size_risk(code_metrics)
        
        assert 0 <= size_risk <= 100
        assert size_risk > 50  # Should be high due to large size
    
    def test_analyze_static_findings(self):
        """Test static findings analysis."""
        predictor = RiskPredictor()
        predictor._estimated_lines = 2000
        
        # Various types of findings
        static_findings = [
            {'severity': 'high', 'category': 'security', 'message': 'SQL injection'},
            {'severity': 'high', 'category': 'security', 'message': 'XSS vulnerability'},
            {'severity': 'medium', 'category': 'style', 'message': 'Naming convention'},
            {'severity': 'low', 'category': 'complexity', 'message': 'Function length'},
            {'severity': 'medium', 'category': 'maintainability', 'message': 'Code duplication'}
        ]
        
        findings_analysis = predictor._analyze_static_findings(static_findings)
        
        assert 'density_score' in findings_analysis
        assert 'security_score' in findings_analysis
        assert 'code_smell_score' in findings_analysis
        assert findings_analysis['security_score'] > 0  # Should detect security issues
    
    def test_determine_risk_level(self):
        """Test risk level determination based on score."""
        predictor = RiskPredictor()
        
        assert predictor._determine_risk_level(90) == 'CRITICAL'
        assert predictor._determine_risk_level(70) == 'HIGH'
        assert predictor._determine_risk_level(50) == 'MEDIUM'
        assert predictor._determine_risk_level(30) == 'LOW'
        assert predictor._determine_risk_level(10) == 'MINIMAL'
    
    def test_identify_risk_factors(self):
        """Test risk factor identification."""
        predictor = RiskPredictor()
        
        code_metrics = {
            'total_files': 50,
            'complexity': {
                'high_complexity_functions': [
                    {'complexity': 15}, {'complexity': 20}
                ]
            },
            'maintainability': {
                'low_maintainability_files': [
                    {'file': 'bad.py', 'index': 15}
                ]
            },
            'size_metrics': {
                'files_over_threshold': 10
            }
        }
        
        component_scores = {
            'complexity_score': 70.0,
            'maintainability_score': 65.0,
            'size_score': 55.0,
            'findings_density_score': 45.0,
            'security_score': 50.0,
            'code_smell_score': 30.0
        }
        
        static_findings = [
            {'category': 'security', 'message': 'Security issue'}
        ]
        
        risk_factors = predictor._identify_risk_factors(code_metrics, static_findings, component_scores)
        
        assert len(risk_factors) > 0
        assert any('complexity' in factor.lower() for factor in risk_factors)
        assert any('maintainability' in factor.lower() for factor in risk_factors)
        assert any('security' in factor.lower() for factor in risk_factors)
    
    def test_generate_risk_recommendations(self):
        """Test risk recommendation generation."""
        predictor = RiskPredictor()
        
        component_scores = {
            'complexity_score': 80.0,  # High complexity
            'maintainability_score': 70.0,  # High maintainability risk
            'size_score': 60.0,  # Medium size risk
            'findings_density_score': 30.0,
            'security_score': 90.0,  # Critical security risk
            'code_smell_score': 50.0  # Medium code smell risk
        }
        
        risk_factors = ['High complexity functions', 'Security vulnerabilities']
        
        recommendations = predictor._generate_risk_recommendations(component_scores, risk_factors)
        
        assert len(recommendations) > 0
        
        # Check that recommendations cover major risk areas
        categories = [rec['category'] for rec in recommendations]
        assert 'Complexity' in categories
        assert 'Maintainability' in categories
        assert 'Security' in categories
        
        # Check priority levels
        priorities = [rec['priority'] for rec in recommendations]
        assert 'CRITICAL' in priorities or 'HIGH' in priorities  # Should have high-priority items


class TestErrorHandling:
    """Test error handling in RiskPredictor."""
    
    def test_calculate_file_metrics_with_invalid_content(self):
        """Test file metrics calculation with invalid content."""
        predictor = RiskPredictor()
        
        # This should not crash, but handle gracefully
        file_metrics = predictor._calculate_file_metrics('test.py', None)
        
        # Should have some basic structure even with errors
        assert 'lines_of_code' in file_metrics
        assert 'logical_lines' in file_metrics
    
    def test_predict_risk_score_with_empty_metrics(self):
        """Test risk prediction with empty/minimal metrics."""
        predictor = RiskPredictor()
        
        # Empty metrics dictionary
        code_metrics = {
            'total_files': 0,
            'total_lines': 0
        }
        
        risk_assessment = predictor.predict_risk_score(code_metrics)
        
        # Should still return valid structure
        assert 'overall_risk_score' in risk_assessment
        assert 'risk_level' in risk_assessment
        assert 'component_scores' in risk_assessment
    
    @mock.patch('src.core_engine.risk_predictor.logger')
    def test_logging_in_risk_prediction(self, mock_logger):
        """Test that appropriate logging occurs during risk prediction."""
        predictor = RiskPredictor()
        
        code_metrics = {
            'total_files': 10,
            'total_lines': 1000,
            'complexity': {'total_cyclomatic_complexity': 50},
            'maintainability': {'average_maintainability_index': 70},
            'size_metrics': {'average_file_size': 100}
        }
        
        predictor.predict_risk_score(code_metrics)
        
        # Should have logged the start and completion
        mock_logger.info.assert_called()


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases."""
    
    def test_complete_risk_assessment_workflow(self):
        """Test complete workflow from code files to risk assessment."""
        predictor = RiskPredictor()
        
        # Sample project files
        code_files = {
            'main.py': '''#!/usr/bin/env python3
"""Main application module."""

import os
import sys
from typing import List, Dict

class DataProcessor:
    """Processes data with various methods."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.data = []
    
    def process_data(self, input_data: List) -> List:
        """Process input data with complex logic."""
        results = []
        for item in input_data:
            if item and isinstance(item, dict):
                if 'type' in item:
                    if item['type'] == 'A':
                        processed = self._process_type_a(item)
                    elif item['type'] == 'B':
                        processed = self._process_type_b(item)
                    else:
                        processed = self._process_default(item)
                    results.append(processed)
        return results
    
    def _process_type_a(self, item):
        # Complex processing with multiple conditions
        if item.get('priority', 0) > 5:
            for i in range(item.get('iterations', 10)):
                if i % 2 == 0:
                    item['processed'] = True
        return item
    
    def _process_type_b(self, item):
        return {'status': 'processed', 'data': item}
    
    def _process_default(self, item):
        return item

if __name__ == "__main__":
    processor = DataProcessor({'debug': True})
    result = processor.process_data([{'type': 'A', 'priority': 8}])
    print(result)
''',
            'utils.py': '''"""Utility functions."""

def calculate_complexity(data):
    """Calculate complexity score."""
    if not data:
        return 0
    
    score = 0
    for item in data:
        if item > 10:
            score += 2
        elif item > 5:
            score += 1
    return score

def validate_input(value):
    """Validate input value."""
    return value is not None and len(str(value)) > 0
''',
            'config.py': '''"""Configuration module."""

import os

DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
SECRET_KEY = "hardcoded-secret-key"  # Security issue!

class Config:
    def __init__(self):
        self.debug = DEBUG
        self.db_url = DATABASE_URL
'''
        }
        
        # Calculate comprehensive metrics
        code_metrics = predictor.calculate_code_metrics(code_files)
        
        # Create mock static findings
        static_findings = [
            {
                'severity': 'high',
                'category': 'security',
                'message': 'Hardcoded secret key found',
                'file': 'config.py',
                'line': 7
            },
            {
                'severity': 'medium',
                'category': 'complexity',
                'message': 'Function has high cyclomatic complexity',
                'file': 'main.py',
                'line': 15
            },
            {
                'severity': 'low',
                'category': 'style',
                'message': 'Missing docstring',
                'file': 'utils.py',
                'line': 20
            }
        ]
        
        # Predict risk score
        risk_assessment = predictor.predict_risk_score(
            code_metrics=code_metrics,
            static_findings=static_findings,
            architectural_analysis="Sample architectural analysis of a Python application with data processing capabilities."
        )
        
        # Validate complete assessment
        assert risk_assessment['overall_risk_score'] >= 0
        assert risk_assessment['risk_level'] in ['MINIMAL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        assert 'component_scores' in risk_assessment
        assert 'risk_factors' in risk_assessment
        assert 'recommendations' in risk_assessment
        assert 'calculation_metadata' in risk_assessment
        
        # Should detect the security issue
        assert risk_assessment['component_scores']['security_score'] > 0
        
        # Should have meaningful recommendations
        assert len(risk_assessment['recommendations']) > 0


if __name__ == '__main__':
    pytest.main([__file__]) 