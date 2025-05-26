"""Unit tests for DiagrammingEngine."""

import pytest
from unittest.mock import Mock, patch
from tree_sitter import Node

from src.core_engine.diagramming_engine import DiagrammingEngine


@pytest.fixture
def mock_ast_node():
    """Create a mock AST node for testing."""
    # Create mock nodes for a simple class
    mock_node = Mock(spec=Node)
    mock_language = Mock()
    mock_query = Mock()
    
    # Mock class name node
    class_name_node = Mock(spec=Node)
    class_name_node.text = b'TestClass'
    class_name_node.type = 'identifier'
    class_name_node.start_point = (0, 0)
    
    # Mock superclass node
    superclass_node = Mock(spec=Node)
    superclass_node.text = b'BaseClass'
    superclass_node.type = 'identifier'
    
    # Mock argument list (superclasses)
    arg_list_node = Mock(spec=Node)
    arg_list_node.type = 'argument_list'
    arg_list_node.children = [superclass_node]
    
    # Mock class body
    class_body_node = Mock(spec=Node)
    class_body_node.type = 'block'
    
    # Mock class definition node
    class_def_node = Mock(spec=Node)
    class_def_node.type = 'class_definition'
    class_def_node.children = [class_name_node, arg_list_node, class_body_node]
    
    # Mock query captures
    mock_query.captures.return_value = [
        (class_def_node, 'class_def')
    ]
    
    mock_language.query.return_value = mock_query
    mock_node.language = mock_language
    
    return mock_node


@pytest.fixture
def mock_ast_with_methods():
    """Create a mock AST node with methods and attributes."""
    mock_node = Mock(spec=Node)
    mock_language = Mock()
    
    # Mock class components
    class_name_node = Mock(spec=Node)
    class_name_node.text = b'ComplexClass'
    class_name_node.type = 'identifier'
    class_name_node.start_point = (0, 0)
    
    class_body_node = Mock(spec=Node)
    class_body_node.type = 'block'
    
    # Mock method
    method_name_node = Mock(spec=Node)
    method_name_node.text = b'test_method'
    method_name_node.type = 'identifier'
    
    param_node = Mock(spec=Node)
    param_node.text = b'param1'
    param_node.type = 'identifier'
    
    params_node = Mock(spec=Node)
    params_node.type = 'parameters'
    params_node.children = [param_node]
    
    method_def_node = Mock(spec=Node)
    method_def_node.type = 'function_definition'
    method_def_node.children = [method_name_node, params_node]
    
    # Mock attribute
    attr_name_node = Mock(spec=Node)
    attr_name_node.text = b'test_attr'
    attr_name_node.type = 'identifier'
    
    assignment_node = Mock(spec=Node)
    assignment_node.type = 'assignment'
    assignment_node.children = [attr_name_node]
    
    class_def_node = Mock(spec=Node)
    class_def_node.type = 'class_definition'
    class_def_node.children = [class_name_node, class_body_node]
    
    # Setup queries
    def mock_query_side_effect(query_string):
        mock_query = Mock()
        if 'class_definition' in query_string:
            mock_query.captures.return_value = [(class_def_node, 'class_def')]
        elif 'function_definition' in query_string:
            mock_query.captures.return_value = [(method_def_node, 'method_def')]
        elif 'assignment' in query_string:
            mock_query.captures.return_value = [(assignment_node, 'assignment')]
        else:
            mock_query.captures.return_value = []
        return mock_query
    
    mock_language.query.side_effect = mock_query_side_effect
    mock_node.language = mock_language
    class_body_node.language = mock_language
    
    return mock_node, class_body_node


@pytest.fixture
def diagramming_engine():
    """Create a DiagrammingEngine instance."""
    return DiagrammingEngine()


@pytest.fixture
def mermaid_engine():
    """Create a DiagrammingEngine instance with Mermaid format."""
    return DiagrammingEngine(diagram_format='mermaid')


def test_init_default_format(diagramming_engine):
    """Test DiagrammingEngine initialization with default format."""
    assert diagramming_engine.diagram_format == 'plantuml'
    assert 'plantuml' in diagramming_engine.supported_formats
    assert 'mermaid' in diagramming_engine.supported_formats
    assert 'python' in diagramming_engine.supported_languages


def test_init_mermaid_format(mermaid_engine):
    """Test DiagrammingEngine initialization with Mermaid format."""
    assert mermaid_engine.diagram_format == 'mermaid'


def test_init_invalid_format():
    """Test DiagrammingEngine initialization with invalid format."""
    with pytest.raises(ValueError, match="Unsupported diagram format"):
        DiagrammingEngine(diagram_format='invalid')


def test_python_ast_to_class_data_simple(diagramming_engine, mock_ast_node):
    """Test extracting class data from simple Python AST."""
    class_data = diagramming_engine._python_ast_to_class_data(mock_ast_node)
    
    # Should have 1 class and 1 relationship
    classes = [item for item in class_data if item.get('type') == 'class']
    relationships = [item for item in class_data if item.get('type') != 'class']
    
    assert len(classes) == 1
    assert len(relationships) == 1
    
    # Verify class data
    test_class = classes[0]
    assert test_class['name'] == 'TestClass'
    assert test_class['type'] == 'class'
    assert test_class['line'] == 1
    assert 'BaseClass' in test_class['superclasses']
    
    # Verify relationship
    inheritance = relationships[0]
    assert inheritance['type'] == 'inheritance'
    assert inheritance['from'] == 'TestClass'
    assert inheritance['to'] == 'BaseClass'


def test_python_ast_to_class_data_with_members(diagramming_engine, mock_ast_with_methods):
    """Test extracting class data with methods and attributes."""
    mock_node, class_body_node = mock_ast_with_methods
    
    class_data = diagramming_engine._python_ast_to_class_data(mock_node)
    
    classes = [item for item in class_data if item.get('type') == 'class']
    assert len(classes) == 1
    
    test_class = classes[0]
    assert test_class['name'] == 'ComplexClass'
    assert len(test_class['methods']) == 1
    assert len(test_class['attributes']) == 1
    
    # Verify method
    method = test_class['methods'][0]
    assert method['name'] == 'test_method'
    assert method['access_modifier'] == 'public'
    assert 'param1' in method['parameters']
    
    # Verify attribute
    attr = test_class['attributes'][0]
    assert attr['name'] == 'test_attr'
    assert attr['access_modifier'] == 'public'


def test_extract_class_members_private_methods(diagramming_engine):
    """Test access modifier detection for private methods."""
    # Mock a private method
    mock_body = Mock(spec=Node)
    mock_language = Mock()
    
    method_name_node = Mock(spec=Node)
    method_name_node.text = b'__private_method'
    method_name_node.type = 'identifier'
    
    method_def_node = Mock(spec=Node)
    method_def_node.type = 'function_definition'
    method_def_node.children = [method_name_node]
    
    mock_query = Mock()
    mock_query.captures.return_value = [(method_def_node, 'method_def')]
    mock_language.query.return_value = mock_query
    mock_body.language = mock_language
    
    class_data = {'methods': [], 'attributes': []}
    diagramming_engine._extract_class_members(mock_body, class_data)
    
    assert len(class_data['methods']) == 1
    assert class_data['methods'][0]['access_modifier'] == 'private'


def test_extract_class_members_protected_attributes(diagramming_engine):
    """Test access modifier detection for protected attributes."""
    # Mock a protected attribute
    mock_body = Mock(spec=Node)
    mock_language = Mock()
    
    attr_name_node = Mock(spec=Node)
    attr_name_node.text = b'_protected_attr'
    attr_name_node.type = 'identifier'
    
    assignment_node = Mock(spec=Node)
    assignment_node.type = 'assignment'
    assignment_node.children = [attr_name_node]
    
    def mock_query_side_effect(query_string):
        mock_query = Mock()
        if 'function_definition' in query_string:
            mock_query.captures.return_value = []
        elif 'assignment' in query_string:
            mock_query.captures.return_value = [(assignment_node, 'assignment')]
        return mock_query
    
    mock_language.query.side_effect = mock_query_side_effect
    mock_body.language = mock_language
    
    class_data = {'methods': [], 'attributes': []}
    diagramming_engine._extract_class_members(mock_body, class_data)
    
    assert len(class_data['attributes']) == 1
    assert class_data['attributes'][0]['access_modifier'] == 'protected'


def test_generate_class_diagram_plantuml(diagramming_engine):
    """Test PlantUML class diagram generation."""
    # Mock AST data
    mock_ast = Mock()
    mock_ast.root_node = Mock()
    
    code_files = {
        'test.py': mock_ast
    }
    
    # Mock class data extraction
    with patch.object(diagramming_engine, '_python_ast_to_class_data') as mock_extract:
        mock_extract.return_value = [
            {
                'type': 'class',
                'name': 'TestClass',
                'attributes': [
                    {'name': 'attr1', 'access_modifier': 'public', 'type': 'str'}
                ],
                'methods': [
                    {'name': 'method1', 'access_modifier': 'public', 'parameters': ['param1'], 'return_type': 'int'}
                ],
                'superclasses': [],
                'line': 1
            }
        ]
        
        diagram = diagramming_engine.generate_class_diagram(code_files, 'python')
        
        # Verify PlantUML structure
        assert '@startuml' in diagram
        assert '@enduml' in diagram
        assert 'class TestClass {' in diagram
        assert '+attr1: str' in diagram
        assert '+method1(param1): int' in diagram


def test_generate_class_diagram_mermaid(mermaid_engine):
    """Test Mermaid.js class diagram generation."""
    # Mock AST data
    mock_ast = Mock()
    mock_ast.root_node = Mock()
    
    code_files = {
        'test.py': mock_ast
    }
    
    # Mock class data extraction
    with patch.object(mermaid_engine, '_python_ast_to_class_data') as mock_extract:
        mock_extract.return_value = [
            {
                'type': 'class',
                'name': 'TestClass',
                'attributes': [
                    {'name': 'attr1', 'access_modifier': 'private', 'type': 'str'}
                ],
                'methods': [
                    {'name': 'method1', 'access_modifier': 'protected', 'parameters': [], 'return_type': 'void'}
                ],
                'superclasses': [],
                'line': 1
            }
        ]
        
        diagram = mermaid_engine.generate_class_diagram(code_files, 'python')
        
        # Verify Mermaid structure
        assert 'classDiagram' in diagram
        assert 'class TestClass {' in diagram
        assert '-str attr1' in diagram
        assert '#method1() void' in diagram


def test_generate_class_diagram_with_inheritance(diagramming_engine):
    """Test class diagram generation with inheritance."""
    mock_ast = Mock()
    mock_ast.root_node = Mock()
    
    code_files = {'test.py': mock_ast}
    
    with patch.object(diagramming_engine, '_python_ast_to_class_data') as mock_extract:
        mock_extract.return_value = [
            {
                'type': 'class',
                'name': 'ChildClass',
                'attributes': [],
                'methods': [],
                'superclasses': ['BaseClass'],
                'line': 1
            },
            {
                'type': 'inheritance',
                'from': 'ChildClass',
                'to': 'BaseClass'
            }
        ]
        
        diagram = diagramming_engine.generate_class_diagram(code_files, 'python')
        
        assert 'BaseClass <|-- ChildClass' in diagram


def test_generate_class_diagram_with_changes(diagramming_engine):
    """Test class diagram generation with change highlighting."""
    mock_ast = Mock()
    mock_ast.root_node = Mock()
    
    code_files = {'test.py': mock_ast}
    changes = {'modified_classes': ['TestClass']}
    
    with patch.object(diagramming_engine, '_python_ast_to_class_data') as mock_extract:
        mock_extract.return_value = [
            {
                'type': 'class',
                'name': 'TestClass',
                'attributes': [],
                'methods': [],
                'superclasses': [],
                'line': 1
            }
        ]
        
        diagram = diagramming_engine.generate_class_diagram(code_files, 'python', changes)
        
        # Should include styling for changed class
        assert 'class TestClass #lightblue' in diagram


def test_generate_class_diagram_unsupported_language(diagramming_engine):
    """Test error handling for unsupported language."""
    with pytest.raises(ValueError, match="Unsupported language"):
        diagramming_engine.generate_class_diagram({}, 'java')


def test_generate_class_diagram_error_handling(diagramming_engine):
    """Test error handling in diagram generation."""
    # Mock AST data that will cause an error
    mock_ast = Mock()
    mock_ast.root_node = Mock()
    
    code_files = {'test.py': mock_ast}
    
    with patch.object(diagramming_engine, '_python_ast_to_class_data') as mock_extract:
        mock_extract.side_effect = Exception("Test error")
        
        diagram = diagramming_engine.generate_class_diagram(code_files, 'python')
        
        # Should return error diagram
        assert '@startuml' in diagram
        assert 'Error generating diagram' in diagram
        assert '@enduml' in diagram


def test_get_plantuml_access_symbols(diagramming_engine):
    """Test PlantUML access symbol mapping."""
    assert diagramming_engine._get_plantuml_access_symbol('public') == '+'
    assert diagramming_engine._get_plantuml_access_symbol('protected') == '#'
    assert diagramming_engine._get_plantuml_access_symbol('private') == '-'
    assert diagramming_engine._get_plantuml_access_symbol('unknown') == '+'


def test_get_mermaid_access_symbols(diagramming_engine):
    """Test Mermaid.js access symbol mapping."""
    assert diagramming_engine._get_mermaid_access_symbol('public') == '+'
    assert diagramming_engine._get_mermaid_access_symbol('protected') == '#'
    assert diagramming_engine._get_mermaid_access_symbol('private') == '-'
    assert diagramming_engine._get_mermaid_access_symbol('unknown') == '+'


def test_get_supported_formats(diagramming_engine):
    """Test getting supported formats."""
    formats = diagramming_engine.get_supported_formats()
    assert 'plantuml' in formats
    assert 'mermaid' in formats
    assert isinstance(formats, list)


def test_get_supported_languages(diagramming_engine):
    """Test getting supported languages."""
    languages = diagramming_engine.get_supported_languages()
    assert 'python' in languages
    assert isinstance(languages, list)


def test_set_diagram_format(diagramming_engine):
    """Test setting diagram format."""
    diagramming_engine.set_diagram_format('mermaid')
    assert diagramming_engine.diagram_format == 'mermaid'
    
    with pytest.raises(ValueError, match="Unsupported diagram format"):
        diagramming_engine.set_diagram_format('invalid')


def test_get_engine_info(diagramming_engine):
    """Test getting engine information."""
    info = diagramming_engine.get_engine_info()
    
    assert info['engine_name'] == 'DiagrammingEngine'
    assert info['version'] == '1.0.0'
    assert info['current_format'] == 'plantuml'
    assert 'class_diagrams' in info['capabilities']
    assert 'inheritance_relationships' in info['capabilities']
    assert 'change_highlighting' in info['capabilities']


def test_empty_ast_handling(diagramming_engine):
    """Test handling of empty or invalid AST data."""
    code_files = {
        'empty.py': None,
        'invalid.py': Mock()  # No root_node attribute
    }
    
    diagram = diagramming_engine.generate_class_diagram(code_files, 'python')
    
    # Should generate empty diagram without errors
    assert '@startuml' in diagram
    assert '@enduml' in diagram


def test_multiple_files_processing(diagramming_engine):
    """Test processing multiple files."""
    mock_ast1 = Mock()
    mock_ast1.root_node = Mock()
    mock_ast2 = Mock()
    mock_ast2.root_node = Mock()
    
    code_files = {
        'file1.py': mock_ast1,
        'file2.py': mock_ast2
    }
    
    with patch.object(diagramming_engine, '_python_ast_to_class_data') as mock_extract:
        mock_extract.side_effect = [
            [{'type': 'class', 'name': 'Class1', 'attributes': [], 'methods': [], 'superclasses': [], 'line': 1}],
            [{'type': 'class', 'name': 'Class2', 'attributes': [], 'methods': [], 'superclasses': [], 'line': 1}]
        ]
        
        diagram = diagramming_engine.generate_class_diagram(code_files, 'python')
        
        # Should include both classes
        assert 'class Class1 {' in diagram
        assert 'class Class2 {' in diagram
        
        # Should have been called twice
        assert mock_extract.call_count == 2 