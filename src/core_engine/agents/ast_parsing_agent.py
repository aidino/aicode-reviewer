"""
ASTParsingAgent for AI Code Review System.

This module implements the ASTParsingAgent responsible for parsing source code
into Abstract Syntax Trees (ASTs) using Tree-sitter for structural analysis.
"""

import os
import tempfile
import logging
from typing import Dict, Optional, Any, List
from pathlib import Path

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


class ASTParsingAgent:
    """
    Agent responsible for parsing source code into Abstract Syntax Trees.
    
    This agent handles:
    - Initializing Tree-sitter parsers for supported languages
    - Parsing source code files into ASTs
    - Extracting structural information from ASTs
    - Managing language-specific parsing configurations
    """
    
    def __init__(self):
        """
        Initialize the ASTParsingAgent.
        
        Sets up Tree-sitter parsers and loads language grammars.
        
        Raises:
            ImportError: If tree-sitter is not installed
            Exception: If language grammars cannot be loaded
        """
        if tree_sitter is None:
            raise ImportError(
                "tree-sitter is not installed. Please install it with: pip install tree-sitter"
            )
        
        self.parser = None
        self.languages = {}
        self.supported_languages = ['python']  # Start with only Python support
        
        # Initialize parsers for supported languages
        self._initialize_parsers()
        
        logger.info(f"ASTParsingAgent initialized with languages: {self.supported_languages}")
    
    def _initialize_parsers(self) -> None:
        """
        Initialize Tree-sitter parsers for supported languages.
        
        Attempts to build and load language grammars. If a grammar fails to load,
        it will be removed from supported languages with a warning.
        
        Raises:
            Exception: If no languages can be loaded successfully
        """
        try:
            # Load Python language first
            python_lang = self._load_python_language()
            if python_lang:
                self.languages['python'] = python_lang
            
            # Try to load Java language if available
            java_lang = self._load_java_language()
            if java_lang:
                self.languages['java'] = java_lang
                if 'java' not in self.supported_languages:
                    self.supported_languages.append('java')
            
            if not self.languages:
                raise Exception("No language grammars could be loaded")
            
            # Create parser with first available language
            first_language = list(self.languages.values())[0]
            self.parser = Parser()
            self.parser.language = first_language  # Use language property instead of set_language
            
        except Exception as e:
            logger.error(f"Failed to initialize parsers: {str(e)}")
            raise
    
    def _load_python_language(self) -> Optional[Language]:
        """
        Load Python language grammar for Tree-sitter.
        
        Attempts multiple methods to load the Python grammar:
        1. From pre-built shared library
        2. From tree-sitter-python package if available
        3. Build from source if grammar files are available
        
        Returns:
            Optional[Language]: Python language object if successful, None otherwise
        """
        try:
            # Method 1: Try to load from pre-built library
            # This assumes tree-sitter-python is installed and built
            try:
                from tree_sitter_python import language
                lang_capsule = language()
                # Wrap PyCapsule with Language object for newer tree-sitter versions
                return Language(lang_capsule)
            except ImportError:
                logger.debug("tree-sitter-python package not found, trying alternative methods")
            
            # Method 2: Try to build from source if grammar files exist
            # Look for common locations where tree-sitter grammars might be
            possible_grammar_paths = [
                "/usr/local/lib/tree-sitter-grammars",
                "/opt/tree-sitter-grammars", 
                os.path.expanduser("~/.tree-sitter/grammars"),
                "./grammars",
                "./tree-sitter-grammars"
            ]
            
            for grammar_path in possible_grammar_paths:
                python_grammar_path = os.path.join(grammar_path, "tree-sitter-python")
                if os.path.exists(python_grammar_path):
                    try:
                        # Try to build language from grammar directory
                        language = Language.build_library(
                            # Output library path
                            os.path.join(tempfile.gettempdir(), "python.so"),
                            # Grammar directories
                            [python_grammar_path]
                        )
                        return language
                    except Exception as e:
                        logger.debug(f"Failed to build from {python_grammar_path}: {str(e)}")
                        continue
            
            # Method 3: Create a minimal fallback (this won't work for real parsing)
            logger.warning("Could not load Python grammar. AST parsing will be limited.")
            return None
            
        except Exception as e:
            logger.error(f"Error loading Python language: {str(e)}")
            return None
    
    def _load_java_language(self) -> Optional[Language]:
        """
        Load Java language grammar for Tree-sitter.
        
        Attempts multiple methods to load the Java grammar:
        1. From pre-built shared library
        2. From tree-sitter-java package if available
        3. Build from source if grammar files are available
        
        Returns:
            Optional[Language]: Java language object if successful, None otherwise
        """
        try:
            # Method 1: Try to load from pre-built library
            try:
                from tree_sitter_java import language
                lang_capsule = language()
                # Wrap PyCapsule with Language object for newer tree-sitter versions
                return Language(lang_capsule)
            except ImportError:
                logger.debug("tree-sitter-java package not found, trying alternative methods")
            
            # Method 2: Try to build from source if grammar files exist
            possible_grammar_paths = [
                "/usr/local/lib/tree-sitter-grammars",
                "/opt/tree-sitter-grammars", 
                os.path.expanduser("~/.tree-sitter/grammars"),
                "./grammars",
                "./tree-sitter-grammars"
            ]
            
            for grammar_path in possible_grammar_paths:
                java_grammar_path = os.path.join(grammar_path, "tree-sitter-java")
                if os.path.exists(java_grammar_path):
                    try:
                        # Try to build language from grammar directory
                        language = Language.build_library(
                            # Output library path
                            os.path.join(tempfile.gettempdir(), "java.so"),
                            # Grammar directories
                            [java_grammar_path]
                        )
                        return language
                    except Exception as e:
                        logger.debug(f"Failed to build from {java_grammar_path}: {str(e)}")
                        continue
            
            # Method 3: Create a minimal fallback (this won't work for real parsing)
            logger.warning("Could not load Java grammar. AST parsing will be limited.")
            return None
            
        except Exception as e:
            logger.error(f"Error loading Java language: {str(e)}")
            return None
    
    def _detect_language(self, file_path: str) -> Optional[str]:
        """
        Detect the programming language based on file extension.
        
        Args:
            file_path (str): Path to the source file
            
        Returns:
            Optional[str]: Detected language name or None if unsupported
        """
        file_ext = Path(file_path).suffix.lower()
        
        extension_map = {
            '.py': 'python',
            '.pyx': 'python',
            '.pyi': 'python',
            # Future extensions for other languages
            '.java': 'java',
            '.kt': 'kotlin',
            '.kts': 'kotlin'
        }
        
        detected_lang = extension_map.get(file_ext)
        
        # Only return if we support this language
        if detected_lang and detected_lang in self.supported_languages:
            return detected_lang
        
        return None
    
    def parse_code_to_ast(self, code_content: str, language: str) -> Optional[Node]:
        """
        Parse source code content into an Abstract Syntax Tree.
        
        Args:
            code_content (str): Source code content to parse
            language (str): Programming language ('python', 'java')
            
        Returns:
            Optional[Node]: Root node of the AST if successful, None if parsing fails
            
        Raises:
            ValueError: If language is not supported
            Exception: If parsing fails critically
        """
        try:
            # Validate language support
            if language not in self.supported_languages:
                raise ValueError(f"Language '{language}' is not supported. Supported languages: {self.supported_languages}")
            
            if language not in self.languages:
                raise ValueError(f"Language '{language}' grammar is not loaded")
            
            # Set parser language
            language_obj = self.languages[language]
            self.parser.language = language_obj  # Use language property instead of set_language
            
            # Convert string to bytes (required by tree-sitter)
            code_bytes = code_content.encode('utf-8')
            
            # Parse the code
            tree = self.parser.parse(code_bytes)
            
            if tree is None:
                logger.error(f"Failed to parse {language} code - parser returned None")
                return None
            
            root_node = tree.root_node
            
            if root_node is None:
                logger.error(f"Failed to get root node from {language} AST")
                return None
            
            # Check for parsing errors
            if root_node.has_error:
                logger.warning(f"AST contains parsing errors for {language} code")
                # Still return the AST as it might be partially useful
            
            logger.debug(f"Successfully parsed {language} code into AST with {root_node.child_count} top-level nodes")
            return root_node
            
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Critical error parsing {language} code: {str(e)}")
            raise Exception(f"Failed to parse {language} code: {str(e)}")
    
    def parse_file_to_ast(self, file_path: str, language: Optional[str] = None) -> Optional[Node]:
        """
        Parse a source code file into an Abstract Syntax Tree.
        
        Args:
            file_path (str): Path to the source code file
            language (Optional[str]): Programming language, auto-detected if None
            
        Returns:
            Optional[Node]: Root node of the AST if successful, None if parsing fails
        """
        try:
            # Auto-detect language if not provided
            if language is None:
                language = self._detect_language(file_path)
                if language is None:
                    logger.warning(f"Could not detect language for file: {file_path}")
                    return None
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code_content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                with open(file_path, 'r', encoding='latin-1') as f:
                    code_content = f.read()
            
            # Parse the content
            return self.parse_code_to_ast(code_content, language)
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {str(e)}")
            return None
    
    def extract_structural_info(self, ast_node: Node, language: str) -> Dict[str, Any]:
        """
        Extract structural information from AST.
        
        Args:
            ast_node (Node): AST node to analyze
            language (str): Programming language
            
        Returns:
            Dict[str, Any]: Extracted structural information
        """
        if language == 'python':
            return self._extract_python_structure(ast_node)
        elif language == 'java':
            return self._extract_java_structure(ast_node)
        else:
            logger.warning(f"Structural extraction not implemented for {language}")
            return {
                "language": language,
                "classes": [],
                "functions": [],
                "methods": [],
                "imports": [],
                "node_count": self._count_nodes(ast_node)
            }
    
    def _extract_python_structure(self, ast_node: Node) -> Dict[str, Any]:
        """
        Extract Python-specific structural information from AST.
        
        Args:
            ast_node (Node): Python AST root node
            
        Returns:
            Dict[str, Any]: Python structural information
        """
        structure = {
            "classes": [],
            "functions": [],
            "imports": [],
            "language": "python",
            "node_count": self._count_nodes(ast_node)
        }
        
        try:
            # Traverse AST to find structural elements
            self._traverse_python_ast(ast_node, structure)
        except Exception as e:
            logger.error(f"Error traversing Python AST: {str(e)}")
            structure["error"] = str(e)
        
        return structure
    
    def _traverse_python_ast(self, node: Node, structure: Dict[str, Any]) -> None:
        """
        Recursively traverse Python AST to extract structural elements.
        
        Args:
            node (Node): Current AST node
            structure (Dict[str, Any]): Structure dictionary to populate
        """
        if node.type == 'class_definition':
            class_info = {
                "name": self._get_node_text(node, 'identifier'),
                "line": node.start_point[0] + 1,
                "methods": []
            }
            
            # Find methods in the class
            for child in node.children:
                if child.type == 'block':
                    for stmt in child.children:
                        if stmt.type == 'function_definition':
                            method_name = self._get_node_text(stmt, 'identifier')
                            if method_name:
                                class_info["methods"].append({
                                    "name": method_name,
                                    "line": stmt.start_point[0] + 1
                                })
            
            structure["classes"].append(class_info)
        
        elif node.type == 'function_definition':
            func_name = self._get_node_text(node, 'identifier')
            if func_name:
                structure["functions"].append({
                    "name": func_name,
                    "line": node.start_point[0] + 1
                })
        
        elif node.type in ['import_statement', 'import_from_statement']:
            import_info = {
                "type": node.type,
                "line": node.start_point[0] + 1,
                "text": node.text.decode('utf-8') if node.text else ""
            }
            structure["imports"].append(import_info)
        
        # Recursively process children
        for child in node.children:
            self._traverse_python_ast(child, structure)
    
    def _get_node_text(self, node: Node, target_type: str) -> Optional[str]:
        """
        Get text content of a specific child node type.
        
        Args:
            node (Node): Parent node
            target_type (str): Type of child node to find
            
        Returns:
            Optional[str]: Text content of the target node
        """
        for child in node.children:
            if child.type == target_type:
                return child.text.decode('utf-8') if child.text else None
        return None
    
    def _count_nodes(self, node: Node) -> int:
        """
        Count total number of nodes in AST.
        
        Args:
            node (Node): Root node
            
        Returns:
            int: Total node count
        """
        if not hasattr(node, 'children') or not node.children:
            return 1
        
        count = 1  # Count current node
        for child in node.children:
            count += self._count_nodes(child)  # Recursively count child and its descendants
        return count
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of currently supported languages.
        
        Returns:
            List[str]: List of supported language names
        """
        return self.supported_languages.copy()
    
    def is_language_supported(self, language: str) -> bool:
        """
        Check if a language is supported for parsing.
        
        Args:
            language (str): Language name to check
            
        Returns:
            bool: True if language is supported
        """
        return language in self.supported_languages
    
    def _extract_java_structure(self, ast_node: Node) -> Dict[str, Any]:
        """
        Extract structural information from Java AST.
        
        Args:
            ast_node (Node): Root AST node
            
        Returns:
            Dict[str, Any]: Extracted structural information
        """
        structure = {
            "language": "java",
            "imports": [],
            "classes": [],
            "methods": [],
            "functions": [],
            "node_count": self._count_nodes(ast_node)
        }
        
        if not hasattr(ast_node, 'children') or not ast_node.children:
            return structure
        
        # Process all nodes
        for node in ast_node.children:
            if not isinstance(node, Node):
                continue
                
            if node.type == 'import_declaration':
                structure['imports'].append(node.text.decode('utf-8'))
            elif node.type == 'class_declaration':
                class_info = self._extract_java_class_info(node)
                if class_info:
                    structure['classes'].append(class_info)
            elif node.type == 'method_declaration':
                method_info = self._extract_java_method_info(node)
                if method_info:
                    structure['methods'].append(method_info)
        
        return structure

    def _extract_java_class_info(self, node: Node) -> Dict[str, Any]:
        """
        Extract Java class information from a class declaration node.
        
        Args:
            node (Node): Java class declaration node
            
        Returns:
            Dict[str, Any]: Extracted class information
        """
        class_info = {
            "name": self._get_node_text(node, 'identifier'),
            "line": node.start_point[0] + 1,
            "methods": []
        }
        
        # Find methods in the class
        for child in node.children:
            if child.type == 'class_body':
                for stmt in child.children:
                    if stmt.type == 'method_declaration':
                        method_name = self._get_node_text(stmt, 'identifier')
                        if method_name:
                            class_info["methods"].append({
                                "name": method_name,
                                "line": stmt.start_point[0] + 1
                            })
        
        return class_info

    def _extract_java_method_info(self, node: Node) -> Dict[str, Any]:
        """
        Extract Java method information from a method declaration node.
        
        Args:
            node (Node): Java method declaration node
            
        Returns:
            Dict[str, Any]: Extracted method information
        """
        method_name = self._get_node_text(node, 'identifier')
        if method_name:
            return {
                "name": method_name,
                "line": node.start_point[0] + 1
            }
        return None 