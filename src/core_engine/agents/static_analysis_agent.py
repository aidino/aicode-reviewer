"""
StaticAnalysisAgent for AI Code Review System.

This module implements the StaticAnalysisAgent responsible for performing
rule-based static analysis on Abstract Syntax Trees (ASTs) using Tree-sitter
queries to identify potential code quality issues.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple

try:
    import tree_sitter
    from tree_sitter import Language, Node
except ImportError:
    tree_sitter = None
    Language = None
    Node = None

# Configure logging
logger = logging.getLogger(__name__)


class StaticAnalysisAgent:
    """
    Agent responsible for performing static analysis on code ASTs.
    
    This agent handles:
    - Loading Tree-sitter language grammars for queries
    - Executing Tree-sitter queries to find code patterns
    - Implementing rule-based checks for code quality issues
    - Generating structured findings with severity levels
    """
    
    def __init__(self):
        """
        Initialize the StaticAnalysisAgent.
        
        Sets up Tree-sitter language support and loads Python grammar
        for executing static analysis queries.
        
        Raises:
            ImportError: If tree-sitter is not installed
            Exception: If Python language grammar cannot be loaded
        """
        if tree_sitter is None:
            raise ImportError(
                "tree-sitter is not installed. Please install it with: pip install tree-sitter"
            )
        
        self.languages = {}
        self.supported_languages = ['python']
        
        # Initialize Python language for queries
        self._initialize_python_language()
        
        logger.info(f"StaticAnalysisAgent initialized with languages: {self.supported_languages}")
    
    def _initialize_python_language(self) -> None:
        """
        Initialize Python language grammar for Tree-sitter queries.
        
        Attempts to load Python grammar using multiple methods.
        
        Raises:
            Exception: If Python language grammar cannot be loaded
        """
        try:
            # Try to load from tree-sitter-python package
            try:
                from tree_sitter_python import language
                lang_capsule = language()
                # Wrap PyCapsule with Language object for newer tree-sitter versions
                self.languages['python'] = Language(lang_capsule)
                logger.info("Successfully loaded Python language grammar for static analysis")
                return
            except ImportError:
                logger.debug("tree-sitter-python package not found")
            
            # If we can't load the language, we'll still continue but with limited functionality
            logger.warning("Could not load Python language grammar. Static analysis will be limited.")
            self.languages['python'] = None
            
        except Exception as e:
            logger.error(f"Error initializing Python language: {str(e)}")
            raise Exception(f"Failed to initialize Python language for static analysis: {str(e)}")
    
    def _query_ast(self, ast_node: Node, query_string: str) -> List[Tuple[Node, Dict]]:
        """
        Execute a Tree-sitter query on an AST node and return captures.
        
        Args:
            ast_node (Node): Root AST node to query
            query_string (str): Tree-sitter query string
            
        Returns:
            List[Tuple[Node, Dict]]: List of (node, captures) tuples from query results
        """
        if self.languages.get('python') is None:
            logger.warning("Python language not available for queries")
            return []
        
        try:
            # Create query object
            query = self.languages['python'].query(query_string)
            
            # Execute query and return captures
            captures = query.captures(ast_node)
            return captures
            
        except Exception as e:
            logger.error(f"Error executing Tree-sitter query: {str(e)}")
            return []
    
    def _check_rule_pdb_set_trace(self, ast_node: Node) -> List[Dict]:
        """
        Check for pdb.set_trace() calls in the code.
        
        This rule identifies debugging statements that should not be in production code.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for pdb.set_trace() usage
        """
        findings = []
        
        # Query for pdb.set_trace() calls
        query_string = """
        (call
          function: (attribute
            object: (identifier) @obj
            attribute: (identifier) @attr)
          arguments: (argument_list)) @call
        (#eq? @obj "pdb")
        (#eq? @attr "set_trace")
        """
        
        try:
            captures = self._query_ast(ast_node, query_string)
            
            for node, capture_dict in captures:
                if capture_dict.get('call'):
                    call_node = capture_dict['call']
                    findings.append({
                        'rule_id': 'PDB_TRACE_FOUND',
                        'message': 'pdb.set_trace() found - debugging statement should be removed',
                        'line': call_node.start_point[0] + 1,
                        'column': call_node.start_point[1] + 1,
                        'severity': 'Warning',
                        'category': 'debugging',
                        'suggestion': 'Remove pdb.set_trace() before committing to production'
                    })
            
        except Exception as e:
            logger.error(f"Error in _check_rule_pdb_set_trace: {str(e)}")
        
        return findings
    
    def _check_rule_print_statements(self, ast_node: Node) -> List[Dict]:
        """
        Check for print() statements in the code.
        
        This rule identifies print statements that might be debugging leftovers
        or should use proper logging instead.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for print statement usage
        """
        findings = []
        
        # Query for print() function calls
        query_string = """
        (call
          function: (identifier) @func
          arguments: (argument_list)) @call
        (#eq? @func "print")
        """
        
        try:
            captures = self._query_ast(ast_node, query_string)
            
            for node, capture_dict in captures:
                if capture_dict.get('call'):
                    call_node = capture_dict['call']
                    findings.append({
                        'rule_id': 'PRINT_STATEMENT_FOUND',
                        'message': 'print() statement found - consider using logging instead',
                        'line': call_node.start_point[0] + 1,
                        'column': call_node.start_point[1] + 1,
                        'severity': 'Info',
                        'category': 'logging',
                        'suggestion': 'Replace print() with proper logging (logger.info, logger.debug, etc.)'
                    })
            
        except Exception as e:
            logger.error(f"Error in _check_rule_print_statements: {str(e)}")
        
        return findings
    
    def _check_rule_function_too_long(self, ast_node: Node) -> List[Dict]:
        """
        Check for functions that are too long (>50 lines).
        
        This rule identifies functions that might be too complex and should be refactored.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for overly long functions
        """
        findings = []
        
        # Query for function definitions
        query_string = """
        (function_definition
          name: (identifier) @func_name) @func_def
        """
        
        try:
            captures = self._query_ast(ast_node, query_string)
            
            for node, capture_dict in captures:
                if capture_dict.get('func_def'):
                    func_node = capture_dict['func_def']
                    func_name_node = capture_dict.get('func_name')
                    
                    # Calculate function length in lines
                    start_line = func_node.start_point[0]
                    end_line = func_node.end_point[0]
                    func_length = end_line - start_line + 1
                    
                    if func_length > 50:
                        func_name = func_name_node.text.decode('utf-8') if func_name_node else 'unknown'
                        findings.append({
                            'rule_id': 'FUNCTION_TOO_LONG',
                            'message': f'Function "{func_name}" is {func_length} lines long (>50 lines)',
                            'line': start_line + 1,
                            'column': func_node.start_point[1] + 1,
                            'severity': 'Warning',
                            'category': 'complexity',
                            'suggestion': f'Consider breaking down function "{func_name}" into smaller, more focused functions'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_rule_function_too_long: {str(e)}")
        
        return findings
    
    def _check_rule_class_too_long(self, ast_node: Node) -> List[Dict]:
        """
        Check for classes that are too long (>200 lines).
        
        This rule identifies classes that might have too many responsibilities
        and should be refactored.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for overly long classes
        """
        findings = []
        
        # Query for class definitions
        query_string = """
        (class_definition
          name: (identifier) @class_name) @class_def
        """
        
        try:
            captures = self._query_ast(ast_node, query_string)
            
            for node, capture_dict in captures:
                if capture_dict.get('class_def'):
                    class_node = capture_dict['class_def']
                    class_name_node = capture_dict.get('class_name')
                    
                    # Calculate class length in lines
                    start_line = class_node.start_point[0]
                    end_line = class_node.end_point[0]
                    class_length = end_line - start_line + 1
                    
                    if class_length > 200:
                        class_name = class_name_node.text.decode('utf-8') if class_name_node else 'unknown'
                        findings.append({
                            'rule_id': 'CLASS_TOO_LONG',
                            'message': f'Class "{class_name}" is {class_length} lines long (>200 lines)',
                            'line': start_line + 1,
                            'column': class_node.start_point[1] + 1,
                            'severity': 'Warning',
                            'category': 'complexity',
                            'suggestion': f'Consider breaking down class "{class_name}" into smaller classes with single responsibilities'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_rule_class_too_long: {str(e)}")
        
        return findings
    
    def _check_rule_simple_unused_imports(self, ast_node: Node) -> List[Dict]:
        """
        Check for potentially unused imports (simplified version).
        
        This is a simplified rule that identifies imports that are not obviously used
        in the same file. A more sophisticated version would require cross-file analysis.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for potentially unused imports
        """
        findings = []
        
        try:
            # First, collect all imports
            import_query = """
            (import_statement
              name: (dotted_name) @import_name) @import_stmt
            """
            
            import_from_query = """
            (import_from_statement
              name: (dotted_name (identifier) @imported_name)) @import_from_stmt
            """
            
            imports = set()
            import_locations = {}
            
            # Collect regular imports
            import_captures = self._query_ast(ast_node, import_query)
            for node, capture_dict in import_captures:
                if capture_dict.get('import_name'):
                    import_node = capture_dict['import_name']
                    import_stmt_node = capture_dict['import_stmt']
                    import_text = import_node.text.decode('utf-8')
                    # For dotted imports, use the first part
                    import_name = import_text.split('.')[0]
                    imports.add(import_name)
                    import_locations[import_name] = import_stmt_node
            
            # Collect from imports
            from_captures = self._query_ast(ast_node, import_from_query)
            for node, capture_dict in from_captures:
                if capture_dict.get('imported_name'):
                    imported_node = capture_dict['imported_name']
                    import_stmt_node = capture_dict['import_from_stmt']
                    import_name = imported_node.text.decode('utf-8')
                    imports.add(import_name)
                    import_locations[import_name] = import_stmt_node
            
            # Now check if imports are used (simple identifier matching)
            identifier_query = """
            (identifier) @identifier
            """
            
            used_identifiers = set()
            identifier_captures = self._query_ast(ast_node, identifier_query)
            for node, capture_dict in identifier_captures:
                if capture_dict.get('identifier'):
                    identifier_node = capture_dict['identifier']
                    identifier_name = identifier_node.text.decode('utf-8')
                    used_identifiers.add(identifier_name)
            
            # Find potentially unused imports
            for import_name in imports:
                if import_name not in used_identifiers:
                    import_node = import_locations.get(import_name)
                    if import_node:
                        findings.append({
                            'rule_id': 'POTENTIALLY_UNUSED_IMPORT',
                            'message': f'Import "{import_name}" appears to be unused',
                            'line': import_node.start_point[0] + 1,
                            'column': import_node.start_point[1] + 1,
                            'severity': 'Info',
                            'category': 'imports',
                            'suggestion': f'Consider removing unused import "{import_name}" if it\'s not needed'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_rule_simple_unused_imports: {str(e)}")
        
        return findings
    
    def analyze_python_ast(self, ast_node: Node) -> List[Dict]:
        """
        Perform comprehensive static analysis on a Python AST.
        
        Applies all implemented Python rules and aggregates their findings.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: Aggregated list of all static analysis findings
        """
        logger.info("Starting Python static analysis")
        
        all_findings = []
        
        try:
            # Apply all Python rules
            rules = [
                self._check_rule_pdb_set_trace,
                self._check_rule_print_statements,
                self._check_rule_function_too_long,
                self._check_rule_class_too_long,
                self._check_rule_simple_unused_imports
            ]
            
            for rule_func in rules:
                try:
                    rule_findings = rule_func(ast_node)
                    all_findings.extend(rule_findings)
                    logger.debug(f"Rule {rule_func.__name__} found {len(rule_findings)} issues")
                except Exception as e:
                    logger.error(f"Error in rule {rule_func.__name__}: {str(e)}")
            
            logger.info(f"Python static analysis completed. Found {len(all_findings)} total issues")
            
        except Exception as e:
            logger.error(f"Error in analyze_python_ast: {str(e)}")
        
        return all_findings
    
    def analyze_file_ast(self, ast_node: Node, file_path: str, language: str = 'python') -> List[Dict]:
        """
        Analyze a single file's AST and return findings.
        
        Args:
            ast_node (Node): Root AST node of the file
            file_path (str): Path to the file being analyzed
            language (str): Programming language (default: 'python')
            
        Returns:
            List[Dict]: List of static analysis findings for the file
        """
        if language != 'python':
            logger.warning(f"Language '{language}' not supported yet. Only Python is currently supported.")
            return []
        
        if ast_node is None:
            logger.warning(f"No AST available for file: {file_path}")
            return []
        
        try:
            findings = self.analyze_python_ast(ast_node)
            
            # Add file path to all findings
            for finding in findings:
                finding['file'] = file_path
            
            logger.info(f"Analyzed {file_path}: found {len(findings)} issues")
            return findings
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return []
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported programming languages.
        
        Returns:
            List[str]: List of supported language names
        """
        return self.supported_languages.copy()
    
    def is_language_supported(self, language: str) -> bool:
        """
        Check if a programming language is supported.
        
        Args:
            language (str): Language name to check
            
        Returns:
            bool: True if language is supported, False otherwise
        """
        return language in self.supported_languages 