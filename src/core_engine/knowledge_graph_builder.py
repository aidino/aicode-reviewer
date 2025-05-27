"""Knowledge Graph Builder for creating and managing code knowledge graphs in Neo4j."""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from tree_sitter import Node
from .agents.knowledge_graph.neo4j_client import Neo4jClient
from .agents.knowledge_graph.schema import CodeNode, CodeEdge, CodeGraph, NodeType, EdgeType

logger = logging.getLogger(__name__)

class KnowledgeGraphBuilder:
    """Builds and manages code knowledge graphs in Neo4j from AST data."""

    def __init__(self, neo4j_client: Optional[Neo4jClient] = None):
        """Initialize the knowledge graph builder.
        
        Args:
            neo4j_client: Optional Neo4j client instance. If not provided, creates new one.
        """
        self.client = neo4j_client or Neo4jClient()
        
    def build_from_ast(self, ast: Node, file_path: str, language: str) -> CodeGraph:
        """Build knowledge graph from an AST.
        
        Args:
            ast: Tree-sitter AST node
            file_path: Path to the source file
            language: Programming language of the source file
            
        Returns:
            CodeGraph containing nodes and edges extracted from AST
        """
        nodes: List[CodeNode] = []
        edges: List[CodeEdge] = []
        
        # Create file node
        file_node = CodeNode(
            id=f"file:{file_path}",
            type=NodeType.FILE,
            name=Path(file_path).name,
            file_path=file_path,
            language=language
        )
        nodes.append(file_node)
        
        # Process AST recursively
        self._process_ast_node(ast, file_node.id, nodes, edges)
        
        # Create graph
        graph = CodeGraph(nodes=nodes, edges=edges)
        
        # Store in Neo4j
        try:
            self.client.create_graph(graph)
            logger.info(f"Successfully built knowledge graph for {file_path}")
        except Exception as e:
            logger.error(f"Error building knowledge graph for {file_path}: {str(e)}")
            
        return graph
        
    def _process_ast_node(
        self,
        node: Node,
        parent_id: str,
        nodes: List[CodeNode],
        edges: List[CodeEdge]
    ):
        """Process an AST node recursively to extract nodes and edges.
        
        Args:
            node: Tree-sitter AST node
            parent_id: ID of the parent node
            nodes: List to collect CodeNode instances
            edges: List to collect CodeEdge instances
        """
        node_type = node.type
        
        # Handle different node types
        if node_type == "class_definition":
            class_node = self._create_class_node(node)
            nodes.append(class_node)
            edges.append(CodeEdge(
                source_id=parent_id,
                target_id=class_node.id,
                type=EdgeType.CONTAINS
            ))
            
            # Process class body
            for child in node.children:
                if child.type == "block":
                    self._process_ast_node(child, class_node.id, nodes, edges)
                    
        elif node_type == "function_definition":
            func_node = self._create_function_node(node)
            nodes.append(func_node)
            edges.append(CodeEdge(
                source_id=parent_id,
                target_id=func_node.id,
                type=EdgeType.CONTAINS
            ))
            
            # Extract function calls
            self._extract_function_calls(node, func_node.id, nodes, edges)
            
        elif node_type == "import_statement":
            self._process_import(node, parent_id, nodes, edges)
            
        # Recursively process children
        for child in node.children:
            self._process_ast_node(child, parent_id, nodes, edges)
            
    def _create_class_node(self, node: Node) -> CodeNode:
        """Create a CodeNode for a class definition."""
        name = ""
        for child in node.children:
            if child.type == "identifier":
                name = child.text.decode('utf-8')
                break
                
        return CodeNode(
            id=f"class:{name}",
            type=NodeType.CLASS,
            name=name,
            properties={
                "start_line": str(node.start_point[0]),
                "end_line": str(node.end_point[0])
            }
        )
        
    def _create_function_node(self, node: Node) -> CodeNode:
        """Create a CodeNode for a function definition."""
        name = ""
        for child in node.children:
            if child.type == "identifier":
                name = child.text.decode('utf-8')
                break
                
        return CodeNode(
            id=f"function:{name}",
            type=NodeType.FUNCTION,
            name=name,
            properties={
                "start_line": str(node.start_point[0]),
                "end_line": str(node.end_point[0])
            }
        )
        
    def _extract_function_calls(
        self,
        node: Node,
        source_id: str,
        nodes: List[CodeNode],
        edges: List[CodeEdge]
    ):
        """Extract function calls from a function body."""
        def visit(node):
            if node.type == "call":
                for child in node.children:
                    if child.type == "identifier":
                        target_name = child.text.decode('utf-8')
                        edges.append(CodeEdge(
                            source_id=source_id,
                            target_id=f"function:{target_name}",
                            type=EdgeType.CALLS
                        ))
            for child in node.children:
                visit(child)
                
        visit(node)
        
    def _process_import(
        self,
        node: Node,
        parent_id: str,
        nodes: List[CodeNode],
        edges: List[CodeEdge]
    ):
        """Process import statements to create module nodes and relationships."""
        module_name = ""
        for child in node.children:
            if child.type == "dotted_name":
                module_name = child.text.decode('utf-8')
                break
                
        if module_name:
            module_node = CodeNode(
                id=f"module:{module_name}",
                type=NodeType.MODULE,
                name=module_name
            )
            nodes.append(module_node)
            edges.append(CodeEdge(
                source_id=parent_id,
                target_id=module_node.id,
                type=EdgeType.IMPORTS
            ))
            
    def find_related_code(self, name: str, max_distance: int = 2) -> Dict[str, Any]:
        """Find code related to a given component name."""
        return self.client.find_related(name, max_distance)
        
    def find_dependencies(self, file_path: str) -> Dict[str, Any]:
        """Find dependencies for a given file."""
        return self.client.find_dependencies(file_path)
        
    def find_call_hierarchy(self, function_name: str) -> Dict[str, Any]:
        """Find call hierarchy for a given function."""
        return self.client.find_call_hierarchy(function_name)
        
    def close(self):
        """Close Neo4j client connection."""
        self.client.close() 