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
            
            # Try to load Kotlin language if available
            kotlin_lang = self._load_kotlin_language()
            if kotlin_lang:
                self.languages['kotlin'] = kotlin_lang
                if 'kotlin' not in self.supported_languages:
                    self.supported_languages.append('kotlin')
            
            # Try to load XML language if available
            xml_lang = self._load_xml_language()
            if xml_lang:
                self.languages['xml'] = xml_lang
                if 'xml' not in self.supported_languages:
                    self.supported_languages.append('xml')
            
            # Try to load JavaScript language if available
            javascript_lang = self._load_javascript_language()
            if javascript_lang:
                self.languages['javascript'] = javascript_lang
                if 'javascript' not in self.supported_languages:
                    self.supported_languages.append('javascript')
            
            # Try to load Dart language if available
            dart_lang = self._load_dart_language()
            if dart_lang:
                self.languages['dart'] = dart_lang
                if 'dart' not in self.supported_languages:
                    self.supported_languages.append('dart')
            
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
    
    def _load_kotlin_language(self) -> Optional[Language]:
        """
        Load Kotlin language grammar for Tree-sitter.
        
        Attempts multiple methods to load the Kotlin grammar:
        1. From pre-built shared library
        2. From tree-sitter-kotlin package if available
        3. Build from source if grammar files are available
        
        Returns:
            Optional[Language]: Kotlin language object if successful, None otherwise
        """
        try:
            # Method 1: Try to load from pre-built library
            try:
                from tree_sitter_kotlin import language
                lang_capsule = language()
                # Wrap PyCapsule with Language object for newer tree-sitter versions
                return Language(lang_capsule)
            except ImportError:
                logger.debug("tree-sitter-kotlin package not found, trying alternative methods")
            
            # Method 2: Try to build from source if grammar files exist
            possible_grammar_paths = [
                "/usr/local/lib/tree-sitter-grammars",
                "/opt/tree-sitter-grammars", 
                os.path.expanduser("~/.tree-sitter/grammars"),
                "./grammars",
                "./tree-sitter-grammars"
            ]
            
            for grammar_path in possible_grammar_paths:
                kotlin_grammar_path = os.path.join(grammar_path, "tree-sitter-kotlin")
                if os.path.exists(kotlin_grammar_path):
                    try:
                        # Try to build language from grammar directory
                        language = Language.build_library(
                            # Output library path
                            os.path.join(tempfile.gettempdir(), "kotlin.so"),
                            # Grammar directories
                            [kotlin_grammar_path]
                        )
                        return language
                    except Exception as e:
                        logger.debug(f"Failed to build from {kotlin_grammar_path}: {str(e)}")
                        continue
            
            # Method 3: Create a minimal fallback (this won't work for real parsing)
            logger.warning("Could not load Kotlin grammar. AST parsing will be limited.")
            return None
            
        except Exception as e:
            logger.error(f"Error loading Kotlin language: {str(e)}")
            return None
    
    def _load_xml_language(self) -> Optional[Language]:
        """
        Load XML language grammar for Tree-sitter.
        
        Attempts multiple methods to load the XML grammar:
        1. From pre-built shared library
        2. From tree-sitter-xml package if available
        3. Build from source if grammar files are available
        
        Returns:
            Optional[Language]: XML language object if successful, None otherwise
        """
        try:
            # Method 1: Try to load from pre-built library
            try:
                from tree_sitter_xml import language
                lang_capsule = language()
                # Wrap PyCapsule with Language object for newer tree-sitter versions
                return Language(lang_capsule)
            except ImportError:
                logger.debug("tree-sitter-xml package not found, trying alternative methods")
            
            # Method 2: Try to build from source if grammar files exist
            possible_grammar_paths = [
                "/usr/local/lib/tree-sitter-grammars",
                "/opt/tree-sitter-grammars", 
                os.path.expanduser("~/.tree-sitter/grammars"),
                "./grammars",
                "./tree-sitter-grammars"
            ]
            
            for grammar_path in possible_grammar_paths:
                xml_grammar_path = os.path.join(grammar_path, "tree-sitter-xml")
                if os.path.exists(xml_grammar_path):
                    try:
                        # Try to build language from grammar directory
                        language = Language.build_library(
                            # Output library path
                            os.path.join(tempfile.gettempdir(), "xml.so"),
                            # Grammar directories
                            [xml_grammar_path]
                        )
                        return language
                    except Exception as e:
                        logger.debug(f"Failed to build from {xml_grammar_path}: {str(e)}")
                        continue
            
            # Method 3: Create a minimal fallback (this won't work for real parsing)
            logger.warning("Could not load XML grammar. AST parsing will be limited.")
            return None
            
        except Exception as e:
            logger.error(f"Error loading XML language: {str(e)}")
            return None
    
    def _load_javascript_language(self) -> Optional[Language]:
        """
        Load JavaScript language grammar for Tree-sitter.
        
        Attempts multiple methods to load the JavaScript grammar:
        1. From pre-built shared library
        2. From tree-sitter-javascript package if available
        3. Build from source if grammar files are available
        
        Returns:
            Optional[Language]: JavaScript language object if successful, None otherwise
        """
        try:
            # Method 1: Try to load from pre-built library
            try:
                from tree_sitter_javascript import language
                lang_capsule = language()
                # Wrap PyCapsule with Language object for newer tree-sitter versions
                return Language(lang_capsule)
            except ImportError:
                logger.debug("tree-sitter-javascript package not found, trying alternative methods")
            
            # Method 2: Try to build from source if grammar files exist
            possible_grammar_paths = [
                "/usr/local/lib/tree-sitter-grammars",
                "/opt/tree-sitter-grammars", 
                os.path.expanduser("~/.tree-sitter/grammars"),
                "./grammars",
                "./tree-sitter-grammars"
            ]
            
            for grammar_path in possible_grammar_paths:
                javascript_grammar_path = os.path.join(grammar_path, "tree-sitter-javascript")
                if os.path.exists(javascript_grammar_path):
                    try:
                        # Try to build language from grammar directory
                        language = Language.build_library(
                            # Output library path
                            os.path.join(tempfile.gettempdir(), "javascript.so"),
                            # Grammar directories
                            [javascript_grammar_path]
                        )
                        return language
                    except Exception as e:
                        logger.debug(f"Failed to build from {javascript_grammar_path}: {str(e)}")
                        continue
            
            # Method 3: Create a minimal fallback (this won't work for real parsing)
            logger.warning("Could not load JavaScript grammar. AST parsing will be limited.")
            return None
            
        except Exception as e:
            logger.error(f"Error loading JavaScript language: {str(e)}")
            return None
    
    def _load_dart_language(self) -> Optional[Language]:
        """
        Load Dart language grammar for Tree-sitter.
        
        Attempts multiple methods to load the Dart grammar:
        1. From pre-built shared library
        2. From tree-sitter-dart package if available
        3. Build from source if grammar files are available
        
        Returns:
            Optional[Language]: Dart language object if successful, None otherwise
        """
        try:
            # Method 1: Try to load from tree-sitter-language-pack (preferred)
            try:
                from tree_sitter_language_pack import get_language
                return get_language("dart")
            except ImportError:
                logger.debug("tree_sitter_language_pack not found, trying alternative methods")
            except Exception as e:
                logger.debug(f"Failed to get Dart from language pack: {str(e)}")
            
            # Method 2: Try to load from tree-sitter-dart package
            try:
                from tree_sitter_dart import language
                lang_capsule = language()
                # Wrap PyCapsule with Language object for newer tree-sitter versions
                return Language(lang_capsule)
            except ImportError:
                logger.debug("tree-sitter-dart package not found, trying alternative methods")
            
            # Method 2: Try to build from source if grammar files exist
            possible_grammar_paths = [
                "/usr/local/lib/tree-sitter-grammars",
                "/opt/tree-sitter-grammars", 
                os.path.expanduser("~/.tree-sitter/grammars"),
                "./grammars",
                "./tree-sitter-grammars"
            ]
            
            for grammar_path in possible_grammar_paths:
                dart_grammar_path = os.path.join(grammar_path, "tree-sitter-dart")
                if os.path.exists(dart_grammar_path):
                    try:
                        # Try to build language from grammar directory
                        language = Language.build_library(
                            # Output library path
                            os.path.join(tempfile.gettempdir(), "dart.so"),
                            # Grammar directories
                            [dart_grammar_path]
                        )
                        return language
                    except Exception as e:
                        logger.debug(f"Failed to build from {dart_grammar_path}: {str(e)}")
                        continue
            
            # Method 3: Create a minimal fallback (this won't work for real parsing)
            logger.warning("Could not load Dart grammar. AST parsing will be limited.")
            return None
            
        except Exception as e:
            logger.error(f"Error loading Dart language: {str(e)}")
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
            # Java
            '.java': 'java',
            # Kotlin
            '.kt': 'kotlin',
            '.kts': 'kotlin',
            # XML (Android layouts, manifests, resources)
            '.xml': 'xml',
            # JavaScript and TypeScript
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'javascript',  # TypeScript can be parsed with JavaScript grammar
            '.tsx': 'javascript',
            '.mjs': 'javascript',
            '.cjs': 'javascript',
            # Dart
            '.dart': 'dart'
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
        elif language == 'kotlin':
            return self._extract_kotlin_structure(ast_node)
        elif language == 'xml':
            return self._extract_xml_structure(ast_node)
        elif language == 'javascript':
            return self._extract_javascript_structure(ast_node)
        elif language == 'dart':
            return self._extract_dart_structure(ast_node)
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
    
    def _extract_kotlin_structure(self, ast_node: Node) -> Dict[str, Any]:
        """
        Extract structural information from Kotlin AST.
        
        Args:
            ast_node (Node): Root AST node
            
        Returns:
            Dict[str, Any]: Extracted structural information
        """
        structure = {
            "language": "kotlin",
            "imports": [],
            "classes": [],
            "methods": [],
            "functions": [],
            "objects": [],  # Kotlin objects
            "interfaces": [],  # Kotlin interfaces
            "data_classes": [],  # Kotlin data classes
            "node_count": self._count_nodes(ast_node)
        }
        
        if not hasattr(ast_node, 'children') or not ast_node.children:
            return structure
        
        try:
            self._traverse_kotlin_ast(ast_node, structure)
        except Exception as e:
            logger.error(f"Error traversing Kotlin AST: {str(e)}")
            structure["error"] = str(e)
        
        return structure
    
    def _traverse_kotlin_ast(self, node: Node, structure: Dict[str, Any]) -> None:
        """
        Recursively traverse Kotlin AST to extract structural elements.
        
        Args:
            node (Node): Current AST node
            structure (Dict[str, Any]): Structure dictionary to populate
        """
        # Kotlin import statements
        if node.type == 'import_header':
            import_info = {
                "type": node.type,
                "line": node.start_point[0] + 1,
                "text": node.text.decode('utf-8') if node.text else ""
            }
            structure["imports"].append(import_info)
        
        # Kotlin class declarations
        elif node.type == 'class_declaration':
            class_info = self._extract_kotlin_class_info(node)
            if class_info:
                if 'data class' in node.text.decode('utf-8', errors='ignore'):
                    structure["data_classes"].append(class_info)
                else:
                    structure["classes"].append(class_info)
        
        # Kotlin object declarations
        elif node.type == 'object_declaration':
            object_info = self._extract_kotlin_object_info(node)
            if object_info:
                structure["objects"].append(object_info)
        
        # Kotlin interface declarations
        elif node.type == 'interface_declaration':
            interface_info = self._extract_kotlin_interface_info(node)
            if interface_info:
                structure["interfaces"].append(interface_info)
        
        # Kotlin function declarations
        elif node.type == 'function_declaration':
            func_info = self._extract_kotlin_function_info(node)
            if func_info:
                structure["functions"].append(func_info)
        
        # Recursively process children
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                self._traverse_kotlin_ast(child, structure)
    
    def _extract_kotlin_class_info(self, node: Node) -> Dict[str, Any]:
        """
        Extract Kotlin class information from a class declaration node.
        
        Args:
            node (Node): Kotlin class declaration node
            
        Returns:
            Dict[str, Any]: Extracted class information
        """
        class_info = {
            "name": self._get_node_text(node, 'type_identifier') or self._get_node_text(node, 'simple_identifier'),
            "line": node.start_point[0] + 1,
            "methods": [],
            "properties": []
        }
        
        # Find methods and properties in the class
        for child in node.children:
            if child.type == 'class_body':
                for stmt in child.children:
                    if stmt.type == 'function_declaration':
                        method_name = self._get_node_text(stmt, 'simple_identifier')
                        if method_name:
                            class_info["methods"].append({
                                "name": method_name,
                                "line": stmt.start_point[0] + 1
                            })
                    elif stmt.type == 'property_declaration':
                        prop_name = self._get_node_text(stmt, 'simple_identifier')
                        if prop_name:
                            class_info["properties"].append({
                                "name": prop_name,
                                "line": stmt.start_point[0] + 1
                            })
        
        return class_info
    
    def _extract_kotlin_object_info(self, node: Node) -> Dict[str, Any]:
        """
        Extract Kotlin object information from an object declaration node.
        
        Args:
            node (Node): Kotlin object declaration node
            
        Returns:
            Dict[str, Any]: Extracted object information
        """
        return {
            "name": self._get_node_text(node, 'type_identifier') or self._get_node_text(node, 'simple_identifier'),
            "line": node.start_point[0] + 1,
            "type": "object"
        }
    
    def _extract_kotlin_interface_info(self, node: Node) -> Dict[str, Any]:
        """
        Extract Kotlin interface information from an interface declaration node.
        
        Args:
            node (Node): Kotlin interface declaration node
            
        Returns:
            Dict[str, Any]: Extracted interface information
        """
        return {
            "name": self._get_node_text(node, 'type_identifier') or self._get_node_text(node, 'simple_identifier'),
            "line": node.start_point[0] + 1,
            "type": "interface"
        }
    
    def _extract_kotlin_function_info(self, node: Node) -> Dict[str, Any]:
        """
        Extract Kotlin function information from a function declaration node.
        
        Args:
            node (Node): Kotlin function declaration node
            
        Returns:
            Dict[str, Any]: Extracted function information
        """
        func_name = self._get_node_text(node, 'simple_identifier')
        if func_name:
            return {
                "name": func_name,
                "line": node.start_point[0] + 1
            }
        return None
    
    def _extract_xml_structure(self, ast_node: Node) -> Dict[str, Any]:
        """
        Extract structural information from XML AST (for Android layouts, manifests).
        
        Args:
            ast_node (Node): Root AST node
            
        Returns:
            Dict[str, Any]: Extracted structural information
        """
        structure = {
            "language": "xml",
            "root_element": None,
            "elements": [],
            "attributes": [],
            "android_components": [],  # Android-specific components
            "permissions": [],  # Android permissions (for manifests)
            "activities": [],  # Android activities (for manifests)
            "services": [],  # Android services (for manifests)
            "node_count": self._count_nodes(ast_node)
        }
        
        if not hasattr(ast_node, 'children') or not ast_node.children:
            return structure
        
        try:
            self._traverse_xml_ast(ast_node, structure)
        except Exception as e:
            logger.error(f"Error traversing XML AST: {str(e)}")
            structure["error"] = str(e)
        
        return structure
    
    def _traverse_xml_ast(self, node: Node, structure: Dict[str, Any]) -> None:
        """
        Recursively traverse XML AST to extract structural elements.
        
        Args:
            node (Node): Current AST node
            structure (Dict[str, Any]): Structure dictionary to populate
        """
        # XML elements
        if node.type == 'element':
            element_info = self._extract_xml_element_info(node)
            if element_info:
                structure["elements"].append(element_info)
                
                # Check for Android-specific components
                tag_name = element_info.get("name", "").lower()
                if any(android_tag in tag_name for android_tag in [
                    'activity', 'service', 'receiver', 'provider',
                    'linearlayout', 'relativelayout', 'constraintlayout', 
                    'recyclerview', 'button', 'textview', 'edittext'
                ]):
                    structure["android_components"].append(element_info)
                
                # Extract Android manifest-specific elements
                if tag_name == 'uses-permission':
                    permission_name = self._get_xml_attribute_value(node, 'android:name')
                    if permission_name:
                        structure["permissions"].append({
                            "name": permission_name,
                            "line": node.start_point[0] + 1
                        })
                elif tag_name == 'activity':
                    activity_name = self._get_xml_attribute_value(node, 'android:name')
                    if activity_name:
                        structure["activities"].append({
                            "name": activity_name,
                            "line": node.start_point[0] + 1
                        })
                elif tag_name == 'service':
                    service_name = self._get_xml_attribute_value(node, 'android:name')
                    if service_name:
                        structure["services"].append({
                            "name": service_name,
                            "line": node.start_point[0] + 1
                        })
                
                # Set root element if not set
                if structure["root_element"] is None:
                    structure["root_element"] = element_info["name"]
        
        # XML attributes
        elif node.type == 'attribute':
            attr_info = self._extract_xml_attribute_info(node)
            if attr_info:
                structure["attributes"].append(attr_info)
        
        # Recursively process children
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                self._traverse_xml_ast(child, structure)
    
    def _extract_xml_element_info(self, node: Node) -> Dict[str, Any]:
        """
        Extract XML element information from an element node.
        
        Args:
            node (Node): XML element node
            
        Returns:
            Dict[str, Any]: Extracted element information
        """
        # Get element name from start tag
        element_name = None
        attributes = []
        
        for child in node.children:
            if child.type == 'start_tag':
                for tag_child in child.children:
                    if tag_child.type == 'name':
                        element_name = tag_child.text.decode('utf-8') if tag_child.text else None
                    elif tag_child.type == 'attribute':
                        attr_info = self._extract_xml_attribute_info(tag_child)
                        if attr_info:
                            attributes.append(attr_info)
        
        return {
            "name": element_name,
            "line": node.start_point[0] + 1,
            "attributes": attributes
        }
    
    def _extract_xml_attribute_info(self, node: Node) -> Dict[str, Any]:
        """
        Extract XML attribute information from an attribute node.
        
        Args:
            node (Node): XML attribute node
            
        Returns:
            Dict[str, Any]: Extracted attribute information
        """
        attr_name = None
        attr_value = None
        
        for child in node.children:
            if child.type == 'attribute_name':
                attr_name = child.text.decode('utf-8') if child.text else None
            elif child.type == 'quoted_attribute_value':
                attr_value = child.text.decode('utf-8').strip('"\'') if child.text else None
        
        return {
            "name": attr_name,
            "value": attr_value,
            "line": node.start_point[0] + 1
        }
    
    def _get_xml_attribute_value(self, node: Node, attr_name: str) -> Optional[str]:
        """
        Get the value of a specific XML attribute from an element node.
        
        Args:
            node (Node): XML element node
            attr_name (str): Name of the attribute to find
            
        Returns:
            Optional[str]: Attribute value if found
        """
        for child in node.children:
            if child.type == 'start_tag':
                for tag_child in child.children:
                    if tag_child.type == 'attribute':
                        attr_info = self._extract_xml_attribute_info(tag_child)
                        if attr_info and attr_info.get("name") == attr_name:
                            return attr_info.get("value")
        return None
    
    def _extract_javascript_structure(self, ast_node: Node) -> Dict[str, Any]:
        """
        Extract structural information from JavaScript/TypeScript AST.
        
        Args:
            ast_node (Node): Root AST node
            
        Returns:
            Dict[str, Any]: Extracted structural information
        """
        structure = {
            "language": "javascript",
            "imports": [],
            "exports": [],
            "classes": [],
            "functions": [],
            "variables": [],
            "arrow_functions": [],
            "async_functions": [],
            "node_count": self._count_nodes(ast_node)
        }
        
        if not hasattr(ast_node, 'children') or not ast_node.children:
            return structure
        
        try:
            self._traverse_javascript_ast(ast_node, structure)
        except Exception as e:
            logger.error(f"Error traversing JavaScript AST: {str(e)}")
            structure["error"] = str(e)
        
        return structure
    
    def _traverse_javascript_ast(self, node: Node, structure: Dict[str, Any]) -> None:
        """
        Recursively traverse JavaScript AST to extract structural elements.
        
        Args:
            node (Node): Current AST node
            structure (Dict[str, Any]): Structure dictionary to populate
        """
        # Class declarations
        if node.type == 'class_declaration':
            class_info = self._extract_javascript_class_info(node)
            if class_info:
                structure["classes"].append(class_info)
        
        # Function declarations
        elif node.type == 'function_declaration':
            func_info = self._extract_javascript_function_info(node)
            if func_info:
                if func_info.get("is_async"):
                    structure["async_functions"].append(func_info)
                else:
                    structure["functions"].append(func_info)
        
        # Arrow functions
        elif node.type == 'arrow_function':
            arrow_func_info = self._extract_javascript_arrow_function_info(node)
            if arrow_func_info:
                structure["arrow_functions"].append(arrow_func_info)
        
        # Variable declarations
        elif node.type == 'variable_declaration':
            var_info = self._extract_javascript_variable_info(node)
            if var_info:
                structure["variables"].extend(var_info)
        
        # Import statements
        elif node.type == 'import_statement':
            import_info = self._extract_javascript_import_info(node)
            if import_info:
                structure["imports"].append(import_info)
        
        # Export statements
        elif node.type in ['export_statement', 'export_default_declaration']:
            export_info = self._extract_javascript_export_info(node)
            if export_info:
                structure["exports"].append(export_info)
        
        # Method definitions (inside classes)
        elif node.type == 'method_definition':
            method_info = self._extract_javascript_method_info(node)
            if method_info:
                # This will be handled by class extraction
                pass
        
        # Recursively process children
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                self._traverse_javascript_ast(child, structure)
    
    def _extract_javascript_class_info(self, node: Node) -> Dict[str, Any]:
        """
        Extract JavaScript class information from a class declaration node.
        
        Args:
            node (Node): JavaScript class declaration node
            
        Returns:
            Dict[str, Any]: Extracted class information
        """
        class_name = None
        extends_class = None
        methods = []
        
        for child in node.children:
            if child.type == 'identifier':
                class_name = child.text.decode('utf-8') if child.text else None
            elif child.type == 'class_heritage':
                # Find extends clause
                for heritage_child in child.children:
                    if heritage_child.type == 'identifier':
                        extends_class = heritage_child.text.decode('utf-8') if heritage_child.text else None
            elif child.type == 'class_body':
                # Extract methods from class body
                for body_child in child.children:
                    if body_child.type == 'method_definition':
                        method_info = self._extract_javascript_method_info(body_child)
                        if method_info:
                            methods.append(method_info)
        
        return {
            "name": class_name,
            "line": node.start_point[0] + 1,
            "extends": extends_class,
            "methods": methods
        }
    
    def _extract_javascript_function_info(self, node: Node) -> Dict[str, Any]:
        """
        Extract JavaScript function information from a function declaration node.
        
        Args:
            node (Node): JavaScript function declaration node
            
        Returns:
            Dict[str, Any]: Extracted function information
        """
        func_name = None
        is_async = False
        parameters = []
        
        # Check if function is async
        if node.text and b'async' in node.text:
            is_async = True
        
        for child in node.children:
            if child.type == 'identifier':
                func_name = child.text.decode('utf-8') if child.text else None
            elif child.type == 'formal_parameters':
                # Extract parameter names
                for param_child in child.children:
                    if param_child.type == 'identifier':
                        param_name = param_child.text.decode('utf-8') if param_child.text else None
                        if param_name:
                            parameters.append(param_name)
        
        return {
            "name": func_name,
            "line": node.start_point[0] + 1,
            "is_async": is_async,
            "parameters": parameters
        }
    
    def _extract_javascript_method_info(self, node: Node) -> Dict[str, Any]:
        """
        Extract JavaScript method information from a method definition node.
        
        Args:
            node (Node): JavaScript method definition node
            
        Returns:
            Dict[str, Any]: Extracted method information
        """
        method_name = None
        is_static = False
        is_async = False
        parameters = []
        
        # Check for static and async modifiers
        if node.text:
            text = node.text.decode('utf-8')
            is_static = 'static' in text
            is_async = 'async' in text
        
        for child in node.children:
            if child.type == 'property_identifier':
                method_name = child.text.decode('utf-8') if child.text else None
            elif child.type == 'formal_parameters':
                # Extract parameter names
                for param_child in child.children:
                    if param_child.type == 'identifier':
                        param_name = param_child.text.decode('utf-8') if param_child.text else None
                        if param_name:
                            parameters.append(param_name)
        
        return {
            "name": method_name,
            "line": node.start_point[0] + 1,
            "is_static": is_static,
            "is_async": is_async,
            "parameters": parameters
        }
    
    def _extract_javascript_arrow_function_info(self, node: Node) -> Dict[str, Any]:
        """
        Extract JavaScript arrow function information.
        
        Args:
            node (Node): JavaScript arrow function node
            
        Returns:
            Dict[str, Any]: Extracted arrow function information
        """
        parameters = []
        is_async = False
        
        # Check if arrow function is async
        if node.text and b'async' in node.text:
            is_async = True
        
        for child in node.children:
            if child.type == 'formal_parameters':
                # Extract parameter names
                for param_child in child.children:
                    if param_child.type == 'identifier':
                        param_name = param_child.text.decode('utf-8') if param_child.text else None
                        if param_name:
                            parameters.append(param_name)
            elif child.type == 'identifier':
                # Single parameter without parentheses
                param_name = child.text.decode('utf-8') if child.text else None
                if param_name:
                    parameters.append(param_name)
        
        return {
            "type": "arrow_function",
            "line": node.start_point[0] + 1,
            "is_async": is_async,
            "parameters": parameters
        }
    
    def _extract_javascript_variable_info(self, node: Node) -> List[Dict[str, Any]]:
        """
        Extract JavaScript variable information from a variable declaration.
        
        Args:
            node (Node): JavaScript variable declaration node
            
        Returns:
            List[Dict[str, Any]]: List of extracted variable information
        """
        variables = []
        var_kind = None  # let, const, var
        
        for child in node.children:
            if child.type in ['let', 'const', 'var']:
                var_kind = child.text.decode('utf-8') if child.text else None
            elif child.type == 'variable_declarator':
                var_name = None
                has_initializer = False
                
                for declarator_child in child.children:
                    if declarator_child.type == 'identifier':
                        var_name = declarator_child.text.decode('utf-8') if declarator_child.text else None
                    elif declarator_child.type in ['assignment_expression', 'arrow_function', 'function_expression']:
                        has_initializer = True
                
                if var_name:
                    variables.append({
                        "name": var_name,
                        "line": child.start_point[0] + 1,
                        "kind": var_kind,
                        "has_initializer": has_initializer
                    })
        
        return variables
    
    def _extract_javascript_import_info(self, node: Node) -> Dict[str, Any]:
        """
        Extract JavaScript import information.
        
        Args:
            node (Node): JavaScript import statement node
            
        Returns:
            Dict[str, Any]: Extracted import information
        """
        import_source = None
        import_names = []
        default_import = None
        namespace_import = None
        
        for child in node.children:
            if child.type == 'string':
                # Import source (module path)
                import_source = child.text.decode('utf-8').strip('"\'') if child.text else None
            elif child.type == 'import_clause':
                for clause_child in child.children:
                    if clause_child.type == 'identifier':
                        # Default import
                        default_import = clause_child.text.decode('utf-8') if clause_child.text else None
                    elif clause_child.type == 'namespace_import':
                        # import * as name
                        for ns_child in clause_child.children:
                            if ns_child.type == 'identifier':
                                namespace_import = ns_child.text.decode('utf-8') if ns_child.text else None
                    elif clause_child.type == 'named_imports':
                        # import { name1, name2 }
                        for named_child in clause_child.children:
                            if named_child.type == 'import_specifier':
                                for spec_child in named_child.children:
                                    if spec_child.type == 'identifier':
                                        import_name = spec_child.text.decode('utf-8') if spec_child.text else None
                                        if import_name:
                                            import_names.append(import_name)
        
        return {
            "source": import_source,
            "line": node.start_point[0] + 1,
            "default_import": default_import,
            "namespace_import": namespace_import,
            "named_imports": import_names
        }
    
    def _extract_javascript_export_info(self, node: Node) -> Dict[str, Any]:
        """
        Extract JavaScript export information.
        
        Args:
            node (Node): JavaScript export statement node
            
        Returns:
            Dict[str, Any]: Extracted export information
        """
        export_type = "named"  # named, default, namespace
        export_names = []
        export_source = None
        
        if node.type == 'export_default_declaration':
            export_type = "default"
        
        for child in node.children:
            if child.type == 'string':
                # Re-export from another module
                export_source = child.text.decode('utf-8').strip('"\'') if child.text else None
            elif child.type == 'identifier':
                export_name = child.text.decode('utf-8') if child.text else None
                if export_name:
                    export_names.append(export_name)
            elif child.type == 'export_clause':
                # export { name1, name2 }
                for clause_child in child.children:
                    if clause_child.type == 'export_specifier':
                        for spec_child in clause_child.children:
                            if spec_child.type == 'identifier':
                                export_name = spec_child.text.decode('utf-8') if spec_child.text else None
                                if export_name:
                                    export_names.append(export_name)
        
        return {
            "type": export_type,
            "line": node.start_point[0] + 1,
            "names": export_names,
            "source": export_source
        }

    def _extract_dart_structure(self, ast_node: Node) -> Dict[str, Any]:
        """
        Extract structural information from Dart AST.
        
        Args:
            ast_node (Node): Root AST node
            
        Returns:
            Dict[str, Any]: Extracted structural information
        """
        structure = {
            "language": "dart",
            "imports": [],
            "exports": [],
            "classes": [],
            "functions": [],
            "methods": [],
            "variables": [],
            "widgets": [],  # Flutter-specific widgets
            "node_count": self._count_nodes(ast_node)
        }
        
        try:
            # Traverse AST to find structural elements
            self._traverse_dart_ast(ast_node, structure)
        except Exception as e:
            logger.error(f"Error traversing Dart AST: {str(e)}")
            structure["error"] = str(e)
        
        return structure
    
    def _traverse_dart_ast(self, node: Node, structure: Dict[str, Any]) -> None:
        """
        Recursively traverse Dart AST to extract structural elements.
        
        Args:
            node (Node): Current AST node
            structure (Dict[str, Any]): Structure dictionary to populate
        """
        if not hasattr(node, 'type') or not hasattr(node, 'children'):
            return
        
        try:
            # Handle different Dart node types
            if node.type == 'class_definition':
                class_info = self._extract_dart_class_info(node)
                if class_info:
                    structure["classes"].append(class_info)
                    # Check if it's a Flutter Widget
                    if self._is_flutter_widget(class_info):
                        structure["widgets"].append(class_info)
            
            elif node.type == 'function_signature':
                function_info = self._extract_dart_function_info(node)
                if function_info:
                    structure["functions"].append(function_info)
            
            elif node.type == 'method_signature':
                method_info = self._extract_dart_method_info(node)
                if method_info:
                    structure["methods"].append(method_info)
            
            elif node.type == 'import_specification':
                import_info = self._extract_dart_import_info(node)
                if import_info:
                    structure["imports"].append(import_info)
            
            elif node.type == 'export_specification':
                export_info = self._extract_dart_export_info(node)
                if export_info:
                    structure["exports"].append(export_info)
            
            elif node.type in ['initialized_variable_definition', 'declared_identifier']:
                var_info = self._extract_dart_variable_info(node)
                if var_info:
                    structure["variables"].extend(var_info)
            
            # Recursively process children
            for child in node.children:
                self._traverse_dart_ast(child, structure)
                
        except Exception as e:
            logger.debug(f"Error processing Dart node {node.type}: {str(e)}")
    
    def _extract_dart_class_info(self, node: Node) -> Optional[Dict[str, Any]]:
        """
        Extract information about a Dart class.
        
        Args:
            node (Node): Class definition node
            
        Returns:
            Optional[Dict[str, Any]]: Class information
        """
        try:
            class_name = None
            superclass = None
            mixins = []
            interfaces = []
            methods = []
            properties = []
            
            # Extract class name
            for child in node.children:
                if child.type == 'identifier':
                    class_name = self._get_node_text_safe(child)
                    break
            
            if not class_name:
                return None
            
            # Extract inheritance information
            for child in node.children:
                if child.type == 'superclass':
                    superclass = self._get_node_text_safe(child)
                elif child.type == 'mixins':
                    mixins = self._extract_dart_type_list(child)
                elif child.type == 'interfaces':
                    interfaces = self._extract_dart_type_list(child)
                elif child.type == 'class_body':
                    # Extract methods and properties from class body
                    methods, properties = self._extract_dart_class_members(child)
            
            return {
                'name': class_name,
                'line': node.start_point[0] + 1,
                'superclass': superclass,
                'mixins': mixins,
                'interfaces': interfaces,
                'methods': methods,
                'properties': properties,
                'is_abstract': self._is_abstract_class(node),
                'is_widget': self._is_flutter_widget_class(class_name, superclass)
            }
            
        except Exception as e:
            logger.debug(f"Error extracting Dart class info: {str(e)}")
            return None
    
    def _extract_dart_function_info(self, node: Node) -> Optional[Dict[str, Any]]:
        """
        Extract information about a Dart function.
        
        Args:
            node (Node): Function signature node
            
        Returns:
            Optional[Dict[str, Any]]: Function information
        """
        try:
            function_name = None
            return_type = None
            parameters = []
            is_async = False
            is_static = False
            
            # Extract function name
            for child in node.children:
                if child.type == 'identifier':
                    function_name = self._get_node_text_safe(child)
                    break
            
            if not function_name:
                return None
            
            # Extract function details
            for child in node.children:
                if child.type == 'type_annotation':
                    return_type = self._get_node_text_safe(child)
                elif child.type == 'formal_parameter_list':
                    parameters = self._extract_dart_parameters(child)
                elif child.type == 'async':
                    is_async = True
            
            # Check for static modifier in parent nodes
            parent = node.parent if hasattr(node, 'parent') else None
            if parent and 'static' in str(parent.text):
                is_static = True
            
            return {
                'name': function_name,
                'line': node.start_point[0] + 1,
                'return_type': return_type,
                'parameters': parameters,
                'is_async': is_async,
                'is_static': is_static
            }
            
        except Exception as e:
            logger.debug(f"Error extracting Dart function info: {str(e)}")
            return None
    
    def _extract_dart_method_info(self, node: Node) -> Optional[Dict[str, Any]]:
        """
        Extract information about a Dart method.
        
        Args:
            node (Node): Method signature node
            
        Returns:
            Optional[Dict[str, Any]]: Method information
        """
        try:
            method_name = None
            return_type = None
            parameters = []
            is_async = False
            is_static = False
            is_override = False
            access_modifier = 'public'
            
            # Extract method name
            for child in node.children:
                if child.type == 'identifier':
                    method_name = self._get_node_text_safe(child)
                    break
            
            if not method_name:
                return None
            
            # Determine access modifier based on naming convention
            if method_name.startswith('_'):
                access_modifier = 'private'
            
            # Extract method details
            for child in node.children:
                if child.type == 'type_annotation':
                    return_type = self._get_node_text_safe(child)
                elif child.type == 'formal_parameter_list':
                    parameters = self._extract_dart_parameters(child)
                elif child.type == 'async':
                    is_async = True
            
            # Check for modifiers in parent nodes
            parent = node.parent if hasattr(node, 'parent') else None
            if parent:
                parent_text = str(parent.text)
                if 'static' in parent_text:
                    is_static = True
                if '@override' in parent_text:
                    is_override = True
            
            return {
                'name': method_name,
                'line': node.start_point[0] + 1,
                'return_type': return_type,
                'parameters': parameters,
                'access_modifier': access_modifier,
                'is_async': is_async,
                'is_static': is_static,
                'is_override': is_override
            }
            
        except Exception as e:
            logger.debug(f"Error extracting Dart method info: {str(e)}")
            return None
    
    def _extract_dart_widget_info(self, node: Node) -> Optional[Dict[str, Any]]:
        """
        Extract information about a Flutter Widget.
        
        Args:
            node (Node): Widget class node
            
        Returns:
            Optional[Dict[str, Any]]: Widget information
        """
        class_info = self._extract_dart_class_info(node)
        if not class_info or not class_info.get('is_widget'):
            return None
        
        # Add Flutter-specific widget information
        widget_info = class_info.copy()
        widget_info.update({
            'widget_type': self._determine_widget_type(class_info),
            'has_build_method': self._has_build_method(class_info),
            'state_management': self._analyze_state_management(class_info)
        })
        
        return widget_info
    
    def _extract_dart_variable_info(self, node: Node) -> List[Dict[str, Any]]:
        """
        Extract information about Dart variable declarations.
        
        Args:
            node (Node): Variable declaration node
            
        Returns:
            List[Dict[str, Any]]: List of variable information
        """
        variables = []
        
        try:
            # Handle different variable declaration patterns
            if node.type == 'initialized_variable_definition':
                for child in node.children:
                    if child.type == 'declared_identifier':
                        var_info = self._extract_single_dart_variable(child)
                        if var_info:
                            variables.append(var_info)
            elif node.type == 'declared_identifier':
                var_info = self._extract_single_dart_variable(node)
                if var_info:
                    variables.append(var_info)
                    
        except Exception as e:
            logger.debug(f"Error extracting Dart variable info: {str(e)}")
        
        return variables
    
    def _extract_dart_import_info(self, node: Node) -> Optional[Dict[str, Any]]:
        """
        Extract information about a Dart import statement.
        
        Args:
            node (Node): Import specification node
            
        Returns:
            Optional[Dict[str, Any]]: Import information
        """
        try:
            import_uri = None
            import_prefix = None
            show_clauses = []
            hide_clauses = []
            
            # Extract import details
            for child in node.children:
                if child.type == 'configurable_uri':
                    import_uri = self._get_node_text_safe(child)
                elif child.type == 'import_prefix':
                    import_prefix = self._get_node_text_safe(child)
                elif child.type == 'show_clause':
                    show_clauses = self._extract_dart_identifier_list(child)
                elif child.type == 'hide_clause':
                    hide_clauses = self._extract_dart_identifier_list(child)
            
            if not import_uri:
                return None
            
            return {
                'type': 'import',
                'uri': import_uri,
                'prefix': import_prefix,
                'show': show_clauses,
                'hide': hide_clauses,
                'line': node.start_point[0] + 1,
                'is_flutter': 'flutter' in import_uri if import_uri else False
            }
            
        except Exception as e:
            logger.debug(f"Error extracting Dart import info: {str(e)}")
            return None
    
    def _extract_dart_export_info(self, node: Node) -> Optional[Dict[str, Any]]:
        """
        Extract information about a Dart export statement.
        
        Args:
            node (Node): Export specification node
            
        Returns:
            Optional[Dict[str, Any]]: Export information
        """
        try:
            export_uri = None
            show_clauses = []
            hide_clauses = []
            
            # Extract export details
            for child in node.children:
                if child.type == 'configurable_uri':
                    export_uri = self._get_node_text_safe(child)
                elif child.type == 'show_clause':
                    show_clauses = self._extract_dart_identifier_list(child)
                elif child.type == 'hide_clause':
                    hide_clauses = self._extract_dart_identifier_list(child)
            
            if not export_uri:
                return None
            
            return {
                'type': 'export',
                'uri': export_uri,
                'show': show_clauses,
                'hide': hide_clauses,
                'line': node.start_point[0] + 1
            }
            
        except Exception as e:
            logger.debug(f"Error extracting Dart export info: {str(e)}")
            return None
    
    # Helper methods for Dart analysis
    
    def _get_node_text_safe(self, node: Node) -> Optional[str]:
        """
        Safely get text content from a node.
        
        Args:
            node (Node): AST node
            
        Returns:
            Optional[str]: Text content or None
        """
        try:
            if hasattr(node, 'text') and node.text:
                return node.text.decode('utf-8')
        except Exception:
            pass
        return None
    
    def _extract_dart_parameters(self, node: Node) -> List[Dict[str, Any]]:
        """
        Extract parameter information from formal parameter list.
        
        Args:
            node (Node): Formal parameter list node
            
        Returns:
            List[Dict[str, Any]]: List of parameter information
        """
        parameters = []
        
        try:
            for child in node.children:
                if child.type in ['normal_formal_parameter', 'optional_formal_parameter', 'named_formal_parameter']:
                    param_info = self._extract_single_dart_parameter(child)
                    if param_info:
                        parameters.append(param_info)
        except Exception as e:
            logger.debug(f"Error extracting Dart parameters: {str(e)}")
        
        return parameters
    
    def _extract_single_dart_parameter(self, node: Node) -> Optional[Dict[str, Any]]:
        """
        Extract information about a single Dart parameter.
        
        Args:
            node (Node): Parameter node
            
        Returns:
            Optional[Dict[str, Any]]: Parameter information
        """
        try:
            param_name = None
            param_type = None
            is_optional = False
            is_named = False
            default_value = None
            
            # Determine parameter type
            if node.type == 'optional_formal_parameter':
                is_optional = True
            elif node.type == 'named_formal_parameter':
                is_named = True
            
            # Extract parameter details
            for child in node.children:
                if child.type == 'identifier':
                    param_name = self._get_node_text_safe(child)
                elif child.type == 'type_annotation':
                    param_type = self._get_node_text_safe(child)
                elif child.type == 'default_formal_parameter':
                    default_value = self._get_node_text_safe(child)
            
            if not param_name:
                return None
            
            return {
                'name': param_name,
                'type': param_type,
                'is_optional': is_optional,
                'is_named': is_named,
                'default_value': default_value
            }
            
        except Exception as e:
            logger.debug(f"Error extracting single Dart parameter: {str(e)}")
            return None
    
    def _extract_single_dart_variable(self, node: Node) -> Optional[Dict[str, Any]]:
        """
        Extract information about a single Dart variable.
        
        Args:
            node (Node): Variable declaration node
            
        Returns:
            Optional[Dict[str, Any]]: Variable information
        """
        try:
            var_name = None
            var_type = None
            is_final = False
            is_const = False
            is_static = False
            
            # Extract variable details
            for child in node.children:
                if child.type == 'identifier':
                    var_name = self._get_node_text_safe(child)
                elif child.type == 'type_annotation':
                    var_type = self._get_node_text_safe(child)
            
            # Check for modifiers in parent nodes
            parent = node.parent if hasattr(node, 'parent') else None
            if parent:
                parent_text = str(parent.text)
                if 'final' in parent_text:
                    is_final = True
                if 'const' in parent_text:
                    is_const = True
                if 'static' in parent_text:
                    is_static = True
            
            if not var_name:
                return None
            
            return {
                'name': var_name,
                'type': var_type,
                'line': node.start_point[0] + 1,
                'is_final': is_final,
                'is_const': is_const,
                'is_static': is_static
            }
            
        except Exception as e:
            logger.debug(f"Error extracting single Dart variable: {str(e)}")
            return None
    
    def _extract_dart_class_members(self, node: Node) -> tuple:
        """
        Extract methods and properties from a Dart class body.
        
        Args:
            node (Node): Class body node
            
        Returns:
            tuple: (methods, properties) lists
        """
        methods = []
        properties = []
        
        try:
            for child in node.children:
                if child.type == 'method_signature':
                    method_info = self._extract_dart_method_info(child)
                    if method_info:
                        methods.append(method_info)
                elif child.type in ['field_declaration', 'declared_identifier']:
                    prop_info = self._extract_single_dart_variable(child)
                    if prop_info:
                        properties.append(prop_info)
        except Exception as e:
            logger.debug(f"Error extracting Dart class members: {str(e)}")
        
        return methods, properties
    
    def _extract_dart_type_list(self, node: Node) -> List[str]:
        """
        Extract a list of type names from a node.
        
        Args:
            node (Node): Node containing type list
            
        Returns:
            List[str]: List of type names
        """
        types = []
        
        try:
            for child in node.children:
                if child.type == 'type':
                    type_name = self._get_node_text_safe(child)
                    if type_name:
                        types.append(type_name)
        except Exception as e:
            logger.debug(f"Error extracting Dart type list: {str(e)}")
        
        return types
    
    def _extract_dart_identifier_list(self, node: Node) -> List[str]:
        """
        Extract a list of identifiers from a node.
        
        Args:
            node (Node): Node containing identifier list
            
        Returns:
            List[str]: List of identifiers
        """
        identifiers = []
        
        try:
            for child in node.children:
                if child.type == 'identifier':
                    identifier = self._get_node_text_safe(child)
                    if identifier:
                        identifiers.append(identifier)
        except Exception as e:
            logger.debug(f"Error extracting Dart identifier list: {str(e)}")
        
        return identifiers
    
    def _is_abstract_class(self, node: Node) -> bool:
        """
        Check if a class is abstract.
        
        Args:
            node (Node): Class definition node
            
        Returns:
            bool: True if class is abstract
        """
        try:
            # Check for abstract modifier
            parent = node.parent if hasattr(node, 'parent') else None
            if parent and 'abstract' in str(parent.text):
                return True
        except Exception:
            pass
        return False
    
    def _is_flutter_widget(self, class_info: Dict[str, Any]) -> bool:
        """
        Check if a class is a Flutter widget.
        
        Args:
            class_info (Dict[str, Any]): Class information
            
        Returns:
            bool: True if class is a Flutter widget
        """
        return class_info.get('is_widget', False)
    
    def _is_flutter_widget_class(self, class_name: str, superclass: Optional[str]) -> bool:
        """
        Check if a class is a Flutter widget based on name and superclass.
        
        Args:
            class_name (str): Class name
            superclass (Optional[str]): Superclass name
            
        Returns:
            bool: True if class is a Flutter widget
        """
        if not superclass:
            return False
        
        flutter_widget_types = [
            'StatelessWidget', 'StatefulWidget', 'Widget',
            'InheritedWidget', 'RenderObjectWidget', 'ProxyWidget'
        ]
        
        return superclass in flutter_widget_types
    
    def _determine_widget_type(self, class_info: Dict[str, Any]) -> str:
        """
        Determine the type of Flutter widget.
        
        Args:
            class_info (Dict[str, Any]): Class information
            
        Returns:
            str: Widget type
        """
        superclass = class_info.get('superclass', '')
        
        if superclass == 'StatelessWidget':
            return 'stateless'
        elif superclass == 'StatefulWidget':
            return 'stateful'
        elif 'Widget' in superclass:
            return 'widget'
        else:
            return 'unknown'
    
    def _has_build_method(self, class_info: Dict[str, Any]) -> bool:
        """
        Check if a widget class has a build method.
        
        Args:
            class_info (Dict[str, Any]): Class information
            
        Returns:
            bool: True if class has build method
        """
        methods = class_info.get('methods', [])
        return any(method.get('name') == 'build' for method in methods)
    
    def _analyze_state_management(self, class_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze state management patterns in a widget.
        
        Args:
            class_info (Dict[str, Any]): Class information
            
        Returns:
            Dict[str, Any]: State management analysis
        """
        methods = class_info.get('methods', [])
        properties = class_info.get('properties', [])
        
        has_set_state = any(method.get('name') == 'setState' for method in methods)
        has_init_state = any(method.get('name') == 'initState' for method in methods)
        has_dispose = any(method.get('name') == 'dispose' for method in methods)
        
        state_variables = [prop for prop in properties if not prop.get('is_final', False)]
        
        return {
            'has_set_state': has_set_state,
            'has_init_state': has_init_state,
            'has_dispose': has_dispose,
            'state_variable_count': len(state_variables),
            'uses_state_management': has_set_state or has_init_state
        }