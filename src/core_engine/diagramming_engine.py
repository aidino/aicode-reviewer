"""
Diagramming Engine for AI Code Review System.

This module implements the DiagrammingEngine responsible for generating
visual diagrams (class diagrams, sequence diagrams) from code analysis.
Currently focuses on Python class diagrams using PlantUML/Mermaid.js syntax.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Union
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
        self.supported_languages = ['python']
        
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
                    class_data = self._python_ast_to_class_data(ast_data.root_node)
                    
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
            'version': '1.0.0',
            'current_format': self.diagram_format,
            'supported_formats': self.supported_formats,
            'supported_languages': self.supported_languages,
            'capabilities': [
                'class_diagrams',
                'inheritance_relationships',
                'change_highlighting',
                'plantuml_output',
                'mermaid_output'
            ]
        } 