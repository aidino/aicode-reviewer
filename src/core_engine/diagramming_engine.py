"""
Diagramming Engine for AI Code Review System.

This module implements the DiagrammingEngine responsible for generating
visual diagrams (class diagrams, sequence diagrams) from code analysis.
Currently focuses on Python class diagrams using PlantUML/Mermaid.js syntax.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Union, Set, Tuple
from tree_sitter import Node

# Configure logging
logger = logging.getLogger(__name__)


class DiagrammingEngine:
    """
    Engine responsible for generating visual diagrams from code analysis.
    
    This engine processes AST data to extract structural information and
    generates diagram definitions in PlantUML or Mermaid.js format.
    """
    
    def __init__(self, diagram_format: str = 'plantuml'):
        """
        Initialize the DiagrammingEngine.
        
        Args:
            diagram_format (str): Format for diagram output ('plantuml' or 'mermaid')
        """
        self.diagram_format = diagram_format.lower()
        self.supported_formats = ['plantuml', 'mermaid']
        self.supported_languages = ['python', 'java', 'kotlin', 'xml', 'javascript', 'dart']
        self.max_sequence_depth = 3  # Maximum depth for sequence tracing
        self.max_calls_per_function = 10  # Maximum calls to trace per function
        
        if self.diagram_format not in self.supported_formats:
            raise ValueError(f"Unsupported diagram format: {diagram_format}. "
                           f"Supported formats: {self.supported_formats}")
        
        logger.info(f"DiagrammingEngine initialized with format: {diagram_format}")
    
    def _python_ast_to_class_data(self, ast_node: Node) -> List[Dict]:
        """
        Extract class structure data from Python AST node.
        
        Args:
            ast_node (Node): Tree-sitter AST node for Python code
            
        Returns:
            List[Dict]: List of dictionaries representing classes and relationships
        """
        try:
            classes = []
            relationships = []
            
            # Query for class definitions
            class_query = """
            (class_definition
                name: (identifier) @class_name
                superclasses: (argument_list)? @superclasses
                body: (block) @class_body
            ) @class_def
            """
            
            # Execute query to find classes
            query = ast_node.language.query(class_query)
            captures = query.captures(ast_node)
            
            # Group captures by class
            classes_data = {}
            for node, capture_name in captures:
                if capture_name == 'class_def':
                    class_name_node = None
                    superclasses_node = None
                    class_body_node = None
                    
                    # Get class components
                    for child in node.children:
                        if child.type == 'identifier':
                            class_name_node = child
                        elif child.type == 'argument_list':
                            superclasses_node = child
                        elif child.type == 'block':
                            class_body_node = child
                    
                    if class_name_node:
                        class_name = class_name_node.text.decode('utf-8')
                        classes_data[class_name] = {
                            'name': class_name,
                            'superclasses': [],
                            'attributes': [],
                            'methods': [],
                            'line': class_name_node.start_point[0] + 1
                        }
                        
                        # Extract superclasses
                        if superclasses_node:
                            for child in superclasses_node.children:
                                if child.type == 'identifier':
                                    superclass = child.text.decode('utf-8')
                                    classes_data[class_name]['superclasses'].append(superclass)
                                    
                                    # Add inheritance relationship
                                    relationships.append({
                                        'type': 'inheritance',
                                        'from': class_name,
                                        'to': superclass
                                    })
                        
                        # Extract methods and attributes from class body
                        if class_body_node:
                            self._extract_class_members(class_body_node, classes_data[class_name])
            
            # Convert to list format
            for class_data in classes_data.values():
                classes.append({
                    'type': 'class',
                    'name': class_data['name'],
                    'attributes': class_data['attributes'],
                    'methods': class_data['methods'],
                    'superclasses': class_data['superclasses'],
                    'line': class_data['line']
                })
            
            # Add relationships
            for relationship in relationships:
                classes.append(relationship)
            
            logger.info(f"Extracted {len([c for c in classes if c.get('type') == 'class'])} classes "
                       f"and {len([c for c in classes if c.get('type') != 'class'])} relationships")
            
            return classes
            
        except Exception as e:
            logger.error(f"Error extracting class data from AST: {str(e)}")
            return []
    
    def _extract_class_members(self, class_body: Node, class_data: Dict) -> None:
        """
        Extract methods and attributes from class body.
        
        Args:
            class_body (Node): AST node representing class body
            class_data (Dict): Dictionary to store extracted data
        """
        try:
            # Query for function definitions (methods)
            method_query = """
            (function_definition
                name: (identifier) @method_name
                parameters: (parameters) @method_params
            ) @method_def
            """
            
            # Query for assignment statements (attributes)
            attribute_query = """
            (assignment
                left: (identifier) @attr_name
                right: (_) @attr_value
            ) @assignment
            """
            
            query = class_body.language.query(method_query)
            method_captures = query.captures(class_body)
            
            # Extract methods
            for node, capture_name in method_captures:
                if capture_name == 'method_def':
                    method_name_node = None
                    method_params_node = None
                    
                    for child in node.children:
                        if child.type == 'identifier':
                            method_name_node = child
                            break
                    
                    for child in node.children:
                        if child.type == 'parameters':
                            method_params_node = child
                            break
                    
                    if method_name_node:
                        method_name = method_name_node.text.decode('utf-8')
                        
                        # Determine access modifier
                        access_modifier = 'public'
                        if method_name.startswith('__') and not method_name.endswith('__'):
                            access_modifier = 'private'
                        elif method_name.startswith('_'):
                            access_modifier = 'protected'
                        
                        # Extract parameters
                        params = []
                        if method_params_node:
                            for param_node in method_params_node.children:
                                if param_node.type == 'identifier':
                                    param_name = param_node.text.decode('utf-8')
                                    if param_name != 'self':  # Skip 'self' parameter
                                        params.append(param_name)
                        
                        class_data['methods'].append({
                            'name': method_name,
                            'access_modifier': access_modifier,
                            'parameters': params,
                            'return_type': 'Any'  # Could be enhanced with type analysis
                        })
            
            # Extract attributes (simplified - looks for assignments in class body)
            query = class_body.language.query(attribute_query)
            attr_captures = query.captures(class_body)
            
            for node, capture_name in attr_captures:
                if capture_name == 'assignment':
                    attr_name_node = None
                    
                    for child in node.children:
                        if child.type == 'identifier':
                            attr_name_node = child
                            break
                    
                    if attr_name_node:
                        attr_name = attr_name_node.text.decode('utf-8')
                        
                        # Determine access modifier
                        access_modifier = 'public'
                        if attr_name.startswith('__'):
                            access_modifier = 'private'
                        elif attr_name.startswith('_'):
                            access_modifier = 'protected'
                        
                        class_data['attributes'].append({
                            'name': attr_name,
                            'access_modifier': access_modifier,
                            'type': 'Any'  # Could be enhanced with type analysis
                        })
                        
        except Exception as e:
            logger.error(f"Error extracting class members: {str(e)}")
    
    def generate_class_diagram(self, code_files: Dict[str, Any], language: str, 
                             changes: Optional[Dict] = None) -> str:
        """
        Generate class diagram from code files.
        
        Args:
            code_files (Dict[str, Any]): Dictionary mapping file paths to AST data
            language (str): Programming language ('python')
            changes (Optional[Dict]): Changes to highlight in diagram
            
        Returns:
            str: PlantUML or Mermaid.js diagram definition
        """
        if language.lower() not in self.supported_languages:
            raise ValueError(f"Unsupported language: {language}. "
                           f"Supported languages: {self.supported_languages}")
        
        try:
            all_class_data = []
            
            # Extract class data from all files
            for file_path, ast_data in code_files.items():
                if ast_data and hasattr(ast_data, 'root_node'):
                    logger.info(f"Processing file: {file_path}")
                    
                    # Choose appropriate extraction method based on language
                    if language.lower() == 'python':
                        class_data = self._python_ast_to_class_data(ast_data.root_node)
                    elif language.lower() == 'java':
                        class_data = self._java_ast_to_class_data(ast_data.root_node)
                    elif language.lower() == 'kotlin':
                        class_data = self._kotlin_ast_to_class_data(ast_data.root_node)
                    elif language.lower() == 'xml':
                        class_data = self._xml_ast_to_class_data(ast_data.root_node)
                    elif language.lower() == 'javascript':
                        class_data = self._javascript_ast_to_class_data(ast_data.root_node)
                    elif language.lower() == 'dart':
                        class_data = self._dart_ast_to_class_data(ast_data.root_node)
                    else:
                        logger.warning(f"Unsupported language for class extraction: {language}")
                        continue
                    
                    # Add file path to each class for context
                    for item in class_data:
                        if item.get('type') == 'class':
                            item['file_path'] = file_path
                    
                    all_class_data.extend(class_data)
            
            # Generate diagram based on format
            if self.diagram_format == 'plantuml':
                return self._generate_plantuml_diagram(all_class_data, changes)
            elif self.diagram_format == 'mermaid':
                return self._generate_mermaid_diagram(all_class_data, changes)
            else:
                raise ValueError(f"Unsupported diagram format: {self.diagram_format}")
                
        except Exception as e:
            logger.error(f"Error generating class diagram: {str(e)}")
            return f"@startuml\nnote as N1\nError generating diagram: {str(e)}\nend note\n@enduml"
    
    def _generate_plantuml_diagram(self, class_data: List[Dict], 
                                 changes: Optional[Dict] = None) -> str:
        """
        Generate PlantUML class diagram.
        
        Args:
            class_data (List[Dict]): List of class and relationship data
            changes (Optional[Dict]): Changes to highlight
            
        Returns:
            str: PlantUML diagram definition
        """
        diagram = ["@startuml", ""]
        
        # Add title
        diagram.append("title Class Diagram")
        diagram.append("")
        
        # Add styling for changes if provided
        changed_classes = set()
        if changes:
            changed_classes = set(changes.get('modified_classes', []))
            if changed_classes:
                diagram.append("' Styling for changed classes")
                for class_name in changed_classes:
                    diagram.append(f"class {class_name} #lightblue")
                diagram.append("")
        
        # Add classes
        classes = [item for item in class_data if item.get('type') == 'class']
        for class_info in classes:
            class_name = class_info['name']
            
            # Start class definition
            diagram.append(f"class {class_name} {{")
            
            # Add attributes
            for attr in class_info.get('attributes', []):
                access_symbol = self._get_plantuml_access_symbol(attr['access_modifier'])
                diagram.append(f"  {access_symbol}{attr['name']}: {attr['type']}")
            
            if class_info.get('attributes') and class_info.get('methods'):
                diagram.append("  --")  # Separator between attributes and methods
            
            # Add methods
            for method in class_info.get('methods', []):
                access_symbol = self._get_plantuml_access_symbol(method['access_modifier'])
                params = ", ".join(method['parameters']) if method['parameters'] else ""
                diagram.append(f"  {access_symbol}{method['name']}({params}): {method['return_type']}")
            
            diagram.append("}")
            diagram.append("")
        
        # Add relationships
        relationships = [item for item in class_data if item.get('type') != 'class']
        for rel in relationships:
            if rel.get('type') == 'inheritance':
                diagram.append(f"{rel['to']} <|-- {rel['from']}")
        
        diagram.append("")
        diagram.append("@enduml")
        
        return "\n".join(diagram)
    
    def _generate_mermaid_diagram(self, class_data: List[Dict], 
                                changes: Optional[Dict] = None) -> str:
        """
        Generate Mermaid.js class diagram.
        
        Args:
            class_data (List[Dict]): List of class and relationship data
            changes (Optional[Dict]): Changes to highlight
            
        Returns:
            str: Mermaid.js diagram definition
        """
        diagram = ["classDiagram"]
        
        # Add classes
        classes = [item for item in class_data if item.get('type') == 'class']
        for class_info in classes:
            class_name = class_info['name']
            
            # Add class declaration
            diagram.append(f"  class {class_name} {{")
            
            # Add attributes
            for attr in class_info.get('attributes', []):
                access_symbol = self._get_mermaid_access_symbol(attr['access_modifier'])
                diagram.append(f"    {access_symbol}{attr['type']} {attr['name']}")
            
            # Add methods
            for method in class_info.get('methods', []):
                access_symbol = self._get_mermaid_access_symbol(method['access_modifier'])
                params = ", ".join(method['parameters']) if method['parameters'] else ""
                diagram.append(f"    {access_symbol}{method['name']}({params}) {method['return_type']}")
            
            diagram.append("  }")
        
        # Add relationships
        relationships = [item for item in class_data if item.get('type') != 'class']
        for rel in relationships:
            if rel.get('type') == 'inheritance':
                diagram.append(f"  {rel['to']} <|-- {rel['from']}")
        
        # Add styling for changes if provided
        changed_classes = set()
        if changes:
            changed_classes = set(changes.get('modified_classes', []))
            if changed_classes:
                diagram.append("")
                diagram.append("  %% Styling for changed classes")
                for class_name in changed_classes:
                    diagram.append(f"  class {class_name} {class_name}Style")
                    diagram.append(f"  classDef {class_name}Style fill:#lightblue")
        
        return "\n".join(diagram)
    
    def _get_plantuml_access_symbol(self, access_modifier: str) -> str:
        """Get PlantUML access symbol."""
        symbols = {
            'public': '+',
            'protected': '#',
            'private': '-'
        }
        return symbols.get(access_modifier, '+')
    
    def _get_mermaid_access_symbol(self, access_modifier: str) -> str:
        """Get Mermaid.js access symbol."""
        symbols = {
            'public': '+',
            'protected': '#',
            'private': '-'
        }
        return symbols.get(access_modifier, '+')
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported diagram formats.
        
        Returns:
            List[str]: List of supported formats
        """
        return self.supported_formats.copy()
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported programming languages.
        
        Returns:
            List[str]: List of supported languages
        """
        return self.supported_languages.copy()
    
    def set_diagram_format(self, diagram_format: str) -> None:
        """
        Set the diagram output format.
        
        Args:
            diagram_format (str): Format for diagram output
            
        Raises:
            ValueError: If format is not supported
        """
        if diagram_format.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported diagram format: {diagram_format}. "
                           f"Supported formats: {self.supported_formats}")
        
        self.diagram_format = diagram_format.lower()
        logger.info(f"Diagram format set to: {diagram_format}")
    
    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get information about the diagramming engine.
        
        Returns:
            Dict[str, Any]: Engine information
        """
        return {
            'engine_name': 'DiagrammingEngine',
            'version': '1.4.0',  # Updated for Dart/Flutter support
            'current_format': self.diagram_format,
            'supported_formats': self.supported_formats,
            'supported_languages': self.supported_languages,
            'max_sequence_depth': self.max_sequence_depth,
            'max_calls_per_function': self.max_calls_per_function,
            'capabilities': [
                'class_diagrams',
                'sequence_diagrams',
                'inheritance_relationships',
                'function_call_tracing',
                'pr_change_focus',
                'change_highlighting',
                'plantuml_output',
                'mermaid_output',
                'kotlin_support',
                'android_xml_support',
                'javascript_support',
                'dart_support',
                'flutter_support'
            ]
        }
    
    def _python_ast_to_sequence_data(self, ast_node: Node, pr_changes: Optional[Dict] = None, 
                                   rag_agent: Optional[Any] = None) -> List[Dict]:
        """
        Extract sequence data from Python AST focusing on PR changes.
        
        Args:
            ast_node (Node): Tree-sitter AST node for Python code
            pr_changes (Optional[Dict]): Information about PR changes (modified/added functions)
            rag_agent (Optional[Any]): RAG agent for resolving external calls
            
        Returns:
            List[Dict]: List of sequence interactions and participants
        """
        try:
            interactions = []
            participants = set()
            
            # If no PR changes specified, analyze all functions
            if not pr_changes:
                pr_changes = {'modified_functions': [], 'added_functions': []}
            
            # Find all function definitions first
            all_functions = self._extract_python_functions(ast_node)
            
            # Identify entry points from PR changes
            entry_functions = []
            for func_name in pr_changes.get('modified_functions', []) + pr_changes.get('added_functions', []):
                matching_funcs = [f for f in all_functions if f['name'] == func_name]
                entry_functions.extend(matching_funcs)
            
            # If no specific changes, use first few functions as entry points
            if not entry_functions:
                entry_functions = all_functions[:3]  # Limit to first 3 functions
            
            # Trace call graphs from entry points
            for entry_func in entry_functions:
                logger.info(f"Tracing sequence from function: {entry_func['name']}")
                
                # Add entry function as participant
                participants.add(entry_func['name'])
                
                # Trace calls from this function
                call_chain = self._trace_python_function_calls(
                    entry_func, all_functions, depth=0, visited=set()
                )
                
                interactions.extend(call_chain)
                
                # Add all called functions as participants
                for interaction in call_chain:
                    participants.add(interaction['caller'])
                    participants.add(interaction['callee'])
            
            # Build sequence data structure
            sequence_data = {
                'participants': list(participants),
                'interactions': interactions,
                'entry_points': [f['name'] for f in entry_functions],
                'language': 'python'
            }
            
            logger.info(f"Extracted sequence data: {len(participants)} participants, "
                       f"{len(interactions)} interactions")
            
            return [sequence_data]
            
        except Exception as e:
            logger.error(f"Error extracting Python sequence data: {str(e)}")
            return []
    
    def _java_ast_to_sequence_data(self, ast_node: Node, pr_changes: Optional[Dict] = None,
                                 rag_agent: Optional[Any] = None) -> List[Dict]:
        """
        Extract sequence data from Java AST focusing on PR changes.
        
        Args:
            ast_node (Node): Tree-sitter AST node for Java code
            pr_changes (Optional[Dict]): Information about PR changes (modified/added methods)
            rag_agent (Optional[Any]): RAG agent for resolving external calls
            
        Returns:
            List[Dict]: List of sequence interactions and participants
        """
        try:
            interactions = []
            participants = set()
            
            # If no PR changes specified, analyze all methods
            if not pr_changes:
                pr_changes = {'modified_methods': [], 'added_methods': []}
            
            # Find all method definitions
            all_methods = self._extract_java_methods(ast_node)
            
            # Identify entry points from PR changes
            entry_methods = []
            for method_name in pr_changes.get('modified_methods', []) + pr_changes.get('added_methods', []):
                matching_methods = [m for m in all_methods if m['name'] == method_name]
                entry_methods.extend(matching_methods)
            
            # If no specific changes, use first few methods as entry points
            if not entry_methods:
                entry_methods = all_methods[:3]  # Limit to first 3 methods
            
            # Trace call graphs from entry points
            for entry_method in entry_methods:
                logger.info(f"Tracing sequence from method: {entry_method['class']}.{entry_method['name']}")
                
                # Add entry method as participant (class.method format)
                participant = f"{entry_method['class']}.{entry_method['name']}"
                participants.add(participant)
                
                # Trace calls from this method
                call_chain = self._trace_java_method_calls(
                    entry_method, all_methods, depth=0, visited=set()
                )
                
                interactions.extend(call_chain)
                
                # Add all called methods as participants
                for interaction in call_chain:
                    participants.add(interaction['caller'])
                    participants.add(interaction['callee'])
            
            # Build sequence data structure
            sequence_data = {
                'participants': list(participants),
                'interactions': interactions,
                'entry_points': [f"{m['class']}.{m['name']}" for m in entry_methods],
                'language': 'java'
            }
            
            logger.info(f"Extracted Java sequence data: {len(participants)} participants, "
                       f"{len(interactions)} interactions")
            
            return [sequence_data]
            
        except Exception as e:
            logger.error(f"Error extracting Java sequence data: {str(e)}")
            return []
    
    def _extract_python_functions(self, ast_node: Node) -> List[Dict]:
        """
        Extract all function definitions from Python AST.
        
        Args:
            ast_node (Node): Tree-sitter AST node
            
        Returns:
            List[Dict]: List of function information
        """
        functions = []
        
        try:
            # Query for function definitions
            function_query = """
            (function_definition
                name: (identifier) @func_name
                body: (block) @func_body
            ) @func_def
            """
            
            query = ast_node.language.query(function_query)
            captures = query.captures(ast_node)
            
            # Group captures by function
            current_func = None
            for node, capture_name in captures:
                if capture_name == 'func_def':
                    current_func = {
                        'node': node,
                        'name': None,
                        'body': None,
                        'line': node.start_point[0] + 1
                    }
                elif capture_name == 'func_name' and current_func:
                    current_func['name'] = node.text.decode('utf-8')
                elif capture_name == 'func_body' and current_func:
                    current_func['body'] = node
                    
                    # Only add if we have both name and body
                    if current_func['name'] and current_func['body']:
                        functions.append(current_func)
                    current_func = None
            
            logger.info(f"Extracted {len(functions)} Python functions")
            return functions
            
        except Exception as e:
            logger.error(f"Error extracting Python functions: {str(e)}")
            return []
    
    def _extract_java_methods(self, ast_node: Node) -> List[Dict]:
        """
        Extract all method definitions from Java AST.
        
        Args:
            ast_node (Node): Tree-sitter AST node
            
        Returns:
            List[Dict]: List of method information
        """
        methods = []
        
        try:
            # Query for method definitions within classes
            method_query = """
            (class_declaration
                name: (identifier) @class_name
                body: (class_body
                    (method_declaration
                        name: (identifier) @method_name
                        body: (block) @method_body
                    ) @method_def
                )
            ) @class_def
            """
            
            query = ast_node.language.query(method_query)
            captures = query.captures(ast_node)
            
            # Process captures to build method list
            current_class = None
            current_method = None
            
            for node, capture_name in captures:
                if capture_name == 'class_name':
                    current_class = node.text.decode('utf-8')
                elif capture_name == 'method_def':
                    current_method = {
                        'node': node,
                        'class': current_class,
                        'name': None,
                        'body': None,
                        'line': node.start_point[0] + 1
                    }
                elif capture_name == 'method_name' and current_method:
                    current_method['name'] = node.text.decode('utf-8')
                elif capture_name == 'method_body' and current_method:
                    current_method['body'] = node
                    
                    # Only add if we have all required info
                    if current_method['name'] and current_method['body'] and current_method['class']:
                        methods.append(current_method)
                    current_method = None
            
            logger.info(f"Extracted {len(methods)} Java methods")
            return methods
            
        except Exception as e:
            logger.error(f"Error extracting Java methods: {str(e)}")
            return []
    
    def _trace_python_function_calls(self, function: Dict, all_functions: List[Dict], 
                                   depth: int, visited: Set[str]) -> List[Dict]:
        """
        Trace function calls from a Python function.
        
        Args:
            function (Dict): Function to trace calls from
            all_functions (List[Dict]): All available functions for resolution
            depth (int): Current recursion depth
            visited (Set[str]): Set of already visited functions (prevent cycles)
            
        Returns:
            List[Dict]: List of call interactions
        """
        interactions = []
        
        if depth >= self.max_sequence_depth or function['name'] in visited:
            return interactions
        
        visited.add(function['name'])
        
        try:
            # Query for function calls in the function body
            call_query = """
            (call
                function: (identifier) @called_func
            ) @call_expr
            """
            
            query = function['body'].language.query(call_query)
            captures = query.captures(function['body'])
            
            call_count = 0
            for node, capture_name in captures:
                if capture_name == 'called_func' and call_count < self.max_calls_per_function:
                    called_func_name = node.text.decode('utf-8')
                    
                    # Skip built-in functions and common library calls
                    if not self._is_builtin_or_library_function(called_func_name):
                        interactions.append({
                            'caller': function['name'],
                            'callee': called_func_name,
                            'type': 'function_call',
                            'line': node.start_point[0] + 1
                        })
                        
                        call_count += 1
                        
                        # Recursively trace the called function if it exists
                        called_function = next((f for f in all_functions if f['name'] == called_func_name), None)
                        if called_function and called_func_name not in visited:
                            nested_calls = self._trace_python_function_calls(
                                called_function, all_functions, depth + 1, visited.copy()
                            )
                            interactions.extend(nested_calls)
            
        except Exception as e:
            logger.error(f"Error tracing calls from {function['name']}: {str(e)}")
        
        return interactions
    
    def _trace_java_method_calls(self, method: Dict, all_methods: List[Dict],
                               depth: int, visited: Set[str]) -> List[Dict]:
        """
        Trace method calls from a Java method.
        
        Args:
            method (Dict): Method to trace calls from
            all_methods (List[Dict]): All available methods for resolution
            depth (int): Current recursion depth
            visited (Set[str]): Set of already visited methods (prevent cycles)
            
        Returns:
            List[Dict]: List of call interactions
        """
        interactions = []
        method_signature = f"{method['class']}.{method['name']}"
        
        if depth >= self.max_sequence_depth or method_signature in visited:
            return interactions
        
        visited.add(method_signature)
        
        try:
            # Query for method invocations in the method body
            call_query = """
            (method_invocation
                name: (identifier) @called_method
            ) @method_call
            """
            
            query = method['body'].language.query(call_query)
            captures = query.captures(method['body'])
            
            call_count = 0
            for node, capture_name in captures:
                if capture_name == 'called_method' and call_count < self.max_calls_per_function:
                    called_method_name = node.text.decode('utf-8')
                    
                    # Skip built-in methods and common library calls
                    if not self._is_builtin_or_library_function(called_method_name):
                        # Try to resolve to a known method in the same class first
                        called_method_full = f"{method['class']}.{called_method_name}"
                        
                        interactions.append({
                            'caller': method_signature,
                            'callee': called_method_full,
                            'type': 'method_call',
                            'line': node.start_point[0] + 1
                        })
                        
                        call_count += 1
                        
                        # Recursively trace the called method if it exists
                        called_method_obj = next((m for m in all_methods 
                                                if f"{m['class']}.{m['name']}" == called_method_full), None)
                        if called_method_obj and called_method_full not in visited:
                            nested_calls = self._trace_java_method_calls(
                                called_method_obj, all_methods, depth + 1, visited.copy()
                            )
                            interactions.extend(nested_calls)
            
        except Exception as e:
            logger.error(f"Error tracing calls from {method_signature}: {str(e)}")
        
        return interactions
    
    def _is_builtin_or_library_function(self, function_name: str) -> bool:
        """
        Check if a function/method name is a built-in or common library function.
        
        Args:
            function_name (str): Function name to check
            
        Returns:
            bool: True if it's a built-in/library function
        """
        # Python built-ins and common library functions
        python_builtins = {
            'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
            'range', 'enumerate', 'zip', 'map', 'filter', 'sum', 'max', 'min',
            'abs', 'round', 'open', 'isinstance', 'hasattr', 'getattr', 'setattr',
            'append', 'extend', 'insert', 'remove', 'pop', 'clear', 'index', 'count',
            'sort', 'reverse', 'copy', 'deepcopy', 'join', 'split', 'strip', 'replace'
        }
        
        # Java built-ins and common library methods
        java_builtins = {
            'println', 'print', 'toString', 'equals', 'hashCode', 'clone',
            'size', 'isEmpty', 'contains', 'add', 'remove', 'clear', 'get',
            'put', 'keySet', 'values', 'entrySet', 'substring', 'charAt',
            'length', 'toLowerCase', 'toUpperCase', 'trim', 'split', 'replace'
        }
        
        return function_name in python_builtins or function_name in java_builtins
    
    def generate_sequence_diagram(self, code_files: Dict[str, Any], language: str,
                                pr_changes: Optional[Dict] = None, rag_agent: Optional[Any] = None) -> str:
        """
        Generate sequence diagram from code files focusing on PR changes.
        
        Args:
            code_files (Dict[str, Any]): Dictionary mapping file paths to AST data
            language (str): Programming language ('python' or 'java')
            pr_changes (Optional[Dict]): Information about PR changes
            rag_agent (Optional[Any]): RAG agent for resolving external calls
            
        Returns:
            str: PlantUML or Mermaid.js sequence diagram definition
        """
        if language.lower() not in self.supported_languages:
            raise ValueError(f"Unsupported language for sequence diagrams: {language}. "
                           f"Supported languages: {self.supported_languages}")
        
        try:
            all_sequence_data = []
            
            # Extract sequence data from all files
            for file_path, ast_data in code_files.items():
                if ast_data and hasattr(ast_data, 'root_node'):
                    logger.info(f"Processing sequence data from file: {file_path}")
                    
                    if language.lower() == 'python':
                        sequence_data = self._python_ast_to_sequence_data(
                            ast_data.root_node, pr_changes, rag_agent
                        )
                    elif language.lower() == 'java':
                        sequence_data = self._java_ast_to_sequence_data(
                            ast_data.root_node, pr_changes, rag_agent
                        )
                    elif language.lower() == 'kotlin':
                        sequence_data = self._kotlin_ast_to_sequence_data(
                            ast_data.root_node, pr_changes, rag_agent
                        )
                    elif language.lower() == 'javascript':
                        sequence_data = self._javascript_ast_to_sequence_data(
                            ast_data.root_node, pr_changes, rag_agent
                        )
                    elif language.lower() == 'dart':
                        sequence_data = self._dart_ast_to_sequence_data(
                            ast_data.root_node, pr_changes, rag_agent
                        )
                    else:
                        logger.warning(f"Sequence diagrams not supported for language: {language}")
                        continue
                    
                    all_sequence_data.extend(sequence_data)
            
            # Merge all sequence data
            merged_sequence_data = self._merge_sequence_data(all_sequence_data)
            
            # Generate diagram based on format
            if self.diagram_format == 'plantuml':
                return self._generate_plantuml_sequence_diagram(merged_sequence_data)
            elif self.diagram_format == 'mermaid':
                return self._generate_mermaid_sequence_diagram(merged_sequence_data)
            else:
                raise ValueError(f"Unsupported diagram format: {self.diagram_format}")
                
        except Exception as e:
            logger.error(f"Error generating sequence diagram: {str(e)}")
            return f"@startuml\nnote as N1\nError generating sequence diagram: {str(e)}\nend note\n@enduml"
    
    def _merge_sequence_data(self, sequence_data_list: List[Dict]) -> Dict:
        """
        Merge multiple sequence data structures into one.
        
        Args:
            sequence_data_list (List[Dict]): List of sequence data structures
            
        Returns:
            Dict: Merged sequence data
        """
        merged = {
            'participants': set(),
            'interactions': [],
            'entry_points': [],
            'language': 'unknown'
        }
        
        for seq_data in sequence_data_list:
            merged['participants'].update(seq_data.get('participants', []))
            merged['interactions'].extend(seq_data.get('interactions', []))
            merged['entry_points'].extend(seq_data.get('entry_points', []))
            
            if seq_data.get('language') != 'unknown':
                merged['language'] = seq_data['language']
        
        # Convert participants back to list and remove duplicates from interactions
        merged['participants'] = list(merged['participants'])
        
        # Remove duplicate interactions
        seen_interactions = set()
        unique_interactions = []
        for interaction in merged['interactions']:
            key = (interaction['caller'], interaction['callee'], interaction['type'])
            if key not in seen_interactions:
                seen_interactions.add(key)
                unique_interactions.append(interaction)
        
        merged['interactions'] = unique_interactions
        
        return merged
    
    def _generate_plantuml_sequence_diagram(self, sequence_data: Dict) -> str:
        """
        Generate PlantUML sequence diagram.
        
        Args:
            sequence_data (Dict): Merged sequence data
            
        Returns:
            str: PlantUML sequence diagram definition
        """
        diagram = ["@startuml", ""]
        
        # Add title
        language = sequence_data.get('language', 'Code')
        diagram.append(f"title {language.title()} Sequence Diagram - PR Changes Focus")
        diagram.append("")
        
        # Add participants
        participants = sequence_data.get('participants', [])
        if participants:
            diagram.append("' Participants")
            for participant in sorted(participants):
                # Clean participant name for PlantUML
                clean_name = participant.replace('.', '_').replace('-', '_')
                diagram.append(f"participant \"{participant}\" as {clean_name}")
            diagram.append("")
        
        # Add interactions
        interactions = sequence_data.get('interactions', [])
        if interactions:
            diagram.append("' Interactions")
            
            # Group interactions by entry point if possible
            entry_points = sequence_data.get('entry_points', [])
            for entry_point in entry_points:
                diagram.append(f"note over {entry_point.replace('.', '_').replace('-', '_')}")
                diagram.append(f"  Entry point: {entry_point}")
                diagram.append("end note")
                diagram.append("")
            
            # Add all interactions
            for interaction in interactions:
                caller = interaction['caller'].replace('.', '_').replace('-', '_')
                callee = interaction['callee'].replace('.', '_').replace('-', '_')
                
                # Determine arrow type based on interaction type
                if interaction.get('type') == 'method_call':
                    arrow = "->>"
                else:
                    arrow = "->"
                
                diagram.append(f"{caller} {arrow} {callee}: {interaction.get('type', 'call')}")
        else:
            diagram.append("note as N1")
            diagram.append("  No function/method calls found")
            diagram.append("  or calls are to built-in functions only")
            diagram.append("end note")
        
        diagram.append("")
        diagram.append("@enduml")
        
        return "\n".join(diagram)
    
    def _generate_mermaid_sequence_diagram(self, sequence_data: Dict) -> str:
        """
        Generate Mermaid.js sequence diagram.
        
        Args:
            sequence_data (Dict): Merged sequence data
            
        Returns:
            str: Mermaid.js sequence diagram definition
        """
        diagram = ["sequenceDiagram"]
        
        # Add title
        language = sequence_data.get('language', 'Code')
        diagram.append(f"    title {language.title()} Sequence Diagram - PR Changes Focus")
        diagram.append("")
        
        # Add participants
        participants = sequence_data.get('participants', [])
        if participants:
            for participant in sorted(participants):
                # Clean participant name for Mermaid
                clean_name = participant.replace('.', '_').replace('-', '_')
                diagram.append(f"    participant {clean_name} as {participant}")
        
        # Add interactions
        interactions = sequence_data.get('interactions', [])
        if interactions:
            diagram.append("")
            
            # Add entry point notes
            entry_points = sequence_data.get('entry_points', [])
            for entry_point in entry_points:
                clean_name = entry_point.replace('.', '_').replace('-', '_')
                diagram.append(f"    note over {clean_name}: Entry point")
            
            if entry_points:
                diagram.append("")
            
            # Add all interactions
            for interaction in interactions:
                caller = interaction['caller'].replace('.', '_').replace('-', '_')
                callee = interaction['callee'].replace('.', '_').replace('-', '_')
                
                # Determine arrow type based on interaction type
                if interaction.get('type') == 'method_call':
                    arrow = "->>"
                else:
                    arrow = "->"
                
                diagram.append(f"    {caller} {arrow} {callee}: {interaction.get('type', 'call')}")
        else:
            diagram.append("")
            diagram.append("    note over participants: No function/method calls found")
        
        return "\n".join(diagram)

    def _java_ast_to_class_data(self, ast_node: Node) -> List[Dict]:
        """
        Extract class structure data from Java AST node.
        
        Args:
            ast_node (Node): Tree-sitter AST node for Java code
            
        Returns:
            List[Dict]: List of dictionaries representing classes and relationships
        """
        try:
            classes = []
            relationships = []
            
            # Find class declarations
            def traverse_java_classes(node: Node):
                if node.type == 'class_declaration':
                    class_info = self._extract_java_class_data(node)
                    if class_info:
                        classes.append(class_info)
                
                # Recursively traverse children
                if hasattr(node, 'children') and node.children:
                    for child in node.children:
                        traverse_java_classes(child)
            
            traverse_java_classes(ast_node)
            
            logger.info(f"Extracted {len(classes)} Java classes")
            return classes
            
        except Exception as e:
            logger.error(f"Error extracting Java class data from AST: {str(e)}")
            return []
    
    def _extract_java_class_data(self, node: Node) -> Optional[Dict]:
        """
        Extract Java class information from a class declaration node.
        
        Args:
            node (Node): Java class declaration node
            
        Returns:
            Optional[Dict]: Extracted class information
        """
        try:
            class_name = None
            superclasses = []
            methods = []
            attributes = []
            
            # Get class name
            for child in node.children:
                if child.type == 'identifier':
                    class_name = child.text.decode('utf-8')
                    break
            
            if not class_name:
                return None
            
            # Extract class body
            for child in node.children:
                if child.type == 'class_body':
                    methods, attributes = self._extract_java_class_members(child)
                    break
            
            return {
                'type': 'class',
                'name': class_name,
                'attributes': attributes,
                'methods': methods,
                'superclasses': superclasses,
                'line': node.start_point[0] + 1
            }
            
        except Exception as e:
            logger.error(f"Error extracting Java class data: {str(e)}")
            return None
    
    def _extract_java_class_members(self, class_body: Node) -> Tuple[List[Dict], List[Dict]]:
        """
        Extract methods and attributes from Java class body.
        
        Args:
            class_body (Node): Java class body node
            
        Returns:
            Tuple[List[Dict], List[Dict]]: (methods, attributes)
        """
        methods = []
        attributes = []
        
        try:
            for child in class_body.children:
                if child.type == 'method_declaration':
                    method_info = self._extract_java_method_data(child)
                    if method_info:
                        methods.append(method_info)
                elif child.type == 'field_declaration':
                    field_info = self._extract_java_field_data(child)
                    if field_info:
                        attributes.append(field_info)
            
        except Exception as e:
            logger.error(f"Error extracting Java class members: {str(e)}")
        
        return methods, attributes
    
    def _extract_java_method_data(self, node: Node) -> Optional[Dict]:
        """
        Extract Java method information.
        
        Args:
            node (Node): Java method declaration node
            
        Returns:
            Optional[Dict]: Method information
        """
        try:
            method_name = None
            parameters = []
            return_type = "void"
            access_modifier = "public"
            
            # Extract method components
            for child in node.children:
                if child.type == 'identifier':
                    method_name = child.text.decode('utf-8')
                elif child.type == 'formal_parameters':
                    parameters = self._extract_java_parameters(child)
                elif child.type == 'type_identifier':
                    return_type = child.text.decode('utf-8')
                elif child.type in ['public', 'private', 'protected']:
                    access_modifier = child.type
            
            if method_name:
                return {
                    'name': method_name,
                    'parameters': parameters,
                    'return_type': return_type,
                    'access_modifier': access_modifier
                }
            
        except Exception as e:
            logger.error(f"Error extracting Java method data: {str(e)}")
        
        return None
    
    def _extract_java_field_data(self, node: Node) -> Optional[Dict]:
        """
        Extract Java field information.
        
        Args:
            node (Node): Java field declaration node
            
        Returns:
            Optional[Dict]: Field information
        """
        try:
            field_name = None
            field_type = "Object"
            access_modifier = "private"
            
            # Extract field components
            for child in node.children:
                if child.type == 'variable_declarator':
                    for var_child in child.children:
                        if var_child.type == 'identifier':
                            field_name = var_child.text.decode('utf-8')
                            break
                elif child.type == 'type_identifier':
                    field_type = child.text.decode('utf-8')
                elif child.type in ['public', 'private', 'protected']:
                    access_modifier = child.type
            
            if field_name:
                return {
                    'name': field_name,
                    'type': field_type,
                    'access_modifier': access_modifier
                }
            
        except Exception as e:
            logger.error(f"Error extracting Java field data: {str(e)}")
        
        return None
    
    def _extract_java_parameters(self, node: Node) -> List[str]:
        """
        Extract Java method parameters.
        
        Args:
            node (Node): Java formal parameters node
            
        Returns:
            List[str]: List of parameter names
        """
        parameters = []
        
        try:
            for child in node.children:
                if child.type == 'formal_parameter':
                    for param_child in child.children:
                        if param_child.type == 'identifier':
                            parameters.append(param_child.text.decode('utf-8'))
                            break
        except Exception as e:
            logger.error(f"Error extracting Java parameters: {str(e)}")
        
        return parameters
    
    def _kotlin_ast_to_class_data(self, ast_node: Node) -> List[Dict]:
        """
        Extract class structure data from Kotlin AST node.
        
        Args:
            ast_node (Node): Tree-sitter AST node for Kotlin code
            
        Returns:
            List[Dict]: List of dictionaries representing classes and relationships
        """
        try:
            classes = []
            relationships = []
            
            # Find class, object, interface, and data class declarations
            def traverse_kotlin_classes(node: Node):
                if node.type in ['class_declaration', 'object_declaration', 'interface_declaration']:
                    class_info = self._extract_kotlin_class_data(node)
                    if class_info:
                        classes.append(class_info)
                
                # Recursively traverse children
                if hasattr(node, 'children') and node.children:
                    for child in node.children:
                        traverse_kotlin_classes(child)
            
            traverse_kotlin_classes(ast_node)
            
            logger.info(f"Extracted {len(classes)} Kotlin classes/objects/interfaces")
            return classes
            
        except Exception as e:
            logger.error(f"Error extracting Kotlin class data from AST: {str(e)}")
            return []
    
    def _extract_kotlin_class_data(self, node: Node) -> Optional[Dict]:
        """
        Extract Kotlin class/object/interface information.
        
        Args:
            node (Node): Kotlin class/object/interface declaration node
            
        Returns:
            Optional[Dict]: Extracted class information
        """
        try:
            class_name = None
            class_type = "class"
            methods = []
            attributes = []
            
            # Determine class type
            if node.type == 'object_declaration':
                class_type = "object"
            elif node.type == 'interface_declaration':
                class_type = "interface"
            
            # Get class name
            for child in node.children:
                if child.type in ['type_identifier', 'simple_identifier']:
                    class_name = child.text.decode('utf-8')
                    break
            
            if not class_name:
                return None
            
            # Extract class body
            for child in node.children:
                if child.type == 'class_body':
                    methods, attributes = self._extract_kotlin_class_members(child)
                    break
            
            return {
                'type': 'class',
                'name': class_name,
                'class_type': class_type,
                'attributes': attributes,
                'methods': methods,
                'superclasses': [],
                'line': node.start_point[0] + 1
            }
            
        except Exception as e:
            logger.error(f"Error extracting Kotlin class data: {str(e)}")
            return None
    
    def _extract_kotlin_class_members(self, class_body: Node) -> Tuple[List[Dict], List[Dict]]:
        """
        Extract methods and properties from Kotlin class body.
        
        Args:
            class_body (Node): Kotlin class body node
            
        Returns:
            Tuple[List[Dict], List[Dict]]: (methods, properties)
        """
        methods = []
        properties = []
        
        try:
            for child in class_body.children:
                if child.type == 'function_declaration':
                    method_info = self._extract_kotlin_function_data(child)
                    if method_info:
                        methods.append(method_info)
                elif child.type == 'property_declaration':
                    prop_info = self._extract_kotlin_property_data(child)
                    if prop_info:
                        properties.append(prop_info)
            
        except Exception as e:
            logger.error(f"Error extracting Kotlin class members: {str(e)}")
        
        return methods, properties
    
    def _extract_kotlin_function_data(self, node: Node) -> Optional[Dict]:
        """
        Extract Kotlin function information.
        
        Args:
            node (Node): Kotlin function declaration node
            
        Returns:
            Optional[Dict]: Function information
        """
        try:
            function_name = None
            parameters = []
            return_type = "Unit"
            access_modifier = "public"
            
            # Extract function components
            for child in node.children:
                if child.type == 'simple_identifier':
                    function_name = child.text.decode('utf-8')
                elif child.type == 'function_value_parameters':
                    parameters = self._extract_kotlin_parameters(child)
                elif child.type == 'type_identifier':
                    return_type = child.text.decode('utf-8')
                elif child.type in ['public', 'private', 'protected', 'internal']:
                    access_modifier = child.type
            
            if function_name:
                return {
                    'name': function_name,
                    'parameters': parameters,
                    'return_type': return_type,
                    'access_modifier': access_modifier
                }
            
        except Exception as e:
            logger.error(f"Error extracting Kotlin function data: {str(e)}")
        
        return None
    
    def _extract_kotlin_property_data(self, node: Node) -> Optional[Dict]:
        """
        Extract Kotlin property information.
        
        Args:
            node (Node): Kotlin property declaration node
            
        Returns:
            Optional[Dict]: Property information
        """
        try:
            property_name = None
            property_type = "Any"
            access_modifier = "public"
            
            # Extract property components
            for child in node.children:
                if child.type == 'simple_identifier':
                    property_name = child.text.decode('utf-8')
                elif child.type == 'type_identifier':
                    property_type = child.text.decode('utf-8')
                elif child.type in ['public', 'private', 'protected', 'internal']:
                    access_modifier = child.type
            
            if property_name:
                return {
                    'name': property_name,
                    'type': property_type,
                    'access_modifier': access_modifier
                }
            
        except Exception as e:
            logger.error(f"Error extracting Kotlin property data: {str(e)}")
        
        return None
    
    def _extract_kotlin_parameters(self, node: Node) -> List[str]:
        """
        Extract Kotlin function parameters.
        
        Args:
            node (Node): Kotlin function value parameters node
            
        Returns:
            List[str]: List of parameter names
        """
        parameters = []
        
        try:
            for child in node.children:
                if child.type == 'parameter':
                    for param_child in child.children:
                        if param_child.type == 'simple_identifier':
                            parameters.append(param_child.text.decode('utf-8'))
                            break
        except Exception as e:
            logger.error(f"Error extracting Kotlin parameters: {str(e)}")
        
        return parameters
    
    def _xml_ast_to_class_data(self, ast_node: Node) -> List[Dict]:
        """
        Extract structural data from XML AST node (Android layouts, manifests).
        
        Args:
            ast_node (Node): Tree-sitter AST node for XML code
            
        Returns:
            List[Dict]: List of dictionaries representing XML structure as diagram elements
        """
        try:
            elements = []
            
            # Find XML elements and represent them as diagram components
            def traverse_xml_elements(node: Node, depth: int = 0):
                if node.type == 'element':
                    element_info = self._extract_xml_element_data(node, depth)
                    if element_info:
                        elements.append(element_info)
                
                # Recursively traverse children
                if hasattr(node, 'children') and node.children:
                    for child in node.children:
                        traverse_xml_elements(child, depth + 1)
            
            traverse_xml_elements(ast_node)
            
            logger.info(f"Extracted {len(elements)} XML elements for diagram")
            return elements
            
        except Exception as e:
            logger.error(f"Error extracting XML structure data from AST: {str(e)}")
            return []
    
    def _extract_xml_element_data(self, node: Node, depth: int) -> Optional[Dict]:
        """
        Extract XML element information for diagram representation.
        
        Args:
            node (Node): XML element node
            depth (int): Nesting depth
            
        Returns:
            Optional[Dict]: Element information formatted for diagram
        """
        try:
            element_name = None
            attributes = []
            
            # Extract element name and attributes
            for child in node.children:
                if child.type == 'start_tag':
                    for tag_child in child.children:
                        if tag_child.type == 'name':
                            element_name = tag_child.text.decode('utf-8')
                        elif tag_child.type == 'attribute':
                            attr_info = self._extract_xml_attribute_data(tag_child)
                            if attr_info:
                                attributes.append(attr_info)
            
            if element_name:
                # Represent XML element as a "class" for diagram purposes
                return {
                    'type': 'class',
                    'name': f"{element_name}_{depth}",  # Add depth to avoid name conflicts
                    'xml_element': element_name,
                    'attributes': [{'name': attr['name'], 'type': attr['value'], 'access_modifier': 'public'} 
                                 for attr in attributes if attr.get('name') and attr.get('value')],
                    'methods': [],
                    'superclasses': [],
                    'line': node.start_point[0] + 1,
                    'depth': depth
                }
            
        except Exception as e:
            logger.error(f"Error extracting XML element data: {str(e)}")
        
        return None
    
    def _extract_xml_attribute_data(self, node: Node) -> Optional[Dict]:
        """
        Extract XML attribute information.
        
        Args:
            node (Node): XML attribute node
            
        Returns:
            Optional[Dict]: Attribute information
        """
        try:
            attr_name = None
            attr_value = None
            
            for child in node.children:
                if child.type == 'attribute_name':
                    attr_name = child.text.decode('utf-8')
                elif child.type == 'quoted_attribute_value':
                    attr_value = child.text.decode('utf-8').strip('"\'')
            
            if attr_name and attr_value:
                return {
                    'name': attr_name,
                    'value': attr_value
                }
            
        except Exception as e:
            logger.error(f"Error extracting XML attribute data: {str(e)}")
        
        return None
    
    def _kotlin_ast_to_sequence_data(self, ast_node: Node, pr_changes: Optional[Dict] = None,
                                   rag_agent: Optional[Any] = None) -> List[Dict]:
        """
        Extract sequence data from Kotlin AST focusing on PR changes.
        
        Args:
            ast_node (Node): Tree-sitter AST node for Kotlin code
            pr_changes (Optional[Dict]): Information about PR changes (modified/added functions)
            rag_agent (Optional[Any]): RAG agent for resolving external calls
            
        Returns:
            List[Dict]: List of sequence interactions and participants
        """
        try:
            interactions = []
            participants = set()
            
            # If no PR changes specified, analyze all functions
            if not pr_changes:
                pr_changes = {'modified_functions': [], 'added_functions': []}
            
            # Find all function definitions
            all_functions = self._extract_kotlin_functions(ast_node)
            
            # Identify entry points from PR changes
            entry_functions = []
            for func_name in pr_changes.get('modified_functions', []) + pr_changes.get('added_functions', []):
                matching_funcs = [f for f in all_functions if f['name'] == func_name]
                entry_functions.extend(matching_funcs)
            
            # If no specific changes, use first few functions as entry points
            if not entry_functions:
                entry_functions = all_functions[:3]  # Limit to first 3 functions
            
            # Trace call graphs from entry points
            for entry_func in entry_functions:
                logger.info(f"Tracing sequence from Kotlin function: {entry_func['name']}")
                
                # Add entry function as participant
                if entry_func.get('class'):
                    participant = f"{entry_func['class']}.{entry_func['name']}"
                else:
                    participant = entry_func['name']
                participants.add(participant)
                
                # Trace calls from this function
                call_chain = self._trace_kotlin_function_calls(
                    entry_func, all_functions, depth=0, visited=set()
                )
                
                interactions.extend(call_chain)
                
                # Add all called functions as participants
                for interaction in call_chain:
                    participants.add(interaction['caller'])
                    participants.add(interaction['callee'])
            
            # Build sequence data structure
            sequence_data = {
                'participants': list(participants),
                'interactions': interactions,
                'entry_points': [f['name'] for f in entry_functions],
                'language': 'kotlin'
            }
            
            logger.info(f"Extracted Kotlin sequence data: {len(participants)} participants, "
                       f"{len(interactions)} interactions")
            
            return [sequence_data]
            
        except Exception as e:
            logger.error(f"Error extracting Kotlin sequence data: {str(e)}")
            return []
    
    def _extract_kotlin_functions(self, ast_node: Node) -> List[Dict]:
        """
        Extract all function definitions from Kotlin AST.
        
        Args:
            ast_node (Node): Tree-sitter AST node
            
        Returns:
            List[Dict]: List of function information
        """
        functions = []
        
        try:
            # Find all function declarations
            def traverse_kotlin_functions(node: Node, class_name: Optional[str] = None):
                if node.type == 'function_declaration':
                    func_info = self._extract_kotlin_function_for_sequence(node, class_name)
                    if func_info:
                        functions.append(func_info)
                elif node.type in ['class_declaration', 'object_declaration']:
                    # Extract class name
                    current_class = None
                    for child in node.children:
                        if child.type in ['type_identifier', 'simple_identifier']:
                            current_class = child.text.decode('utf-8')
                            break
                    
                    # Continue traversing with class context
                    if hasattr(node, 'children') and node.children:
                        for child in node.children:
                            traverse_kotlin_functions(child, current_class)
                else:
                    # Continue traversing
                    if hasattr(node, 'children') and node.children:
                        for child in node.children:
                            traverse_kotlin_functions(child, class_name)
            
            traverse_kotlin_functions(ast_node)
            
            logger.info(f"Found {len(functions)} Kotlin functions for sequence analysis")
            return functions
            
        except Exception as e:
            logger.error(f"Error extracting Kotlin functions: {str(e)}")
            return []
    
    def _extract_kotlin_function_for_sequence(self, node: Node, class_name: Optional[str] = None) -> Optional[Dict]:
        """
        Extract Kotlin function information for sequence analysis.
        
        Args:
            node (Node): Kotlin function declaration node
            class_name (Optional[str]): Name of containing class if any
            
        Returns:
            Optional[Dict]: Function information
        """
        try:
            function_name = None
            function_body = None
            
            # Extract function name and body
            for child in node.children:
                if child.type == 'simple_identifier':
                    function_name = child.text.decode('utf-8')
                elif child.type == 'function_body':
                    function_body = child
            
            if function_name:
                return {
                    'name': function_name,
                    'class': class_name,
                    'body_node': function_body,
                    'line': node.start_point[0] + 1
                }
            
        except Exception as e:
            logger.error(f"Error extracting Kotlin function for sequence: {str(e)}")
        
        return None
    
    def _trace_kotlin_function_calls(self, function: Dict, all_functions: List[Dict],
                                   depth: int, visited: Set[str]) -> List[Dict]:
        """
        Trace function calls within a Kotlin function body.
        
        Args:
            function (Dict): Function information with body_node
            all_functions (List[Dict]): All available functions
            depth (int): Current tracing depth
            visited (Set[str]): Set of visited function names to prevent infinite recursion
            
        Returns:
            List[Dict]: List of interaction dictionaries
        """
        interactions = []
        
        # Limit depth to prevent infinite recursion
        if depth >= self.max_sequence_depth:
            return interactions
        
        # Limit calls per function
        call_count = 0
        max_calls = self.max_calls_per_function
        
        try:
            body_node = function.get('body_node')
            if not body_node:
                return interactions
            
            caller_name = function['name']
            if function.get('class'):
                caller_name = f"{function['class']}.{function['name']}"
            
            # Avoid revisiting the same function
            if caller_name in visited:
                return interactions
            
            visited.add(caller_name)
            
            # Find function calls in the body
            def find_kotlin_calls(node: Node):
                nonlocal call_count
                if call_count >= max_calls:
                    return
                
                if node.type == 'call_expression':
                    callee_name = self._extract_kotlin_call_target(node)
                    if callee_name and not self._is_builtin_or_library_function(callee_name):
                        # Find the called function
                        called_function = None
                        for func in all_functions:
                            if func['name'] == callee_name:
                                called_function = func
                                break
                        
                        if called_function:
                            callee_full_name = callee_name
                            if called_function.get('class'):
                                callee_full_name = f"{called_function['class']}.{callee_name}"
                            
                            interactions.append({
                                'caller': caller_name,
                                'callee': callee_full_name,
                                'type': 'function_call'
                            })
                            
                            call_count += 1
                            
                            # Recursively trace the called function
                            if callee_full_name not in visited:
                                sub_interactions = self._trace_kotlin_function_calls(
                                    called_function, all_functions, depth + 1, visited.copy()
                                )
                                interactions.extend(sub_interactions)
                
                # Continue traversing child nodes
                if hasattr(node, 'children') and node.children:
                    for child in node.children:
                        find_kotlin_calls(child)
            
            find_kotlin_calls(body_node)
            
        except Exception as e:
            logger.error(f"Error tracing Kotlin function calls: {str(e)}")
        finally:
            visited.discard(caller_name)
        
        return interactions
    
    def _extract_kotlin_call_target(self, node: Node) -> Optional[str]:
        """
        Extract the target function name from a Kotlin call expression.
        
        Args:
            node (Node): Call expression node
            
        Returns:
            Optional[str]: Function name being called
        """
        try:
            # Look for identifier or navigation expression
            for child in node.children:
                if child.type == 'simple_identifier':
                    return child.text.decode('utf-8')
                elif child.type == 'navigation_expression':
                    # Handle method calls like object.method()
                    for nav_child in child.children:
                        if nav_child.type == 'simple_identifier':
                            # Return the last identifier (method name)
                            return nav_child.text.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error extracting Kotlin call target: {str(e)}")
        
        return None

    def _javascript_ast_to_class_data(self, ast_node: Node) -> List[Dict]:
        """
        Extract class structure data from JavaScript AST node.
        
        Args:
            ast_node (Node): Tree-sitter AST node for JavaScript code
            
        Returns:
            List[Dict]: List of dictionaries representing classes and relationships
        """
        try:
            classes = []
            relationships = []
            
            # Find all class declarations
            def traverse_javascript_classes(node: Node):
                if node.type == 'class_declaration':
                    class_info = self._extract_javascript_class_data(node)
                    if class_info:
                        classes.append(class_info)
                        
                        # Extract inheritance relationships
                        if class_info.get('superclass'):
                            relationships.append({
                                'type': 'inheritance',
                                'from': class_info['name'],
                                'to': class_info['superclass']
                            })
                
                # Continue traversing
                if hasattr(node, 'children') and node.children:
                    for child in node.children:
                        traverse_javascript_classes(child)
            
            traverse_javascript_classes(ast_node)
            
            logger.info(f"Extracted {len([c for c in classes if c.get('type') == 'class'])} JavaScript classes "
                       f"and {len([c for c in classes if c.get('type') != 'class'])} relationships")
            
            return classes
            
        except Exception as e:
            logger.error(f"Error extracting JavaScript class data from AST: {str(e)}")
            return []
    
    def _extract_javascript_class_data(self, node: Node) -> Optional[Dict]:
        """
        Extract JavaScript class information from class declaration node.
        
        Args:
            node (Node): JavaScript class declaration node
            
        Returns:
            Optional[Dict]: Class information
        """
        try:
            class_name = None
            superclass = None
            class_body = None
            
            # Extract class components
            for child in node.children:
                if child.type == 'identifier':
                    class_name = child.text.decode('utf-8')
                elif child.type == 'class_heritage':
                    # Extract superclass from extends clause
                    for heritage_child in child.children:
                        if heritage_child.type == 'identifier':
                            superclass = heritage_child.text.decode('utf-8')
                elif child.type == 'class_body':
                    class_body = child
            
            if class_name and class_body:
                # Extract methods and properties
                methods, properties = self._extract_javascript_class_members(class_body)
                
                return {
                    'type': 'class',
                    'name': class_name,
                    'attributes': properties,
                    'methods': methods,
                    'superclass': superclass,
                    'line': node.start_point[0] + 1
                }
            
        except Exception as e:
            logger.error(f"Error extracting JavaScript class data: {str(e)}")
        
        return None
    
    def _extract_javascript_class_members(self, class_body: Node) -> Tuple[List[Dict], List[Dict]]:
        """
        Extract methods and properties from JavaScript class body.
        
        Args:
            class_body (Node): JavaScript class body node
            
        Returns:
            Tuple[List[Dict], List[Dict]]: (methods, properties)
        """
        methods = []
        properties = []
        
        try:
            for child in class_body.children:
                if child.type == 'method_definition':
                    method_info = self._extract_javascript_method_data(child)
                    if method_info:
                        methods.append(method_info)
                elif child.type == 'field_definition':
                    property_info = self._extract_javascript_property_data(child)
                    if property_info:
                        properties.append(property_info)
                elif child.type == 'public_field_definition':
                    property_info = self._extract_javascript_property_data(child)
                    if property_info:
                        properties.append(property_info)
            
        except Exception as e:
            logger.error(f"Error extracting JavaScript class members: {str(e)}")
        
        return methods, properties
    
    def _extract_javascript_method_data(self, node: Node) -> Optional[Dict]:
        """
        Extract JavaScript method information from method definition node.
        
        Args:
            node (Node): JavaScript method definition node
            
        Returns:
            Optional[Dict]: Method information
        """
        try:
            method_name = None
            is_static = False
            is_async = False
            access_modifier = 'public'  # JavaScript default
            parameters = []
            
            # Check for modifiers
            for child in node.children:
                if child.type == 'static':
                    is_static = True
                elif child.type == 'async':
                    is_async = True
                elif child.type == 'property_identifier':
                    method_name = child.text.decode('utf-8')
                elif child.type == 'formal_parameters':
                    parameters = self._extract_javascript_parameters(child)
            
            if method_name:
                # Determine access modifier based on naming convention
                if method_name.startswith('_'):
                    access_modifier = 'private'
                elif method_name.startswith('#'):
                    access_modifier = 'private'  # Private fields in modern JS
                
                method_signature = f"{method_name}({', '.join(parameters)})"
                if is_async:
                    method_signature = f"async {method_signature}"
                if is_static:
                    method_signature = f"static {method_signature}"
                
                return {
                    'name': method_name,
                    'signature': method_signature,
                    'access_modifier': access_modifier,
                    'is_static': is_static,
                    'is_async': is_async,
                    'parameters': parameters,
                    'line': node.start_point[0] + 1
                }
            
        except Exception as e:
            logger.error(f"Error extracting JavaScript method data: {str(e)}")
        
        return None
    
    def _extract_javascript_property_data(self, node: Node) -> Optional[Dict]:
        """
        Extract JavaScript property information from field definition node.
        
        Args:
            node (Node): JavaScript field definition node
            
        Returns:
            Optional[Dict]: Property information
        """
        try:
            property_name = None
            is_static = False
            access_modifier = 'public'
            
            # Extract property information
            for child in node.children:
                if child.type == 'static':
                    is_static = True
                elif child.type == 'property_identifier':
                    property_name = child.text.decode('utf-8')
            
            if property_name:
                # Determine access modifier based on naming convention
                if property_name.startswith('_'):
                    access_modifier = 'private'
                elif property_name.startswith('#'):
                    access_modifier = 'private'  # Private fields in modern JS
                
                return {
                    'name': property_name,
                    'access_modifier': access_modifier,
                    'is_static': is_static,
                    'line': node.start_point[0] + 1
                }
            
        except Exception as e:
            logger.error(f"Error extracting JavaScript property data: {str(e)}")
        
        return None
    
    def _extract_javascript_parameters(self, node: Node) -> List[str]:
        """
        Extract parameter names from JavaScript formal parameters node.
        
        Args:
            node (Node): JavaScript formal parameters node
            
        Returns:
            List[str]: List of parameter names
        """
        parameters = []
        
        try:
            for child in node.children:
                if child.type == 'identifier':
                    parameters.append(child.text.decode('utf-8'))
                elif child.type == 'assignment_pattern':
                    # Handle default parameters
                    for param_child in child.children:
                        if param_child.type == 'identifier':
                            param_name = param_child.text.decode('utf-8')
                            parameters.append(f"{param_name} = default")
                            break
                elif child.type == 'rest_pattern':
                    # Handle rest parameters (...args)
                    for param_child in child.children:
                        if param_child.type == 'identifier':
                            param_name = param_child.text.decode('utf-8')
                            parameters.append(f"...{param_name}")
                            break
            
        except Exception as e:
            logger.error(f"Error extracting JavaScript parameters: {str(e)}")
        
        return parameters
    
    def _javascript_ast_to_sequence_data(self, ast_node: Node, pr_changes: Optional[Dict] = None,
                                       rag_agent: Optional[Any] = None) -> List[Dict]:
        """
        Extract sequence diagram data from JavaScript AST node.
        
        Args:
            ast_node (Node): Tree-sitter AST node for JavaScript code
            pr_changes (Optional[Dict]): PR changes information
            rag_agent (Optional[Any]): RAG agent for context
            
        Returns:
            List[Dict]: List of interaction dictionaries for sequence diagram
        """
        try:
            # Extract all functions from the AST
            all_functions = self._extract_javascript_functions(ast_node)
            
            if not all_functions:
                logger.warning("No JavaScript functions found for sequence analysis")
                return []
            
            # Generate interactions for each function
            all_interactions = []
            
            for function in all_functions:
                # Skip if this function is not in PR changes (if specified)
                if pr_changes and not self._is_function_in_changes(function, pr_changes):
                    continue
                
                # Trace function calls
                interactions = self._trace_javascript_function_calls(
                    function, all_functions, depth=0, visited=set()
                )
                all_interactions.extend(interactions)
            
            logger.info(f"Generated {len(all_interactions)} JavaScript interactions for sequence diagram")
            return all_interactions
            
        except Exception as e:
            logger.error(f"Error extracting JavaScript sequence data: {str(e)}")
            return []
    
    def _extract_javascript_functions(self, ast_node: Node) -> List[Dict]:
        """
        Extract all function definitions from JavaScript AST.
        
        Args:
            ast_node (Node): Tree-sitter AST node
            
        Returns:
            List[Dict]: List of function information
        """
        functions = []
        
        try:
            # Find all function declarations and expressions
            def traverse_javascript_functions(node: Node, class_name: Optional[str] = None):
                if node.type in ['function_declaration', 'function_expression', 'arrow_function']:
                    func_info = self._extract_javascript_function_for_sequence(node, class_name)
                    if func_info:
                        functions.append(func_info)
                elif node.type == 'method_definition':
                    # Handle class methods
                    func_info = self._extract_javascript_function_for_sequence(node, class_name)
                    if func_info:
                        functions.append(func_info)
                elif node.type == 'class_declaration':
                    # Extract class name and continue traversing
                    current_class = None
                    for child in node.children:
                        if child.type == 'identifier':
                            current_class = child.text.decode('utf-8')
                            break
                    
                    # Continue traversing with class context
                    if hasattr(node, 'children') and node.children:
                        for child in node.children:
                            traverse_javascript_functions(child, current_class)
                else:
                    # Continue traversing
                    if hasattr(node, 'children') and node.children:
                        for child in node.children:
                            traverse_javascript_functions(child, class_name)
            
            traverse_javascript_functions(ast_node)
            
            logger.info(f"Found {len(functions)} JavaScript functions for sequence analysis")
            return functions
            
        except Exception as e:
            logger.error(f"Error extracting JavaScript functions: {str(e)}")
            return []
    
    def _extract_javascript_function_for_sequence(self, node: Node, class_name: Optional[str] = None) -> Optional[Dict]:
        """
        Extract JavaScript function information for sequence analysis.
        
        Args:
            node (Node): JavaScript function node
            class_name (Optional[str]): Name of containing class if any
            
        Returns:
            Optional[Dict]: Function information
        """
        try:
            function_name = None
            function_body = None
            
            # Extract function name and body based on node type
            if node.type == 'function_declaration':
                for child in node.children:
                    if child.type == 'identifier':
                        function_name = child.text.decode('utf-8')
                    elif child.type == 'statement_block':
                        function_body = child
            elif node.type == 'method_definition':
                for child in node.children:
                    if child.type == 'property_identifier':
                        function_name = child.text.decode('utf-8')
                    elif child.type == 'statement_block':
                        function_body = child
            elif node.type in ['function_expression', 'arrow_function']:
                # For anonymous functions, try to get name from context
                function_name = 'anonymous'
                for child in node.children:
                    if child.type == 'statement_block':
                        function_body = child
                    elif child.type == 'expression_statement':
                        function_body = child
            
            if function_name:
                return {
                    'name': function_name,
                    'class': class_name,
                    'body_node': function_body,
                    'line': node.start_point[0] + 1
                }
            
        except Exception as e:
            logger.error(f"Error extracting JavaScript function for sequence: {str(e)}")
        
        return None
    
    def _trace_javascript_function_calls(self, function: Dict, all_functions: List[Dict],
                                       depth: int, visited: Set[str]) -> List[Dict]:
        """
        Trace function calls within a JavaScript function body.
        
        Args:
            function (Dict): Function information with body_node
            all_functions (List[Dict]): All available functions
            depth (int): Current tracing depth
            visited (Set[str]): Set of visited function names to prevent infinite recursion
            
        Returns:
            List[Dict]: List of interaction dictionaries
        """
        interactions = []
        
        # Limit depth to prevent infinite recursion
        if depth >= self.max_sequence_depth:
            return interactions
        
        # Limit calls per function
        call_count = 0
        max_calls = self.max_calls_per_function
        
        try:
            body_node = function.get('body_node')
            if not body_node:
                return interactions
            
            caller_name = function['name']
            if function.get('class'):
                caller_name = f"{function['class']}.{function['name']}"
            
            # Avoid revisiting the same function
            if caller_name in visited:
                return interactions
            
            visited.add(caller_name)
            
            # Find function calls in the body
            def find_javascript_calls(node: Node):
                nonlocal call_count
                if call_count >= max_calls:
                    return
                
                if node.type == 'call_expression':
                    callee_name = self._extract_javascript_call_target(node)
                    if callee_name and not self._is_builtin_or_library_function(callee_name):
                        # Find the called function
                        called_function = None
                        for func in all_functions:
                            if func['name'] == callee_name:
                                called_function = func
                                break
                        
                        if called_function:
                            callee_full_name = callee_name
                            if called_function.get('class'):
                                callee_full_name = f"{called_function['class']}.{callee_name}"
                            
                            interactions.append({
                                'caller': caller_name,
                                'callee': callee_full_name,
                                'type': 'function_call'
                            })
                            
                            call_count += 1
                            
                            # Recursively trace the called function
                            if callee_full_name not in visited:
                                sub_interactions = self._trace_javascript_function_calls(
                                    called_function, all_functions, depth + 1, visited.copy()
                                )
                                interactions.extend(sub_interactions)
                
                # Continue traversing child nodes
                if hasattr(node, 'children') and node.children:
                    for child in node.children:
                        find_javascript_calls(child)
            
            find_javascript_calls(body_node)
            
        except Exception as e:
            logger.error(f"Error tracing JavaScript function calls: {str(e)}")
        finally:
            visited.discard(caller_name)
        
        return interactions
    
    def _extract_javascript_call_target(self, node: Node) -> Optional[str]:
        """
        Extract the target function name from a JavaScript call expression.
        
        Args:
            node (Node): Call expression node
            
        Returns:
            Optional[str]: Function name being called
        """
        try:
            # Look for identifier or member expression
            for child in node.children:
                if child.type == 'identifier':
                    return child.text.decode('utf-8')
                elif child.type == 'member_expression':
                    # Handle method calls like object.method()
                    for member_child in child.children:
                        if member_child.type == 'property_identifier':
                            # Return the property name (method name)
                            return member_child.text.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error extracting JavaScript call target: {str(e)}")
        
        return None 

    def _dart_ast_to_class_data(self, ast_node: Node) -> List[Dict]:
        """
        Extract class structure data from Dart AST node.
        
        Args:
            ast_node (Node): Tree-sitter AST node for Dart code
            
        Returns:
            List[Dict]: List of dictionaries representing classes and relationships
        """
        try:
            classes = []
            relationships = []
            
            # Traverse AST to find class definitions
            def traverse_dart_classes(node: Node):
                if node.type == 'class_definition':
                    class_data = self._extract_dart_class_data(node)
                    if class_data:
                        classes.append(class_data)
                        
                        # Extract inheritance relationships
                        if class_data.get('superclass'):
                            relationships.append({
                                'type': 'inheritance',
                                'from': class_data['name'],
                                'to': class_data['superclass']
                            })
                        
                        # Extract mixin relationships
                        for mixin in class_data.get('mixins', []):
                            relationships.append({
                                'type': 'mixin',
                                'from': class_data['name'],
                                'to': mixin
                            })
                        
                        # Extract interface relationships
                        for interface in class_data.get('interfaces', []):
                            relationships.append({
                                'type': 'implements',
                                'from': class_data['name'],
                                'to': interface
                            })
                
                # Recursively traverse children
                for child in node.children:
                    traverse_dart_classes(child)
            
            traverse_dart_classes(ast_node)
            
            # Convert classes to standard format
            result = []
            for class_data in classes:
                result.append({
                    'type': 'class',
                    'name': class_data['name'],
                    'attributes': class_data.get('properties', []),
                    'methods': class_data.get('methods', []),
                    'superclass': class_data.get('superclass'),
                    'mixins': class_data.get('mixins', []),
                    'interfaces': class_data.get('interfaces', []),
                    'line': class_data.get('line', 0),
                    'is_abstract': class_data.get('is_abstract', False),
                    'is_widget': class_data.get('is_widget', False)
                })
            
            # Add relationships
            for relationship in relationships:
                result.append(relationship)
            
            logger.info(f"Extracted {len(classes)} Dart classes and {len(relationships)} relationships")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting Dart class data from AST: {str(e)}")
            return []
    
    def _extract_dart_class_data(self, node: Node) -> Optional[Dict]:
        """
        Extract Dart class information from a class definition node.
        
        Args:
            node (Node): Dart class definition node
            
        Returns:
            Optional[Dict]: Extracted class information
        """
        try:
            class_name = None
            superclass = None
            mixins = []
            interfaces = []
            methods = []
            properties = []
            is_abstract = False
            
            # Extract class name
            for child in node.children:
                if child.type == 'identifier':
                    class_name = child.text.decode('utf-8') if child.text else None
                    break
            
            if not class_name:
                return None
            
            # Check for abstract modifier
            parent_text = str(node.parent.text) if hasattr(node, 'parent') and node.parent else ""
            is_abstract = 'abstract' in parent_text
            
            # Extract inheritance information and class members
            for child in node.children:
                if child.type == 'superclass':
                    superclass = self._get_dart_type_name(child)
                elif child.type == 'mixins':
                    mixins = self._extract_dart_type_list(child)
                elif child.type == 'interfaces':
                    interfaces = self._extract_dart_type_list(child)
                elif child.type == 'class_body':
                    methods, properties = self._extract_dart_class_members(child)
            
            # Determine if this is a Flutter widget
            is_widget = self._is_dart_flutter_widget(class_name, superclass)
            
            return {
                'name': class_name,
                'line': node.start_point[0] + 1,
                'superclass': superclass,
                'mixins': mixins,
                'interfaces': interfaces,
                'methods': methods,
                'properties': properties,
                'is_abstract': is_abstract,
                'is_widget': is_widget
            }
            
        except Exception as e:
            logger.error(f"Error extracting Dart class data: {str(e)}")
            return None
    
    def _extract_dart_class_members(self, class_body: Node) -> Tuple[List[Dict], List[Dict]]:
        """
        Extract methods and properties from Dart class body.
        
        Args:
            class_body (Node): Dart class body node
            
        Returns:
            Tuple[List[Dict], List[Dict]]: (methods, properties)
        """
        methods = []
        properties = []
        
        try:
            for child in class_body.children:
                if child.type == 'method_signature':
                    method_data = self._extract_dart_method_data(child)
                    if method_data:
                        methods.append(method_data)
                elif child.type in ['field_declaration', 'declared_identifier']:
                    property_data = self._extract_dart_property_data(child)
                    if property_data:
                        properties.append(property_data)
        except Exception as e:
            logger.error(f"Error extracting Dart class members: {str(e)}")
        
        return methods, properties
    
    def _extract_dart_method_data(self, node: Node) -> Optional[Dict]:
        """
        Extract Dart method information from a method signature node.
        
        Args:
            node (Node): Dart method signature node
            
        Returns:
            Optional[Dict]: Extracted method information
        """
        try:
            method_name = None
            return_type = 'void'
            parameters = []
            access_modifier = 'public'
            is_static = False
            is_async = False
            is_override = False
            
            # Extract method name
            for child in node.children:
                if child.type == 'identifier':
                    method_name = child.text.decode('utf-8') if child.text else None
                    break
            
            if not method_name:
                return None
            
            # Determine access modifier (Dart uses _ prefix for private)
            if method_name.startswith('_'):
                access_modifier = 'private'
            
            # Extract method details
            for child in node.children:
                if child.type == 'type_annotation':
                    return_type = child.text.decode('utf-8') if child.text else 'void'
                elif child.type == 'formal_parameter_list':
                    parameters = self._extract_dart_parameters(child)
            
            # Check for modifiers in parent context
            parent_text = str(node.parent.text) if hasattr(node, 'parent') and node.parent else ""
            is_static = 'static' in parent_text
            is_async = 'async' in parent_text
            is_override = '@override' in parent_text
            
            return {
                'name': method_name,
                'return_type': return_type,
                'parameters': parameters,
                'access_modifier': access_modifier,
                'is_static': is_static,
                'is_async': is_async,
                'is_override': is_override,
                'line': node.start_point[0] + 1
            }
            
        except Exception as e:
            logger.error(f"Error extracting Dart method data: {str(e)}")
            return None
    
    def _extract_dart_property_data(self, node: Node) -> Optional[Dict]:
        """
        Extract Dart property information from a field declaration node.
        
        Args:
            node (Node): Dart field declaration node
            
        Returns:
            Optional[Dict]: Extracted property information
        """
        try:
            property_name = None
            property_type = 'dynamic'
            access_modifier = 'public'
            is_static = False
            is_final = False
            is_const = False
            
            # Extract property name
            for child in node.children:
                if child.type == 'identifier':
                    property_name = child.text.decode('utf-8') if child.text else None
                    break
            
            if not property_name:
                return None
            
            # Determine access modifier
            if property_name.startswith('_'):
                access_modifier = 'private'
            
            # Extract property details
            for child in node.children:
                if child.type == 'type_annotation':
                    property_type = child.text.decode('utf-8') if child.text else 'dynamic'
            
            # Check for modifiers in parent context
            parent_text = str(node.parent.text) if hasattr(node, 'parent') and node.parent else ""
            is_static = 'static' in parent_text
            is_final = 'final' in parent_text
            is_const = 'const' in parent_text
            
            return {
                'name': property_name,
                'type': property_type,
                'access_modifier': access_modifier,
                'is_static': is_static,
                'is_final': is_final,
                'is_const': is_const,
                'line': node.start_point[0] + 1
            }
            
        except Exception as e:
            logger.error(f"Error extracting Dart property data: {str(e)}")
            return None
    
    def _extract_dart_parameters(self, node: Node) -> List[str]:
        """
        Extract parameter names from Dart formal parameter list.
        
        Args:
            node (Node): Dart formal parameter list node
            
        Returns:
            List[str]: List of parameter names
        """
        parameters = []
        
        try:
            for child in node.children:
                if child.type in ['normal_formal_parameter', 'optional_formal_parameter', 'named_formal_parameter']:
                    param_name = None
                    param_type = None
                    
                    for param_child in child.children:
                        if param_child.type == 'identifier':
                            param_name = param_child.text.decode('utf-8') if param_child.text else None
                        elif param_child.type == 'type_annotation':
                            param_type = param_child.text.decode('utf-8') if param_child.text else None
                    
                    if param_name:
                        if param_type:
                            parameters.append(f"{param_type} {param_name}")
                        else:
                            parameters.append(param_name)
        except Exception as e:
            logger.error(f"Error extracting Dart parameters: {str(e)}")
        
        return parameters
    
    def _dart_ast_to_sequence_data(self, ast_node: Node, pr_changes: Optional[Dict] = None,
                                 rag_agent: Optional[Any] = None) -> List[Dict]:
        """
        Extract sequence data from Dart AST focusing on PR changes.
        
        Args:
            ast_node (Node): Tree-sitter AST node for Dart code
            pr_changes (Optional[Dict]): Information about PR changes
            rag_agent (Optional[Any]): RAG agent for resolving external calls
            
        Returns:
            List[Dict]: List of sequence interactions and participants
        """
        try:
            interactions = []
            participants = set()
            
            # If no PR changes specified, analyze all functions
            if not pr_changes:
                pr_changes = {'modified_functions': [], 'added_functions': []}
            
            # Find all function definitions first
            all_functions = self._extract_dart_functions(ast_node)
            
            # Identify entry points from PR changes
            entry_functions = []
            for func_name in pr_changes.get('modified_functions', []) + pr_changes.get('added_functions', []):
                matching_funcs = [f for f in all_functions if f['name'] == func_name]
                entry_functions.extend(matching_funcs)
            
            # If no specific changes, use first few functions as entry points
            if not entry_functions:
                entry_functions = all_functions[:3]  # Limit to first 3 functions
            
            # Trace call graphs from entry points
            for entry_func in entry_functions:
                logger.info(f"Tracing Dart sequence from function: {entry_func['name']}")
                
                # Add entry function as participant
                participant_name = f"{entry_func.get('class', 'Global')}.{entry_func['name']}"
                participants.add(participant_name)
                
                # Trace calls from this function
                call_chain = self._trace_dart_function_calls(
                    entry_func, all_functions, depth=0, visited=set()
                )
                
                interactions.extend(call_chain)
                
                # Add all called functions as participants
                for interaction in call_chain:
                    participants.add(interaction['caller'])
                    participants.add(interaction['callee'])
            
            # Build sequence data structure
            sequence_data = {
                'participants': list(participants),
                'interactions': interactions,
                'entry_points': [f"{f.get('class', 'Global')}.{f['name']}" for f in entry_functions],
                'language': 'dart'
            }
            
            logger.info(f"Extracted Dart sequence data: {len(participants)} participants, "
                       f"{len(interactions)} interactions")
            
            return [sequence_data]
            
        except Exception as e:
            logger.error(f"Error extracting Dart sequence data: {str(e)}")
            return []
    
    def _extract_dart_functions(self, ast_node: Node) -> List[Dict]:
        """
        Extract all function definitions from Dart AST.
        
        Args:
            ast_node (Node): Tree-sitter AST node
            
        Returns:
            List[Dict]: List of function information
        """
        functions = []
        
        try:
            # Traverse AST to find function definitions
            def traverse_dart_functions(node: Node, class_name: Optional[str] = None):
                if node.type == 'class_definition':
                    # Extract class name for context
                    current_class = None
                    for child in node.children:
                        if child.type == 'identifier':
                            current_class = child.text.decode('utf-8') if child.text else None
                            break
                    
                    # Recursively process class body with class context
                    for child in node.children:
                        traverse_dart_functions(child, current_class)
                
                elif node.type in ['function_signature', 'method_signature']:
                    func_data = self._extract_dart_function_for_sequence(node, class_name)
                    if func_data:
                        functions.append(func_data)
                
                else:
                    # Recursively process children
                    for child in node.children:
                        traverse_dart_functions(child, class_name)
            
            traverse_dart_functions(ast_node)
            
        except Exception as e:
            logger.error(f"Error extracting Dart functions: {str(e)}")
        
        return functions
    
    def _extract_dart_function_for_sequence(self, node: Node, class_name: Optional[str] = None) -> Optional[Dict]:
        """
        Extract Dart function information for sequence analysis.
        
        Args:
            node (Node): Function signature node
            class_name (Optional[str]): Name of containing class
            
        Returns:
            Optional[Dict]: Function information for sequence analysis
        """
        try:
            function_name = None
            
            # Extract function name
            for child in node.children:
                if child.type == 'identifier':
                    function_name = child.text.decode('utf-8') if child.text else None
                    break
            
            if not function_name:
                return None
            
            return {
                'name': function_name,
                'class': class_name,
                'node': node,
                'line': node.start_point[0] + 1,
                'full_name': f"{class_name}.{function_name}" if class_name else function_name
            }
            
        except Exception as e:
            logger.error(f"Error extracting Dart function for sequence: {str(e)}")
            return None
    
    def _trace_dart_function_calls(self, function: Dict, all_functions: List[Dict],
                                 depth: int, visited: Set[str]) -> List[Dict]:
        """
        Trace function calls from a Dart function.
        
        Args:
            function (Dict): Function to trace calls from
            all_functions (List[Dict]): All available functions
            depth (int): Current recursion depth
            visited (Set[str]): Set of already visited functions
            
        Returns:
            List[Dict]: List of call interactions
        """
        interactions = []
        
        if depth >= self.max_sequence_depth:
            return interactions
        
        function_name = function['full_name']
        if function_name in visited:
            return interactions
        
        visited.add(function_name)
        
        try:
            # Find function calls in the function body
            function_node = function['node']
            calls_found = []
            
            def find_dart_calls(node: Node):
                if node.type == 'invocation_expression':
                    call_target = self._extract_dart_call_target(node)
                    if call_target and not self._is_builtin_or_library_function(call_target):
                        calls_found.append(call_target)
                
                # Recursively search children
                for child in node.children:
                    find_dart_calls(child)
            
            find_dart_calls(function_node)
            
            # Limit calls per function
            calls_found = calls_found[:self.max_calls_per_function]
            
            # Create interactions for each call
            for call_target in calls_found:
                interactions.append({
                    'caller': function_name,
                    'callee': call_target,
                    'type': 'function_call',
                    'line': function['line']
                })
                
                # Find the called function and trace its calls
                called_function = None
                for func in all_functions:
                    if func['full_name'] == call_target or func['name'] == call_target:
                        called_function = func
                        break
                
                if called_function:
                    nested_interactions = self._trace_dart_function_calls(
                        called_function, all_functions, depth + 1, visited.copy()
                    )
                    interactions.extend(nested_interactions)
            
        except Exception as e:
            logger.error(f"Error tracing Dart function calls: {str(e)}")
        
        return interactions
    
    def _extract_dart_call_target(self, node: Node) -> Optional[str]:
        """
        Extract the target of a Dart function call.
        
        Args:
            node (Node): Invocation expression node
            
        Returns:
            Optional[str]: Target function name
        """
        try:
            # Look for function identifier in invocation
            for child in node.children:
                if child.type == 'identifier':
                    return child.text.decode('utf-8') if child.text else None
                elif child.type == 'selector_expression':
                    # Handle method calls like object.method()
                    for selector_child in child.children:
                        if selector_child.type == 'identifier':
                            return selector_child.text.decode('utf-8') if selector_child.text else None
        except Exception as e:
            logger.error(f"Error extracting Dart call target: {str(e)}")
        
        return None
    
    # Helper methods for Dart analysis
    
    def _get_dart_type_name(self, node: Node) -> Optional[str]:
        """
        Get type name from a Dart type node.
        
        Args:
            node (Node): Type node
            
        Returns:
            Optional[str]: Type name
        """
        try:
            for child in node.children:
                if child.type in ['type_identifier', 'identifier']:
                    return child.text.decode('utf-8') if child.text else None
        except Exception:
            pass
        return None
    
    def _extract_dart_type_list(self, node: Node) -> List[str]:
        """
        Extract a list of type names from a Dart type list node.
        
        Args:
            node (Node): Type list node
            
        Returns:
            List[str]: List of type names
        """
        types = []
        
        try:
            for child in node.children:
                if child.type in ['type', 'type_identifier', 'identifier']:
                    type_name = child.text.decode('utf-8') if child.text else None
                    if type_name:
                        types.append(type_name)
        except Exception as e:
            logger.debug(f"Error extracting Dart type list: {str(e)}")
        
        return types
    
    def _is_dart_flutter_widget(self, class_name: str, superclass: Optional[str]) -> bool:
        """
        Check if a Dart class is a Flutter widget.
        
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
            'InheritedWidget', 'RenderObjectWidget', 'ProxyWidget',
            'State'  # State classes for StatefulWidget
        ]
        
        return superclass in flutter_widget_types or 'Widget' in superclass