"""Unit tests for KnowledgeGraphBuilder."""

import pytest
from unittest.mock import Mock, patch
from tree_sitter import Node

from src.core_engine.knowledge_graph_builder import KnowledgeGraphBuilder
from src.core_engine.agents.knowledge_graph.schema import CodeNode, CodeEdge, CodeGraph, NodeType, EdgeType

@pytest.fixture
def mock_neo4j_client():
    return Mock()

@pytest.fixture
def mock_ast_node():
    node = Mock(spec=Node)
    node.type = "module"
    node.children = []
    node.start_point = (0, 0)
    node.end_point = (10, 0)
    return node

@pytest.fixture
def builder(mock_neo4j_client):
    return KnowledgeGraphBuilder(neo4j_client=mock_neo4j_client)

def test_initialization(mock_neo4j_client):
    """Test KnowledgeGraphBuilder initialization."""
    builder = KnowledgeGraphBuilder(neo4j_client=mock_neo4j_client)
    assert builder.client == mock_neo4j_client

def test_build_from_ast_creates_file_node(builder, mock_ast_node):
    """Test that build_from_ast creates a file node."""
    graph = builder.build_from_ast(mock_ast_node, "test.py", "python")
    
    assert len(graph.nodes) >= 1
    file_node = next(n for n in graph.nodes if n.type == NodeType.FILE)
    assert file_node.name == "test.py"
    assert file_node.language == "python"

def test_process_class_definition(builder):
    """Test processing of class definitions."""
    class_node = Mock(spec=Node)
    class_node.type = "class_definition"
    
    identifier = Mock(spec=Node)
    identifier.type = "identifier"
    identifier.text = b"TestClass"
    
    class_node.children = [identifier]
    class_node.start_point = (1, 0)
    class_node.end_point = (10, 0)
    
    nodes = []
    edges = []
    builder._process_ast_node(class_node, "file:test.py", nodes, edges)
    
    assert len(nodes) == 1
    assert nodes[0].type == NodeType.CLASS
    assert nodes[0].name == "TestClass"
    
    assert len(edges) == 1
    assert edges[0].type == EdgeType.CONTAINS
    assert edges[0].source_id == "file:test.py"
    assert edges[0].target_id == "class:TestClass"

def test_process_function_definition(builder):
    """Test processing of function definitions."""
    func_node = Mock(spec=Node)
    func_node.type = "function_definition"
    
    identifier = Mock(spec=Node)
    identifier.type = "identifier"
    identifier.text = b"test_function"
    
    func_node.children = [identifier]
    func_node.start_point = (1, 0)
    func_node.end_point = (5, 0)
    
    nodes = []
    edges = []
    builder._process_ast_node(func_node, "class:TestClass", nodes, edges)
    
    assert len(nodes) == 1
    assert nodes[0].type == NodeType.FUNCTION
    assert nodes[0].name == "test_function"
    
    assert len(edges) == 1
    assert edges[0].type == EdgeType.CONTAINS
    assert edges[0].source_id == "class:TestClass"
    assert edges[0].target_id == "function:test_function"

def test_process_import_statement(builder):
    """Test processing of import statements."""
    import_node = Mock(spec=Node)
    import_node.type = "import_statement"
    
    dotted_name = Mock(spec=Node)
    dotted_name.type = "dotted_name"
    dotted_name.text = b"os.path"
    
    import_node.children = [dotted_name]
    
    nodes = []
    edges = []
    builder._process_ast_node(import_node, "file:test.py", nodes, edges)
    
    assert len(nodes) == 1
    assert nodes[0].type == NodeType.MODULE
    assert nodes[0].name == "os.path"
    
    assert len(edges) == 1
    assert edges[0].type == EdgeType.IMPORTS
    assert edges[0].source_id == "file:test.py"
    assert edges[0].target_id == "module:os.path"

def test_extract_function_calls(builder):
    """Test extraction of function calls."""
    call_node = Mock(spec=Node)
    call_node.type = "call"
    
    identifier = Mock(spec=Node)
    identifier.type = "identifier"
    identifier.text = b"called_function"
    
    call_node.children = [identifier]
    
    nodes = []
    edges = []
    builder._extract_function_calls(call_node, "function:caller", nodes, edges)
    
    assert len(edges) == 1
    assert edges[0].type == EdgeType.CALLS
    assert edges[0].source_id == "function:caller"
    assert edges[0].target_id == "function:called_function"

def test_find_related_code(builder, mock_neo4j_client):
    """Test finding related code."""
    builder.find_related_code("test_function")
    mock_neo4j_client.find_related.assert_called_once_with("test_function", 2)

def test_find_dependencies(builder, mock_neo4j_client):
    """Test finding dependencies."""
    builder.find_dependencies("test.py")
    mock_neo4j_client.find_dependencies.assert_called_once_with("test.py")

def test_find_call_hierarchy(builder, mock_neo4j_client):
    """Test finding call hierarchy."""
    builder.find_call_hierarchy("test_function")
    mock_neo4j_client.find_call_hierarchy.assert_called_once_with("test_function")

def test_close(builder, mock_neo4j_client):
    """Test closing Neo4j client connection."""
    builder.close()
    mock_neo4j_client.close.assert_called_once() 