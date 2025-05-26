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
    
    def _query_ast(self, ast_node: Node, query_string: str) -> List[Tuple[Node, Dict[str, Node]]]:
        """
        Execute a Tree-sitter query on an AST node and return captures.
        
        Args:
            ast_node (Node): Root AST node to query
            query_string (str): Tree-sitter query string
            
        Returns:
            List[Tuple[Node, Dict[str, Node]]]: List of (match, captures) tuples
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
            
            for _, capture_dict in captures:
                if 'call' in capture_dict:
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
            
            for _, capture_dict in captures:
                if 'call' in capture_dict:
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
            
            for _, capture_dict in captures:
                if 'func_def' in capture_dict and 'func_name' in capture_dict:
                    func_node = capture_dict['func_def']
                    func_name_node = capture_dict['func_name']
                    
                    # Calculate function length in lines
                    start_line = func_node.start_point[0]
                    end_line = func_node.end_point[0]
                    func_length = end_line - start_line + 1
                    
                    if func_length > 50:
                        func_name = func_name_node.text.decode('utf-8')
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
        
        This rule identifies classes that might be too complex and should be refactored.
        
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
            
            for _, capture_dict in captures:
                if 'class_def' in capture_dict and 'class_name' in capture_dict:
                    class_node = capture_dict['class_def']
                    class_name_node = capture_dict['class_name']
                    
                    # Calculate class length in lines
                    start_line = class_node.start_point[0]
                    end_line = class_node.end_point[0]
                    class_length = end_line - start_line + 1
                    
                    if class_length > 200:
                        class_name = class_name_node.text.decode('utf-8')
                        findings.append({
                            'rule_id': 'CLASS_TOO_LONG',
                            'message': f'Class "{class_name}" is {class_length} lines long (>200 lines)',
                            'line': start_line + 1,
                            'column': class_node.start_point[1] + 1,
                            'severity': 'Warning',
                            'category': 'complexity',
                            'suggestion': f'Consider breaking down class "{class_name}" into smaller, more focused classes'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_rule_class_too_long: {str(e)}")
        
        return findings
    
    def _check_rule_simple_unused_imports(self, ast_node: Node) -> List[Dict]:
        """
        Check for potentially unused imports.
        
        This is a simple implementation that looks for imported names that don't
        appear as identifiers in the code. This may have false positives.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for potentially unused imports
        """
        findings = []
        imported_names = set()
        used_names = set()
        
        try:
            # Get all import statements
            import_query = """
            (import_statement
              name: (dotted_name (identifier) @import_name)) @import_stmt
            """
            import_captures = self._query_ast(ast_node, import_query)
            
            for _, capture_dict in import_captures:
                if 'import_name' in capture_dict:
                    import_node = capture_dict['import_name']
                    imported_names.add(import_node.text.decode('utf-8'))
            
            # Get all from-import statements
            from_import_query = """
            (import_from_statement
              name: (dotted_name (identifier) @from_name)
              names: (import_names (identifier) @import_name)) @from_stmt
            """
            from_import_captures = self._query_ast(ast_node, from_import_query)
            
            for _, capture_dict in from_import_captures:
                if 'import_name' in capture_dict:
                    import_node = capture_dict['import_name']
                    imported_names.add(import_node.text.decode('utf-8'))
            
            # Get all identifiers
            identifier_query = """
            (identifier) @identifier
            """
            identifier_captures = self._query_ast(ast_node, identifier_query)
            
            for _, capture_dict in identifier_captures:
                if 'identifier' in capture_dict:
                    identifier_node = capture_dict['identifier']
                    used_names.add(identifier_node.text.decode('utf-8'))
            
            # Find unused imports
            for imported_name in imported_names:
                if imported_name not in used_names:
                    findings.append({
                        'rule_id': 'POTENTIALLY_UNUSED_IMPORT',
                        'message': f'Import "{imported_name}" appears to be unused',
                        'line': 1,  # We don't have the exact line number in this simple implementation
                        'column': 1,
                        'severity': 'Info',
                        'category': 'imports',
                        'suggestion': f'Consider removing unused import "{imported_name}" if it is not needed'
                    })
            
        except Exception as e:
            logger.error(f"Error in _check_rule_simple_unused_imports: {str(e)}")
        
        return findings
    
    def _check_empty_except_block(self, ast_node: Node) -> List[Dict]:
        """
        Check for empty except blocks in try-except statements.
        
        This rule identifies except blocks that don't contain any code, which is a bad practice
        as it silently swallows exceptions.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for empty except blocks
        """
        findings = []
        
        # Query for empty except blocks
        query_string = """
        (try_statement
          (except_clause
            body: (block . ":" @except_colon
                        . (pass_statement) @pass))) @except
        """
        
        try:
            captures = self._query_ast(ast_node, query_string)
            
            for _, capture_dict in captures:
                if 'except' in capture_dict:
                    except_node = capture_dict['except']
                    findings.append({
                        'rule_id': 'EMPTY_EXCEPT_BLOCK',
                        'message': 'Empty except block found - should handle exceptions explicitly',
                        'line': except_node.start_point[0] + 1,
                        'column': except_node.start_point[1] + 1,
                        'severity': 'Error',
                        'category': 'error_handling',
                        'suggestion': 'Add explicit exception handling or logging in the except block'
                    })
            
        except Exception as e:
            logger.error(f"Error in _check_empty_except_block: {str(e)}")
        
        return findings

    def _check_hardcoded_passwords(self, ast_node: Node) -> List[Dict]:
        """
        Check for potential hardcoded passwords in string assignments.
        
        This rule identifies assignments where the variable name contains 'password'
        and is assigned a string literal.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for hardcoded passwords
        """
        findings = []
        
        # Query for string assignments to password-like variables
        query_string = """
        (assignment
          left: (identifier) @var_name
          right: (string) @string_value)
        """
        
        try:
            captures = self._query_ast(ast_node, query_string)
            
            for _, capture_dict in captures:
                if 'var_name' in capture_dict and 'string_value' in capture_dict:
                    var_name = capture_dict['var_name'].text.decode('utf-8').lower()
                    if 'password' in var_name or 'passwd' in var_name:
                        findings.append({
                            'rule_id': 'HARDCODED_PASSWORD',
                            'message': f'Potential hardcoded password in variable "{var_name}"',
                            'line': capture_dict['var_name'].start_point[0] + 1,
                            'column': capture_dict['var_name'].start_point[1] + 1,
                            'severity': 'Error',
                            'category': 'security',
                            'suggestion': 'Use environment variables or secure configuration management for passwords'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_hardcoded_passwords: {str(e)}")
        
        return findings

    def _check_excessive_boolean_complexity(self, ast_node: Node) -> List[Dict]:
        """
        Check for boolean expressions with excessive complexity.
        
        This rule identifies expressions with more than 3 AND/OR operators.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for complex boolean expressions
        """
        findings = []
        
        # Query for boolean operators
        query_string = """
        (boolean_operator) @bool_op
        """
        
        try:
            captures = self._query_ast(ast_node, query_string)
            
            for _, capture_dict in captures:
                if 'bool_op' in capture_dict:
                    bool_op_node = capture_dict['bool_op']
                    # Count parent boolean operators to determine complexity
                    operator_count = 1
                    current_node = bool_op_node
                    while current_node.parent and current_node.parent.type == 'boolean_operator':
                        operator_count += 1
                        current_node = current_node.parent
                    
                    if operator_count > 3:
                        findings.append({
                            'rule_id': 'EXCESSIVE_BOOLEAN_COMPLEXITY',
                            'message': f'Boolean expression with {operator_count} operators is too complex',
                            'line': bool_op_node.start_point[0] + 1,
                            'column': bool_op_node.start_point[1] + 1,
                            'severity': 'Warning',
                            'category': 'complexity',
                            'suggestion': 'Break down complex boolean expressions into smaller, more readable conditions'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_excessive_boolean_complexity: {str(e)}")
        
        return findings

    def _check_magic_numbers(self, ast_node: Node) -> List[Dict]:
        """
        Check for magic numbers in code.
        
        This rule identifies numeric literals used outside of variable assignments
        or default parameters.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for magic numbers
        """
        findings = []
        
        # Query for numeric literals
        query_string = """
        (integer) @number
        (float) @number
        """
        
        try:
            captures = self._query_ast(ast_node, query_string)
            
            for _, capture_dict in captures:
                if 'number' in capture_dict:
                    number_node = capture_dict['number']
                    # Skip common acceptable numbers like 0, 1, -1
                    number_text = number_node.text.decode('utf-8')
                    if number_text in ['0', '1', '-1']:
                        continue
                    
                    # Skip if parent is assignment or parameters
                    parent = number_node.parent
                    if parent and parent.type in ['assignment', 'parameters']:
                        continue
                    
                    findings.append({
                        'rule_id': 'MAGIC_NUMBER',
                        'message': f'Magic number {number_text} found',
                        'line': number_node.start_point[0] + 1,
                        'column': number_node.start_point[1] + 1,
                        'severity': 'Info',
                        'category': 'maintainability',
                        'suggestion': f'Consider defining constant for the value {number_text}'
                    })
            
        except Exception as e:
            logger.error(f"Error in _check_magic_numbers: {str(e)}")
        
        return findings

    def _check_todo_comments(self, ast_node: Node) -> List[Dict]:
        """
        Check for TODO/FIXME comments in code.
        
        This rule identifies comments containing TODO or FIXME markers.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for TODO/FIXME comments
        """
        findings = []
        
        # Query for comments
        query_string = """
        (comment) @comment
        """
        
        try:
            captures = self._query_ast(ast_node, query_string)
            
            for _, capture_dict in captures:
                if 'comment' in capture_dict:
                    comment_node = capture_dict['comment']
                    comment_text = comment_node.text.decode('utf-8').upper()
                    if 'TODO' in comment_text or 'FIXME' in comment_text:
                        findings.append({
                            'rule_id': 'TODO_COMMENT_FOUND',
                            'message': 'TODO comment found',
                            'line': comment_node.start_point[0] + 1,
                            'column': comment_node.start_point[1] + 1,
                            'severity': 'Info',
                            'category': 'documentation',
                            'suggestion': 'Consider creating a ticket/issue for tracking this TODO item'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_todo_comments: {str(e)}")
        
        return findings

    def analyze_python_ast(self, ast_node: Node) -> List[Dict]:
        """
        Analyze a Python AST and return all findings from static analysis rules.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: Combined list of findings from all rules
        """
        findings = []
        
        # Execute all Python static analysis rules
        rule_methods = [
            self._check_rule_pdb_set_trace,
            self._check_rule_print_statements,
            self._check_rule_function_too_long,
            self._check_rule_class_too_long,
            self._check_rule_simple_unused_imports,
            self._check_empty_except_block,
            self._check_hardcoded_passwords,
            self._check_excessive_boolean_complexity,
            self._check_magic_numbers,
            self._check_todo_comments
        ]
        
        for rule_method in rule_methods:
            try:
                rule_findings = rule_method(ast_node)
                findings.extend(rule_findings)
            except Exception as e:
                # Log error without accessing __name__
                logger.error(f"Error executing rule: {str(e)}")
        
        return findings
    
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