"""
StaticAnalysisAgent for AI Code Review System.

This module implements the StaticAnalysisAgent responsible for performing
rule-based static analysis on Abstract Syntax Trees (ASTs) using Tree-sitter
queries to identify potential code quality issues.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import os

try:
    import tree_sitter
    from tree_sitter import Language, Parser, Node
except ImportError:
    tree_sitter = None
    Language = None
    Parser = None
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
        
        Sets up Tree-sitter language support and loads Python and Java grammars
        for executing static analysis queries.
        
        Raises:
            ImportError: If tree-sitter is not installed
            Exception: If language grammars cannot be loaded
        """
        if tree_sitter is None:
            raise ImportError(
                "tree-sitter is not installed. Please install it with: pip install tree-sitter"
            )
        
        self.languages = {}
        self.supported_languages = ['python']  # Start with only Python support
        
        # Initialize languages for queries
        self._initialize_languages()
        
        logger.info(f"StaticAnalysisAgent initialized with languages: {self.supported_languages}")
    
    def _initialize_languages(self) -> None:
        """
        Initialize language grammars for Tree-sitter queries.
        
        Attempts to load Python and Java grammars using multiple methods.
        
        Raises:
            Exception: If no language grammars can be loaded
        """
        try:
            # Load Python language first
            python_lang = self._initialize_python_language()
            if python_lang:
                self.languages['python'] = python_lang
            else:
                logger.warning("Could not load Python language grammar. Static analysis will be limited.")
                self.languages['python'] = None  # Set to None to indicate failed initialization
            
            # Try to load Java language if available
            java_lang = self._initialize_java_language()
            if java_lang:
                self.languages['java'] = java_lang
                if 'java' not in self.supported_languages:
                    self.supported_languages.append('java')
            
            # Try to load Kotlin language if available
            kotlin_lang = self._initialize_kotlin_language()
            if kotlin_lang:
                self.languages['kotlin'] = kotlin_lang
                if 'kotlin' not in self.supported_languages:
                    self.supported_languages.append('kotlin')
            
            # Try to load XML language if available
            xml_lang = self._initialize_xml_language()
            if xml_lang:
                self.languages['xml'] = xml_lang
                if 'xml' not in self.supported_languages:
                    self.supported_languages.append('xml')
            
            # Try to load JavaScript language if available
            javascript_lang = self._initialize_javascript_language()
            if javascript_lang:
                self.languages['javascript'] = javascript_lang
                if 'javascript' not in self.supported_languages:
                    self.supported_languages.append('javascript')
            
            # Try to load Dart language if available
            dart_lang = self._initialize_dart_language()
            if dart_lang:
                self.languages['dart'] = dart_lang
                if 'dart' not in self.supported_languages:
                    self.supported_languages.append('dart')
            
            if not any(lang is not None for lang in self.languages.values()):
                raise Exception("No language grammars could be loaded")
            
        except Exception as e:
            logger.error(f"Error initializing languages: {str(e)}")
            raise
    
    def _initialize_python_language(self) -> Optional[Language]:
        """
        Initialize Python language grammar for Tree-sitter queries.
        
        Attempts to load Python grammar using multiple methods.
        
        Returns:
            Optional[Language]: Python language object if successful, None if failed
        """
        try:
            # Try to load from package first
            from tree_sitter_python import language
            lang_capsule = language()
            # Wrap PyCapsule with Language object for newer tree-sitter versions
            python_lang = Language(lang_capsule)
            logger.info("Successfully loaded Python language grammar for static analysis")
            return python_lang
        except ImportError:
            logger.debug("tree-sitter-python package not found")
            
            # If we can't load the language, we'll still continue but with limited functionality
            logger.warning("Could not load Python language grammar. Static analysis will be limited.")
            return None
            
        except Exception as e:
            logger.error(f"Error initializing Python language: {str(e)}")
            raise Exception(f"Failed to initialize Python language for static analysis: {str(e)}")
    
    def _initialize_java_language(self) -> Optional[Language]:
        """
        Initialize Java language support.
        
        Attempts to load Java grammar from tree-sitter-java package.
        Falls back to loading from local build if package is not found.
        
        Returns:
            Optional[Language]: Java language object if successful, None if failed
        """
        try:
            # Try to load from package first
            from tree_sitter_java import language as java_language
            lang_capsule = java_language()
            # Wrap PyCapsule with Language object for newer tree-sitter versions
            java_lang = Language(lang_capsule)
            logger.info("Successfully loaded Java language grammar for static analysis")
            return java_lang
        except ImportError:
            logger.warning("tree-sitter-java package not found, falling back to local build")
            try:
                # Try to load from local build
                java_lib_path = os.path.join(os.path.dirname(__file__), "build/java.so")
                if os.path.exists(java_lib_path):
                    return Language(java_lib_path, 'java')
                else:
                    logger.error("Java grammar not found in local build")
                    return None
            except Exception as e:
                logger.error(f"Failed to load Java grammar: {str(e)}")
                return None
    
    def _initialize_kotlin_language(self) -> Optional[Language]:
        """
        Initialize Kotlin language support.
        
        Attempts to load Kotlin grammar from tree-sitter-kotlin package.
        Falls back to loading from local build if package is not found.
        
        Returns:
            Optional[Language]: Kotlin language object if successful, None if failed
        """
        try:
            # Try to load from package first
            from tree_sitter_kotlin import language as kotlin_language
            lang_capsule = kotlin_language()
            # Wrap PyCapsule with Language object for newer tree-sitter versions
            kotlin_lang = Language(lang_capsule)
            logger.info("Successfully loaded Kotlin language grammar for static analysis")
            return kotlin_lang
        except ImportError:
            logger.warning("tree-sitter-kotlin package not found, falling back to local build")
            try:
                # Try to load from local build
                kotlin_lib_path = os.path.join(os.path.dirname(__file__), "build/kotlin.so")
                if os.path.exists(kotlin_lib_path):
                    return Language(kotlin_lib_path, 'kotlin')
                else:
                    logger.error("Kotlin grammar not found in local build")
                    return None
            except Exception as e:
                logger.error(f"Failed to load Kotlin grammar: {str(e)}")
                return None
    
    def _initialize_xml_language(self) -> Optional[Language]:
        """
        Initialize XML language support.
        
        Attempts to load XML grammar from tree-sitter-xml package.
        Falls back to loading from local build if package is not found.
        
        Returns:
            Optional[Language]: XML language object if successful, None if failed
        """
        try:
            # Try to load from package first
            from tree_sitter_xml import language as xml_language
            lang_capsule = xml_language()
            # Wrap PyCapsule with Language object for newer tree-sitter versions
            xml_lang = Language(lang_capsule)
            logger.info("Successfully loaded XML language grammar for static analysis")
            return xml_lang
        except ImportError:
            logger.warning("tree-sitter-xml package not found, falling back to local build")
            try:
                # Try to load from local build
                xml_lib_path = os.path.join(os.path.dirname(__file__), "build/xml.so")
                if os.path.exists(xml_lib_path):
                    return Language(xml_lib_path, 'xml')
                else:
                    logger.error("XML grammar not found in local build")
                    return None
            except Exception as e:
                logger.error(f"Failed to load XML grammar: {str(e)}")
                return None
    
    def _initialize_javascript_language(self) -> Optional[Language]:
        """
        Initialize JavaScript language support.
        
        Attempts to load JavaScript grammar from tree-sitter-javascript package.
        Falls back to loading from local build if package is not found.
        
        Returns:
            Optional[Language]: JavaScript language object if successful, None if failed
        """
        try:
            # Try to load from package first
            from tree_sitter_javascript import language as javascript_language
            lang_capsule = javascript_language()
            # Wrap PyCapsule with Language object for newer tree-sitter versions
            javascript_lang = Language(lang_capsule)
            logger.info("Successfully loaded JavaScript language grammar for static analysis")
            return javascript_lang
        except ImportError:
            logger.warning("tree-sitter-javascript package not found, falling back to local build")
            try:
                # Try to load from local build
                javascript_lib_path = os.path.join(os.path.dirname(__file__), "build/javascript.so")
                if os.path.exists(javascript_lib_path):
                    return Language(javascript_lib_path, 'javascript')
                else:
                    logger.error("JavaScript grammar not found in local build")
                    return None
            except Exception as e:
                logger.error(f"Failed to load JavaScript grammar: {str(e)}")
                return None
    
    def _initialize_dart_language(self) -> Optional[Language]:
        """
        Initialize Dart language support.
        
        Attempts to load Dart grammar from tree-sitter-dart package.
        Falls back to loading from local build if package is not found.
        
        Returns:
            Optional[Language]: Dart language object if successful, None if failed
        """
        try:
            # Method 1: Try to load from tree-sitter-language-pack (preferred)
            try:
                from tree_sitter_language_pack import get_language
                dart_lang = get_language("dart")
                logger.info("Successfully loaded Dart language grammar from language pack for static analysis")
                return dart_lang
            except ImportError:
                logger.debug("tree_sitter_language_pack not found, trying alternative methods")
            except Exception as e:
                logger.debug(f"Failed to get Dart from language pack: {str(e)}")
            
            # Method 2: Try to load from tree-sitter-dart package
            try:
                from tree_sitter_dart import language as dart_language
                lang_capsule = dart_language()
                # Wrap PyCapsule with Language object for newer tree-sitter versions
                dart_lang = Language(lang_capsule)
                logger.info("Successfully loaded Dart language grammar for static analysis")
                return dart_lang
            except ImportError:
                logger.warning("tree-sitter-dart package not found, falling back to local build")
                try:
                    # Try to load from local build
                    dart_lib_path = os.path.join(os.path.dirname(__file__), "build/dart.so")
                    if os.path.exists(dart_lib_path):
                        return Language(dart_lib_path, 'dart')
                    else:
                        logger.error("Dart grammar not found in local build")
                        return None
                except Exception as e:
                    logger.error(f"Failed to load Dart grammar: {str(e)}")
                    return None
        except Exception as e:
            logger.error(f"Failed to load Dart grammar: {str(e)}")
            return None
    
    def _query_ast(self, ast_node: Node, query_string: str, language: str = 'python') -> List[Tuple[Node, Dict[str, Node]]]:
        """
        Execute a Tree-sitter query on an AST node and return captures.
        
        Args:
            ast_node (Node): Root AST node to query
            query_string (str): Tree-sitter query string
            language (str): Language to use for the query (default: 'python')
            
        Returns:
            List[Tuple[Node, Dict[str, Node]]]: List of (match, captures) tuples
        """
        if self.languages.get(language) is None:
            logger.warning(f"{language} language not available for queries")
            return []
        
        try:
            # Create query object
            query = self.languages[language].query(query_string)
            
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

    def _check_java_system_out_println(self, ast_node: Node) -> List[Dict]:
        """
        Check for System.out.println() calls in Java code.
        
        This rule identifies print statements that should use proper logging instead.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for System.out.println usage
        """
        findings = []
        
        # Query for System.out.println() calls
        query_string = """
        (method_invocation
          object: (field_access
            object: (field_access
              object: (identifier) @sys
              field: (identifier) @out)
            field: (identifier) @println)
          arguments: (argument_list)) @call
        (#eq? @sys "System")
        (#eq? @out "out")
        (#eq? @println "println")
        """
        
        try:
            captures = self._query_ast(ast_node, query_string)
            
            for _, capture_dict in captures:
                if 'call' in capture_dict:
                    call_node = capture_dict['call']
                    findings.append({
                        'rule_id': 'SYSTEM_OUT_PRINTLN_FOUND',
                        'message': 'System.out.println() found - consider using proper logging',
                        'line': call_node.start_point[0] + 1,
                        'column': call_node.start_point[1] + 1,
                        'severity': 'Info',
                        'category': 'logging',
                        'suggestion': 'Replace System.out.println() with a proper logging framework (e.g., SLF4J, Log4j)'
                    })
            
        except Exception as e:
            logger.error(f"Error in _check_java_system_out_println: {str(e)}")
        
        return findings

    def _check_java_empty_catch_block(self, ast_node: Node) -> List[Dict]:
        """
        Check for empty catch blocks in Java code.
        
        This rule identifies catch blocks that silently swallow exceptions.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for empty catch blocks
        """
        findings = []
        
        # Query for catch clauses
        query_string = """
        (catch_clause
          body: (block) @catch_body) @catch
        """
        
        try:
            captures = self._query_ast(ast_node, query_string)
            
            for _, capture_dict in captures:
                if 'catch_body' in capture_dict:
                    body_node = capture_dict['catch_body']
                    # Check if block is empty (only contains whitespace/comments)
                    if len(body_node.children) <= 2:  # Account for braces
                        findings.append({
                            'rule_id': 'EMPTY_CATCH_BLOCK',
                            'message': 'Empty catch block found - exceptions should be handled or logged',
                            'line': body_node.start_point[0] + 1,
                            'column': body_node.start_point[1] + 1,
                            'severity': 'Warning',
                            'category': 'error_handling',
                            'suggestion': 'Either handle the exception appropriately or log it. Never silently swallow exceptions.'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_java_empty_catch_block: {str(e)}")
        
        return findings

    def _check_java_public_fields(self, ast_node: Node) -> List[Dict]:
        """
        Check for public fields in Java classes.
        
        This rule identifies public fields that might violate encapsulation.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for public fields
        """
        findings = []
        
        # Query for public field declarations
        query_string = """
        (field_declaration
          modifiers: (modifiers
            (modifier) @mod)
          declarator: (variable_declarator
            name: (identifier) @field_name)) @field
        (#eq? @mod "public")
        """
        
        try:
            captures = self._query_ast(ast_node, query_string)
            
            for _, capture_dict in captures:
                if 'field_name' in capture_dict and 'field' in capture_dict:
                    field_node = capture_dict['field']
                    field_name = capture_dict['field_name'].text.decode('utf-8')
                    findings.append({
                        'rule_id': 'PUBLIC_FIELD',
                        'message': f'Public field "{field_name}" found - consider using accessors',
                        'line': field_node.start_point[0] + 1,
                        'column': field_node.start_point[1] + 1,
                        'severity': 'Warning',
                        'category': 'encapsulation',
                        'suggestion': f'Make field "{field_name}" private and provide getter/setter methods if needed'
                    })
            
        except Exception as e:
            logger.error(f"Error in _check_java_public_fields: {str(e)}")
        
        return findings

    def analyze_java_ast(self, ast_node: Node) -> List[Dict]:
        """
        Analyze a Java AST and return all findings from static analysis rules.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: Combined list of findings from all Java rules
        """
        findings = []
        
        # Execute all Java static analysis rules
        rule_methods = [
            self._check_java_system_out_println,
            self._check_java_empty_catch_block,
            self._check_java_public_fields
        ]
        
        for rule_method in rule_methods:
            try:
                rule_findings = rule_method(ast_node)
                findings.extend(rule_findings)
            except Exception as e:
                logger.error(f"Error executing Java rule: {str(e)}")
        
        return findings

    def analyze_ast(self, ast_node: Node, file_path: str, language: str = 'python') -> List[Dict]:
        """
        Analyze an AST and return findings based on the language.
        
        Args:
            ast_node (Node): Root AST node to analyze
            file_path (str): Path to the file being analyzed
            language (str): Programming language (default: 'python')
            
        Returns:
            List[Dict]: List of static analysis findings
        """
        if language not in self.supported_languages:
            logger.warning(f"Language '{language}' not supported yet")
            return []
        
        if ast_node is None:
            logger.warning(f"No AST available for file: {file_path}")
            return []
        
        try:
            if language == 'python':
                findings = self.analyze_python_ast(ast_node)
            elif language == 'java':
                findings = self.analyze_java_ast(ast_node)
            elif language == 'kotlin':
                findings = self.analyze_kotlin_ast(ast_node)
            elif language == 'xml':
                findings = self.analyze_xml_ast(ast_node)
            elif language == 'javascript':
                findings = self.analyze_javascript_ast(ast_node)
            elif language == 'dart':
                findings = self.analyze_dart_ast(ast_node)
            else:
                findings = []
            
            # Add file path to all findings
            for finding in findings:
                finding['file'] = file_path
            
            logger.info(f"Analyzed {file_path}: found {len(findings)} issues")
            return findings
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return []

    def _check_kotlin_hardcoded_strings(self, ast_node: Node) -> List[Dict]:
        """
        Check for hardcoded string literals in Kotlin code.
        
        This rule identifies string literals that should be moved to string resources.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for hardcoded strings
        """
        findings = []
        
        # Query for string literals but exclude very short ones or common patterns
        query_string = """
        (string_literal) @string
        """
        
        try:
            captures = self._query_ast(ast_node, query_string, 'kotlin')
            
            for _, capture_dict in captures:
                if 'string' in capture_dict:
                    string_node = capture_dict['string']
                    string_text = string_node.text.decode('utf-8', errors='ignore')
                    
                    # Only flag longer strings that look like UI text
                    if (len(string_text) > 10 and 
                        not string_text.startswith('""') and
                        not any(pattern in string_text.lower() for pattern in ['test', 'debug', 'log', 'tag'])):
                        findings.append({
                            'rule_id': 'KOTLIN_HARDCODED_STRINGS',
                            'message': f'Hardcoded string found: {string_text[:30]}...',
                            'line': string_node.start_point[0] + 1,
                            'column': string_node.start_point[1] + 1,
                            'severity': 'Warning',
                            'category': 'android_best_practices',
                            'suggestion': 'Move string literals to strings.xml resource file for internationalization'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_kotlin_hardcoded_strings: {str(e)}")
        
        return findings
    
    def _check_kotlin_null_safety_violations(self, ast_node: Node) -> List[Dict]:
        """
        Check for potential null safety violations in Kotlin code.
        
        This rule identifies usage of !! operator which can cause KotlinNullPointerException.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for null safety violations
        """
        findings = []
        
        # Query for not-null assertion operator (!!)
        query_string = """
        (not_null_assertion) @not_null
        """
        
        try:
            captures = self._query_ast(ast_node, query_string, 'kotlin')
            
            for _, capture_dict in captures:
                if 'not_null' in capture_dict:
                    not_null_node = capture_dict['not_null']
                    findings.append({
                        'rule_id': 'KOTLIN_NULL_SAFETY_VIOLATION',
                        'message': 'Not-null assertion operator (!!) found - potential crash risk',
                        'line': not_null_node.start_point[0] + 1,
                        'column': not_null_node.start_point[1] + 1,
                        'severity': 'Error',
                        'category': 'null_safety',
                        'suggestion': 'Consider using safe call operator (?.) or proper null checking instead of !!'
                    })
            
        except Exception as e:
            logger.error(f"Error in _check_kotlin_null_safety_violations: {str(e)}")
        
        return findings
    
    def _check_kotlin_companion_object_constants(self, ast_node: Node) -> List[Dict]:
        """
        Check for constants that should be in companion objects in Kotlin.
        
        This rule identifies top-level constants that might be better organized.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for constant organization
        """
        findings = []
        
        # Query for top-level val declarations with constant-like names
        query_string = """
        (property_declaration
          modifiers: (modifiers) @mods
          (variable_declaration
            (simple_identifier) @name)) @prop
        """
        
        try:
            captures = self._query_ast(ast_node, query_string, 'kotlin')
            
            for _, capture_dict in captures:
                if 'name' in capture_dict and 'prop' in capture_dict:
                    name_node = capture_dict['name']
                    prop_node = capture_dict['prop']
                    name_text = name_node.text.decode('utf-8', errors='ignore')
                    
                    # Check if it looks like a constant (all uppercase or starts with uppercase)
                    if name_text.isupper() or (name_text and name_text[0].isupper()):
                        findings.append({
                            'rule_id': 'KOTLIN_COMPANION_OBJECT_CONSTANTS',
                            'message': f'Constant "{name_text}" could be organized in a companion object',
                            'line': prop_node.start_point[0] + 1,
                            'column': prop_node.start_point[1] + 1,
                            'severity': 'Info',
                            'category': 'code_organization',
                            'suggestion': f'Consider moving constant "{name_text}" to a companion object for better organization'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_kotlin_companion_object_constants: {str(e)}")
        
        return findings
    
    def _check_kotlin_android_logging(self, ast_node: Node) -> List[Dict]:
        """
        Check for Android logging best practices in Kotlin.
        
        This rule identifies Log.d/v calls that might be left in production code.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for logging issues
        """
        findings = []
        
        # Query for Log.d or Log.v calls
        query_string = """
        (call_expression
          (navigation_expression
            (simple_identifier) @log_class
            (simple_identifier) @log_method)) @call
        (#eq? @log_class "Log")
        """
        
        try:
            captures = self._query_ast(ast_node, query_string, 'kotlin')
            
            for _, capture_dict in captures:
                if 'log_method' in capture_dict and 'call' in capture_dict:
                    method_node = capture_dict['log_method']
                    call_node = capture_dict['call']
                    method_name = method_node.text.decode('utf-8', errors='ignore')
                    
                    if method_name in ['d', 'v']:  # Debug and Verbose logs
                        findings.append({
                            'rule_id': 'KOTLIN_ANDROID_LOGGING',
                            'message': f'Log.{method_name}() found - ensure debug logs are stripped in release builds',
                            'line': call_node.start_point[0] + 1,
                            'column': call_node.start_point[1] + 1,
                            'severity': 'Warning',
                            'category': 'android_logging',
                            'suggestion': f'Ensure Log.{method_name}() calls are removed or disabled in production builds'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_kotlin_android_logging: {str(e)}")
        
        return findings
    
    def analyze_kotlin_ast(self, ast_node: Node) -> List[Dict]:
        """
        Analyze a Kotlin AST and return all findings from static analysis rules.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: Combined list of findings from all Kotlin rules
        """
        findings = []
        
        # Execute all Kotlin static analysis rules
        rule_methods = [
            self._check_kotlin_hardcoded_strings,
            self._check_kotlin_null_safety_violations,
            self._check_kotlin_companion_object_constants,
            self._check_kotlin_android_logging
        ]
        
        for rule_method in rule_methods:
            try:
                rule_findings = rule_method(ast_node)
                findings.extend(rule_findings)
            except Exception as e:
                logger.error(f"Error executing Kotlin rule: {str(e)}")
        
        return findings
    
    def _check_android_manifest_permissions(self, ast_node: Node) -> List[Dict]:
        """
        Check for potentially dangerous permissions in Android manifest.
        
        This rule identifies high-risk permissions that need careful consideration.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for dangerous permissions
        """
        findings = []
        
        # Query for uses-permission elements
        query_string = """
        (element
          (start_tag
            (name) @tag_name
            (attribute
              (attribute_name) @attr_name
              (quoted_attribute_value) @attr_value))) @element
        (#eq? @tag_name "uses-permission")
        (#eq? @attr_name "android:name")
        """
        
        # List of potentially dangerous permissions
        dangerous_permissions = [
            'android.permission.CAMERA',
            'android.permission.READ_CONTACTS',
            'android.permission.WRITE_CONTACTS',
            'android.permission.ACCESS_FINE_LOCATION',
            'android.permission.ACCESS_COARSE_LOCATION',
            'android.permission.RECORD_AUDIO',
            'android.permission.READ_PHONE_STATE',
            'android.permission.READ_SMS',
            'android.permission.WRITE_EXTERNAL_STORAGE'
        ]
        
        try:
            captures = self._query_ast(ast_node, query_string, 'xml')
            
            for _, capture_dict in captures:
                if 'attr_value' in capture_dict and 'element' in capture_dict:
                    value_node = capture_dict['attr_value']
                    element_node = capture_dict['element']
                    permission_name = value_node.text.decode('utf-8', errors='ignore').strip('"\'')
                    
                    if permission_name in dangerous_permissions:
                        findings.append({
                            'rule_id': 'ANDROID_DANGEROUS_PERMISSION',
                            'message': f'Dangerous permission declared: {permission_name}',
                            'line': element_node.start_point[0] + 1,
                            'column': element_node.start_point[1] + 1,
                            'severity': 'Warning',
                            'category': 'android_security',
                            'suggestion': f'Ensure {permission_name} is necessary and handle runtime permission requests properly'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_android_manifest_permissions: {str(e)}")
        
        return findings
    
    def _check_android_layout_performance(self, ast_node: Node) -> List[Dict]:
        """
        Check for potential performance issues in Android layouts.
        
        This rule identifies layout patterns that might impact performance.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for layout performance issues
        """
        findings = []
        
        # Query for nested LinearLayouts
        query_string = """
        (element
          (start_tag
            (name) @outer_tag)
          (element
            (start_tag
              (name) @inner_tag))) @outer_element
        (#eq? @outer_tag "LinearLayout")
        (#eq? @inner_tag "LinearLayout")
        """
        
        try:
            captures = self._query_ast(ast_node, query_string, 'xml')
            
            for _, capture_dict in captures:
                if 'outer_element' in capture_dict:
                    element_node = capture_dict['outer_element']
                    findings.append({
                        'rule_id': 'ANDROID_NESTED_LINEARLAYOUT',
                        'message': 'Nested LinearLayouts found - consider using ConstraintLayout for better performance',
                        'line': element_node.start_point[0] + 1,
                        'column': element_node.start_point[1] + 1,
                        'severity': 'Warning',
                        'category': 'android_performance',
                        'suggestion': 'Replace nested LinearLayouts with ConstraintLayout to reduce view hierarchy depth'
                    })
            
        except Exception as e:
            logger.error(f"Error in _check_android_layout_performance: {str(e)}")
        
        return findings
    
    def _check_android_hardcoded_sizes(self, ast_node: Node) -> List[Dict]:
        """
        Check for hardcoded sizes in Android layouts.
        
        This rule identifies hardcoded dp/px values that should use dimension resources.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for hardcoded sizes
        """
        findings = []
        
        # Query for attributes with hardcoded size values
        query_string = """
        (attribute
          (attribute_name) @attr_name
          (quoted_attribute_value) @attr_value) @attribute
        """
        
        size_attributes = [
            'android:layout_width', 'android:layout_height',
            'android:textSize', 'android:padding', 'android:margin',
            'android:paddingTop', 'android:paddingBottom', 'android:paddingLeft', 'android:paddingRight',
            'android:marginTop', 'android:marginBottom', 'android:marginLeft', 'android:marginRight'
        ]
        
        try:
            captures = self._query_ast(ast_node, query_string, 'xml')
            
            for _, capture_dict in captures:
                if 'attr_name' in capture_dict and 'attr_value' in capture_dict:
                    name_node = capture_dict['attr_name']
                    value_node = capture_dict['attr_value']
                    attr_name = name_node.text.decode('utf-8', errors='ignore')
                    attr_value = value_node.text.decode('utf-8', errors='ignore').strip('"\'')
                    
                    if (attr_name in size_attributes and 
                        ('dp' in attr_value or 'px' in attr_value or 'sp' in attr_value) and
                        not attr_value.startswith('@')):  # Not already a resource reference
                        findings.append({
                            'rule_id': 'ANDROID_HARDCODED_SIZE',
                            'message': f'Hardcoded size value found: {attr_name}="{attr_value}"',
                            'line': value_node.start_point[0] + 1,
                            'column': value_node.start_point[1] + 1,
                            'severity': 'Info',
                            'category': 'android_resources',
                            'suggestion': f'Move hardcoded size "{attr_value}" to dimension resources (dimens.xml)'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_android_hardcoded_sizes: {str(e)}")
        
        return findings
    
    def analyze_xml_ast(self, ast_node: Node) -> List[Dict]:
        """
        Analyze an XML AST (Android layouts, manifests) and return all findings.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: Combined list of findings from all XML/Android rules
        """
        findings = []
        
        # Execute all XML/Android static analysis rules
        rule_methods = [
            self._check_android_manifest_permissions,
            self._check_android_layout_performance,
            self._check_android_hardcoded_sizes
        ]
        
        for rule_method in rule_methods:
            try:
                rule_findings = rule_method(ast_node)
                findings.extend(rule_findings)
            except Exception as e:
                logger.error(f"Error executing XML/Android rule: {str(e)}")
        
        return findings
    
    def _check_javascript_console_log(self, ast_node: Node) -> List[Dict]:
        """
        Check for console.log() statements in JavaScript code.
        
        This rule identifies console.log statements that might be debugging leftovers
        or should use proper logging instead.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for console.log usage
        """
        findings = []
        
        # Query for console.log() calls
        query_string = """
        (call_expression
          function: (member_expression
            object: (identifier) @obj
            property: (property_identifier) @prop)
          arguments: (arguments)) @call
        (#eq? @obj "console")
        (#eq? @prop "log")
        """
        
        try:
            captures = self._query_ast(ast_node, query_string, 'javascript')
            
            for _, capture_dict in captures:
                if 'call' in capture_dict:
                    call_node = capture_dict['call']
                    findings.append({
                        'rule_id': 'JS_CONSOLE_LOG_FOUND',
                        'message': 'console.log() statement found - consider using proper logging',
                        'line': call_node.start_point[0] + 1,
                        'column': call_node.start_point[1] + 1,
                        'severity': 'Info',
                        'category': 'logging',
                        'suggestion': 'Replace console.log() with proper logging framework or remove before production'
                    })
            
        except Exception as e:
            logger.error(f"Error in _check_javascript_console_log: {str(e)}")
        
        return findings
    
    def _check_javascript_var_usage(self, ast_node: Node) -> List[Dict]:
        """
        Check for var keyword usage in JavaScript code.
        
        This rule identifies var declarations that should use let or const instead.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for var usage
        """
        findings = []
        
        # Query for var declarations
        query_string = """
        (variable_declaration
          (var) @var_keyword
          (variable_declarator)) @declaration
        """
        
        try:
            captures = self._query_ast(ast_node, query_string, 'javascript')
            
            for _, capture_dict in captures:
                if 'declaration' in capture_dict:
                    declaration_node = capture_dict['declaration']
                    findings.append({
                        'rule_id': 'JS_VAR_USAGE',
                        'message': 'var keyword found - consider using let or const instead',
                        'line': declaration_node.start_point[0] + 1,
                        'column': declaration_node.start_point[1] + 1,
                        'severity': 'Warning',
                        'category': 'best_practices',
                        'suggestion': 'Use let for mutable variables or const for immutable values instead of var'
                    })
            
        except Exception as e:
            logger.error(f"Error in _check_javascript_var_usage: {str(e)}")
        
        return findings
    
    def _check_javascript_equality_operators(self, ast_node: Node) -> List[Dict]:
        """
        Check for loose equality operators (== and !=) in JavaScript code.
        
        This rule identifies loose equality operators that should use strict equality.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for loose equality usage
        """
        findings = []
        
        # Query for loose equality operators
        query_string = """
        (binary_expression
          operator: "==" @operator) @expression
        """
        
        query_string_not_equal = """
        (binary_expression
          operator: "!=" @operator) @expression
        """
        
        try:
            # Check for == operator
            captures = self._query_ast(ast_node, query_string, 'javascript')
            for _, capture_dict in captures:
                if 'expression' in capture_dict:
                    expression_node = capture_dict['expression']
                    findings.append({
                        'rule_id': 'JS_LOOSE_EQUALITY',
                        'message': 'Loose equality operator (==) found - use strict equality (===) instead',
                        'line': expression_node.start_point[0] + 1,
                        'column': expression_node.start_point[1] + 1,
                        'severity': 'Warning',
                        'category': 'best_practices',
                        'suggestion': 'Replace == with === for strict equality comparison'
                    })
            
            # Check for != operator
            captures = self._query_ast(ast_node, query_string_not_equal, 'javascript')
            for _, capture_dict in captures:
                if 'expression' in capture_dict:
                    expression_node = capture_dict['expression']
                    findings.append({
                        'rule_id': 'JS_LOOSE_INEQUALITY',
                        'message': 'Loose inequality operator (!=) found - use strict inequality (!==) instead',
                        'line': expression_node.start_point[0] + 1,
                        'column': expression_node.start_point[1] + 1,
                        'severity': 'Warning',
                        'category': 'best_practices',
                        'suggestion': 'Replace != with !== for strict inequality comparison'
                    })
            
        except Exception as e:
            logger.error(f"Error in _check_javascript_equality_operators: {str(e)}")
        
        return findings
    
    def _check_javascript_function_too_long(self, ast_node: Node) -> List[Dict]:
        """
        Check for JavaScript functions that are too long (>50 lines).
        
        This rule identifies functions that might be too complex and should be refactored.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for overly long functions
        """
        findings = []
        
        # Query for function declarations
        query_string = """
        (function_declaration
          name: (identifier) @func_name) @func_def
        """
        
        # Query for function expressions
        query_string_expr = """
        (function_expression) @func_expr
        """
        
        # Query for arrow functions
        query_string_arrow = """
        (arrow_function) @arrow_func
        """
        
        try:
            # Check function declarations
            captures = self._query_ast(ast_node, query_string, 'javascript')
            for _, capture_dict in captures:
                if 'func_def' in capture_dict and 'func_name' in capture_dict:
                    func_node = capture_dict['func_def']
                    name_node = capture_dict['func_name']
                    func_name = name_node.text.decode('utf-8', errors='ignore')
                    
                    # Calculate function length
                    start_line = func_node.start_point[0]
                    end_line = func_node.end_point[0]
                    func_length = end_line - start_line + 1
                    
                    if func_length > 50:
                        findings.append({
                            'rule_id': 'JS_FUNCTION_TOO_LONG',
                            'message': f'Function "{func_name}" is too long ({func_length} lines)',
                            'line': start_line + 1,
                            'column': func_node.start_point[1] + 1,
                            'severity': 'Warning',
                            'category': 'complexity',
                            'suggestion': f'Consider breaking down function "{func_name}" into smaller, more focused functions'
                        })
            
            # Check function expressions and arrow functions
            for query in [query_string_expr, query_string_arrow]:
                captures = self._query_ast(ast_node, query, 'javascript')
                for _, capture_dict in captures:
                    func_key = 'func_expr' if 'func_expr' in capture_dict else 'arrow_func'
                    if func_key in capture_dict:
                        func_node = capture_dict[func_key]
                        
                        # Calculate function length
                        start_line = func_node.start_point[0]
                        end_line = func_node.end_point[0]
                        func_length = end_line - start_line + 1
                        
                        if func_length > 50:
                            func_type = "Function expression" if func_key == 'func_expr' else "Arrow function"
                            findings.append({
                                'rule_id': 'JS_FUNCTION_TOO_LONG',
                                'message': f'{func_type} is too long ({func_length} lines)',
                                'line': start_line + 1,
                                'column': func_node.start_point[1] + 1,
                                'severity': 'Warning',
                                'category': 'complexity',
                                'suggestion': f'Consider breaking down this {func_type.lower()} into smaller, more focused functions'
                            })
            
        except Exception as e:
            logger.error(f"Error in _check_javascript_function_too_long: {str(e)}")
        
        return findings
    
    def _check_javascript_unused_variables(self, ast_node: Node) -> List[Dict]:
        """
        Check for potentially unused variables in JavaScript code.
        
        This rule identifies variable declarations that might not be used.
        Note: This is a simplified check and may have false positives.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for potentially unused variables
        """
        findings = []
        
        # Query for variable declarations
        query_string = """
        (variable_declaration
          (variable_declarator
            name: (identifier) @var_name)) @declaration
        """
        
        try:
            captures = self._query_ast(ast_node, query_string, 'javascript')
            
            # Get all variable names
            declared_vars = set()
            for _, capture_dict in captures:
                if 'var_name' in capture_dict:
                    name_node = capture_dict['var_name']
                    var_name = name_node.text.decode('utf-8', errors='ignore')
                    declared_vars.add(var_name)
            
            # Simple check: look for variables that are declared but not referenced elsewhere
            # This is a basic implementation and may have false positives
            ast_text = ast_node.text.decode('utf-8', errors='ignore') if ast_node.text else ""
            
            for _, capture_dict in captures:
                if 'var_name' in capture_dict and 'declaration' in capture_dict:
                    name_node = capture_dict['var_name']
                    declaration_node = capture_dict['declaration']
                    var_name = name_node.text.decode('utf-8', errors='ignore')
                    
                    # Count occurrences of variable name in the code
                    # Subtract 1 for the declaration itself
                    usage_count = ast_text.count(var_name) - 1
                    
                    # If variable appears only once (the declaration), it might be unused
                    if usage_count == 0 and len(var_name) > 1:  # Ignore single-letter variables
                        findings.append({
                            'rule_id': 'JS_UNUSED_VARIABLE',
                            'message': f'Variable "{var_name}" appears to be unused',
                            'line': declaration_node.start_point[0] + 1,
                            'column': declaration_node.start_point[1] + 1,
                            'severity': 'Info',
                            'category': 'unused_code',
                            'suggestion': f'Remove unused variable "{var_name}" or use it in the code'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_javascript_unused_variables: {str(e)}")
        
        return findings
    
    def analyze_javascript_ast(self, ast_node: Node) -> List[Dict]:
        """
        Analyze a JavaScript AST and return all findings.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: Combined list of findings from all JavaScript rules
        """
        findings = []
        
        # Execute all JavaScript static analysis rules
        rule_methods = [
            self._check_javascript_console_log,
            self._check_javascript_var_usage,
            self._check_javascript_equality_operators,
            self._check_javascript_function_too_long,
            self._check_javascript_unused_variables
        ]
        
        for rule_method in rule_methods:
            try:
                rule_findings = rule_method(ast_node)
                findings.extend(rule_findings)
            except Exception as e:
                logger.error(f"Error executing JavaScript rule: {str(e)}")
        
        return findings

    def _check_dart_print_statements(self, ast_node: Node) -> List[Dict]:
        """
        Check for print() statements in Dart code.
        
        This rule identifies print statements that should be removed from production code.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for print statement usage
        """
        findings = []
        
        # Query for print() function calls
        query_string = """
        (invocation_expression
          function: (identifier) @func
          arguments: (argument_list)) @call
        (#eq? @func "print")
        """
        
        try:
            captures = self._query_ast(ast_node, query_string, 'dart')
            
            for _, capture_dict in captures:
                if 'call' in capture_dict:
                    call_node = capture_dict['call']
                    findings.append({
                        'rule_id': 'DART_PRINT_STATEMENT_FOUND',
                        'message': 'print() statement found - should be removed from production code',
                        'line': call_node.start_point[0] + 1,
                        'column': call_node.start_point[1] + 1,
                        'severity': 'Warning',
                        'category': 'debugging',
                        'suggestion': 'Remove print() statements or replace with proper logging (developer.log)'
                    })
            
        except Exception as e:
            logger.error(f"Error in _check_dart_print_statements: {str(e)}")
        
        return findings
    
    def _check_flutter_widget_key_usage(self, ast_node: Node) -> List[Dict]:
        """
        Check for missing keys in Flutter widget lists.
        
        This rule identifies ListView or Column children that might need keys for performance.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for missing widget keys
        """
        findings = []
        
        # Query for ListView or Column with children but no keys
        query_string = """
        (invocation_expression
          function: (identifier) @widget_name
          arguments: (argument_list
            (named_expression
              name: (label (identifier) @param_name)
              expression: (list_literal) @children_list))) @widget_call
        (#match? @widget_name "(ListView|Column|Row)")
        (#eq? @param_name "children")
        """
        
        try:
            captures = self._query_ast(ast_node, query_string, 'dart')
            
            for _, capture_dict in captures:
                if 'widget_call' in capture_dict and 'widget_name' in capture_dict:
                    widget_node = capture_dict['widget_call']
                    widget_name = capture_dict['widget_name'].text.decode('utf-8', errors='ignore')
                    
                    # Check if children list has multiple items (where keys would be beneficial)
                    children_list = capture_dict.get('children_list')
                    if children_list and len(children_list.children) > 3:  # More than 3 children
                        findings.append({
                            'rule_id': 'FLUTTER_WIDGET_KEY_USAGE',
                            'message': f'{widget_name} with multiple children should use keys for performance',
                            'line': widget_node.start_point[0] + 1,
                            'column': widget_node.start_point[1] + 1,
                            'severity': 'Info',
                            'category': 'flutter_performance',
                            'suggestion': f'Consider adding keys to {widget_name} children for better performance and state preservation'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_flutter_widget_key_usage: {str(e)}")
        
        return findings
    
    def _check_flutter_stateless_vs_stateful(self, ast_node: Node) -> List[Dict]:
        """
        Check for StatefulWidget that could be StatelessWidget.
        
        This rule identifies StatefulWidget classes that don't use setState.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for unnecessary StatefulWidget usage
        """
        findings = []
        
        # Query for StatefulWidget classes
        query_string = """
        (class_definition
          name: (identifier) @class_name
          superclass: (type_identifier) @superclass) @class_def
        (#eq? @superclass "StatefulWidget")
        """
        
        try:
            captures = self._query_ast(ast_node, query_string, 'dart')
            
            for _, capture_dict in captures:
                if 'class_def' in capture_dict and 'class_name' in capture_dict:
                    class_node = capture_dict['class_def']
                    class_name = capture_dict['class_name'].text.decode('utf-8', errors='ignore')
                    
                    # Check if the class or its State class uses setState
                    has_set_state = self._check_for_set_state_usage(class_node)
                    
                    if not has_set_state:
                        findings.append({
                            'rule_id': 'FLUTTER_STATELESS_VS_STATEFUL',
                            'message': f'StatefulWidget "{class_name}" doesn\'t use setState - consider StatelessWidget',
                            'line': class_node.start_point[0] + 1,
                            'column': class_node.start_point[1] + 1,
                            'severity': 'Info',
                            'category': 'flutter_optimization',
                            'suggestion': f'Consider converting "{class_name}" to StatelessWidget if no state management is needed'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_flutter_stateless_vs_stateful: {str(e)}")
        
        return findings
    
    def _check_dart_async_without_await(self, ast_node: Node) -> List[Dict]:
        """
        Check for async functions that don't use await.
        
        This rule identifies async functions that might not need to be async.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for unnecessary async usage
        """
        findings = []
        
        # Query for async functions
        query_string = """
        (function_signature
          name: (identifier) @func_name
          parameters: (formal_parameter_list)
          return_type: (type_annotation)?
          (function_body) @body) @func
        """
        
        try:
            captures = self._query_ast(ast_node, query_string, 'dart')
            
            for _, capture_dict in captures:
                if 'func' in capture_dict and 'func_name' in capture_dict and 'body' in capture_dict:
                    func_node = capture_dict['func']
                    func_name = capture_dict['func_name'].text.decode('utf-8', errors='ignore')
                    body_node = capture_dict['body']
                    
                    # Check if function is marked as async
                    func_text = func_node.text.decode('utf-8', errors='ignore')
                    if 'async' in func_text:
                        # Check if body contains await
                        body_text = body_node.text.decode('utf-8', errors='ignore')
                        if 'await' not in body_text:
                            findings.append({
                                'rule_id': 'DART_ASYNC_WITHOUT_AWAIT',
                                'message': f'Async function "{func_name}" doesn\'t use await',
                                'line': func_node.start_point[0] + 1,
                                'column': func_node.start_point[1] + 1,
                                'severity': 'Warning',
                                'category': 'async_patterns',
                                'suggestion': f'Remove async keyword from "{func_name}" if await is not used'
                            })
            
        except Exception as e:
            logger.error(f"Error in _check_dart_async_without_await: {str(e)}")
        
        return findings
    
    def _check_flutter_build_method_complexity(self, ast_node: Node) -> List[Dict]:
        """
        Check for complex build methods in Flutter widgets.
        
        This rule identifies build methods that are too long or complex.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of findings for complex build methods
        """
        findings = []
        
        # Query for build methods in Widget classes
        query_string = """
        (method_declaration
          name: (identifier) @method_name
          parameters: (formal_parameter_list)
          body: (function_body) @body) @method
        (#eq? @method_name "build")
        """
        
        try:
            captures = self._query_ast(ast_node, query_string, 'dart')
            
            for _, capture_dict in captures:
                if 'method' in capture_dict and 'body' in capture_dict:
                    method_node = capture_dict['method']
                    body_node = capture_dict['body']
                    
                    # Calculate method length in lines
                    start_line = method_node.start_point[0]
                    end_line = method_node.end_point[0]
                    method_length = end_line - start_line + 1
                    
                    # Check for complexity indicators
                    body_text = body_node.text.decode('utf-8', errors='ignore')
                    nested_widgets = body_text.count('(') - body_text.count(')')  # Rough nesting indicator
                    
                    if method_length > 30 or abs(nested_widgets) > 10:
                        findings.append({
                            'rule_id': 'FLUTTER_BUILD_METHOD_COMPLEXITY',
                            'message': f'Build method is complex ({method_length} lines) - consider extracting widgets',
                            'line': method_node.start_point[0] + 1,
                            'column': method_node.start_point[1] + 1,
                            'severity': 'Warning',
                            'category': 'flutter_complexity',
                            'suggestion': 'Break down complex build method into smaller widget methods or separate widgets'
                        })
            
        except Exception as e:
            logger.error(f"Error in _check_flutter_build_method_complexity: {str(e)}")
        
        return findings
    
    def analyze_dart_ast(self, ast_node: Node) -> List[Dict]:
        """
        Analyze Dart AST and return all findings.
        
        Args:
            ast_node (Node): Root AST node to analyze
            
        Returns:
            List[Dict]: List of all static analysis findings for Dart code
        """
        findings = []
        
        # List of Dart/Flutter analysis rules
        dart_rules = [
            self._check_dart_print_statements,
            self._check_flutter_widget_key_usage,
            self._check_flutter_stateless_vs_stateful,
            self._check_dart_async_without_await,
            self._check_flutter_build_method_complexity
        ]
        
        for rule in dart_rules:
            try:
                rule_findings = rule(ast_node)
                findings.extend(rule_findings)
            except Exception as e:
                logger.error(f"Error executing Dart rule: {str(e)}")
        
        return findings
    
    # Helper methods for Dart analysis
    
    def _check_for_set_state_usage(self, class_node: Node) -> bool:
        """
        Check if a class or its related State class uses setState.
        
        Args:
            class_node (Node): Class definition node
            
        Returns:
            bool: True if setState is used
        """
        try:
            class_text = class_node.text.decode('utf-8', errors='ignore')
            return 'setState' in class_text
        except Exception:
            return False