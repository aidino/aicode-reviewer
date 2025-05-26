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
def mock_python_functions_ast():
    """Create a mock AST node with Python functions for sequence diagram testing."""
    mock_node = Mock(spec=Node)
    mock_language = Mock()
    
    # Mock function 1: main_function
    func1_name_node = Mock(spec=Node)
    func1_name_node.text = b'main_function'
    func1_name_node.type = 'identifier'
    func1_name_node.start_point = (0, 0)
    
    func1_body_node = Mock(spec=Node)
    func1_body_node.type = 'block'
    func1_body_node.language = mock_language
    
    func1_def_node = Mock(spec=Node)
    func1_def_node.type = 'function_definition'
    func1_def_node.children = [func1_name_node, func1_body_node]
    func1_def_node.start_point = (0, 0)
    
    # Mock function 2: helper_function
    func2_name_node = Mock(spec=Node)
    func2_name_node.text = b'helper_function'
    func2_name_node.type = 'identifier'
    func2_name_node.start_point = (5, 0)
    
    func2_body_node = Mock(spec=Node)
    func2_body_node.type = 'block'
    func2_body_node.language = mock_language
    
    func2_def_node = Mock(spec=Node)
    func2_def_node.type = 'function_definition'
    func2_def_node.children = [func2_name_node, func2_body_node]
    func2_def_node.start_point = (5, 0)
    
    # Mock function call in main_function
    call_func_name_node = Mock(spec=Node)
    call_func_name_node.text = b'helper_function'
    call_func_name_node.type = 'identifier'
    call_func_name_node.start_point = (2, 4)
    
    call_expr_node = Mock(spec=Node)
    call_expr_node.type = 'call'
    call_expr_node.children = [call_func_name_node]
    
    # Setup query side effects
    def mock_query_side_effect(query_string):
        mock_query = Mock()
        if 'function_definition' in query_string:
            mock_query.captures.return_value = [
                (func1_def_node, 'func_def'),
                (func1_name_node, 'func_name'),
                (func1_body_node, 'func_body'),
                (func2_def_node, 'func_def'),
                (func2_name_node, 'func_name'),
                (func2_body_node, 'func_body')
            ]
        elif 'call' in query_string:
            if query_string.startswith(query_string):  # When querying function body
                mock_query.captures.return_value = [
                    (call_expr_node, 'call_expr'),
                    (call_func_name_node, 'called_func')
                ]
            else:
                mock_query.captures.return_value = []
        else:
            mock_query.captures.return_value = []
        return mock_query
    
    mock_language.query.side_effect = mock_query_side_effect
    mock_node.language = mock_language
    
    return mock_node


@pytest.fixture
def mock_java_methods_ast():
    """Create a mock AST node with Java methods for sequence diagram testing."""
    mock_node = Mock(spec=Node)
    mock_language = Mock()
    
    # Mock class name
    class_name_node = Mock(spec=Node)
    class_name_node.text = b'TestClass'
    class_name_node.type = 'identifier'
    
    # Mock method 1: mainMethod
    method1_name_node = Mock(spec=Node)
    method1_name_node.text = b'mainMethod'
    method1_name_node.type = 'identifier'
    method1_name_node.start_point = (0, 0)
    
    method1_body_node = Mock(spec=Node)
    method1_body_node.type = 'block'
    method1_body_node.language = mock_language
    
    method1_def_node = Mock(spec=Node)
    method1_def_node.type = 'method_declaration'
    method1_def_node.children = [method1_name_node, method1_body_node]
    method1_def_node.start_point = (0, 0)
    
    # Mock method 2: helperMethod
    method2_name_node = Mock(spec=Node)
    method2_name_node.text = b'helperMethod'
    method2_name_node.type = 'identifier'
    method2_name_node.start_point = (10, 0)
    
    method2_body_node = Mock(spec=Node)
    method2_body_node.type = 'block'
    method2_body_node.language = mock_language
    
    method2_def_node = Mock(spec=Node)
    method2_def_node.type = 'method_declaration'
    method2_def_node.children = [method2_name_node, method2_body_node]
    method2_def_node.start_point = (10, 0)
    
    # Mock method invocation
    invoked_method_name_node = Mock(spec=Node)
    invoked_method_name_node.text = b'helperMethod'
    invoked_method_name_node.type = 'identifier'
    invoked_method_name_node.start_point = (5, 8)
    
    method_call_node = Mock(spec=Node)
    method_call_node.type = 'method_invocation'
    method_call_node.children = [invoked_method_name_node]
    
    # Mock class body and class definition
    class_body_node = Mock(spec=Node)
    class_body_node.type = 'class_body'
    class_body_node.children = [method1_def_node, method2_def_node]
    
    class_def_node = Mock(spec=Node)
    class_def_node.type = 'class_declaration'
    class_def_node.children = [class_name_node, class_body_node]
    
    # Setup query side effects
    def mock_query_side_effect(query_string):
        mock_query = Mock()
        if 'class_declaration' in query_string and 'method_declaration' in query_string:
            mock_query.captures.return_value = [
                (class_name_node, 'class_name'),
                (method1_def_node, 'method_def'),
                (method1_name_node, 'method_name'),
                (method1_body_node, 'method_body'),
                (method2_def_node, 'method_def'),
                (method2_name_node, 'method_name'),
                (method2_body_node, 'method_body')
            ]
        elif 'method_invocation' in query_string:
            mock_query.captures.return_value = [
                (method_call_node, 'method_call'),
                (invoked_method_name_node, 'called_method')
            ]
        else:
            mock_query.captures.return_value = []
        return mock_query
    
    mock_language.query.side_effect = mock_query_side_effect
    mock_node.language = mock_language
    
    return mock_node


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
        diagramming_engine.generate_class_diagram({}, 'javascript')


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
    assert info['version'] == '1.1.0'
    assert info['current_format'] == 'plantuml'
    assert 'class_diagrams' in info['capabilities']
    assert 'sequence_diagrams' in info['capabilities']
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


def test_multiple_files_processing(diagramming_engine):
    """Test processing multiple code files."""
    # Mock multiple AST files
    mock_ast1 = Mock()
    mock_ast1.root_node = Mock(spec=Node)
    mock_ast1.root_node.language = Mock()
    mock_ast1.root_node.language.query.return_value.captures.return_value = []
    
    mock_ast2 = Mock()
    mock_ast2.root_node = Mock(spec=Node)
    mock_ast2.root_node.language = Mock()
    mock_ast2.root_node.language.query.return_value.captures.return_value = []
    
    code_files = {
        'file1.py': mock_ast1,
        'file2.py': mock_ast2
    }
    
    # Should not raise exception even with empty ASTs
    result = diagramming_engine.generate_class_diagram(code_files, 'python')
    assert '@startuml' in result
    assert '@enduml' in result


# ===== SEQUENCE DIAGRAM TESTS =====

def test_init_sequence_diagram_capabilities(diagramming_engine):
    """Test that DiagrammingEngine is initialized with sequence diagram capabilities."""
    assert diagramming_engine.max_sequence_depth == 3
    assert diagramming_engine.max_calls_per_function == 10
    assert 'java' in diagramming_engine.supported_languages
    
    engine_info = diagramming_engine.get_engine_info()
    assert 'sequence_diagrams' in engine_info['capabilities']
    assert 'function_call_tracing' in engine_info['capabilities']
    assert 'pr_change_focus' in engine_info['capabilities']
    assert engine_info['version'] == '1.1.0'


def test_extract_python_functions(diagramming_engine, mock_python_functions_ast):
    """Test extracting Python functions from AST."""
    functions = diagramming_engine._extract_python_functions(mock_python_functions_ast)
    
    assert len(functions) == 2
    
    # Check first function
    assert functions[0]['name'] == 'main_function'
    assert functions[0]['line'] == 1
    assert functions[0]['body'] is not None
    
    # Check second function
    assert functions[1]['name'] == 'helper_function'
    assert functions[1]['line'] == 6
    assert functions[1]['body'] is not None


def test_extract_java_methods(diagramming_engine, mock_java_methods_ast):
    """Test extracting Java methods from AST."""
    methods = diagramming_engine._extract_java_methods(mock_java_methods_ast)
    
    assert len(methods) == 2
    
    # Check first method
    assert methods[0]['name'] == 'mainMethod'
    assert methods[0]['class'] == 'TestClass'
    assert methods[0]['line'] == 1
    assert methods[0]['body'] is not None
    
    # Check second method
    assert methods[1]['name'] == 'helperMethod'
    assert methods[1]['class'] == 'TestClass'
    assert methods[1]['line'] == 11
    assert methods[1]['body'] is not None


def test_python_ast_to_sequence_data_no_changes(diagramming_engine, mock_python_functions_ast):
    """Test extracting Python sequence data without PR changes."""
    sequence_data_list = diagramming_engine._python_ast_to_sequence_data(mock_python_functions_ast)
    
    assert len(sequence_data_list) == 1
    sequence_data = sequence_data_list[0]
    
    assert sequence_data['language'] == 'python'
    assert len(sequence_data['participants']) >= 2
    assert 'main_function' in sequence_data['participants']
    assert 'helper_function' in sequence_data['participants']
    assert len(sequence_data['entry_points']) <= 3  # Limited to first 3 functions


def test_python_ast_to_sequence_data_with_changes(diagramming_engine, mock_python_functions_ast):
    """Test extracting Python sequence data with specific PR changes."""
    pr_changes = {
        'modified_functions': ['main_function'],
        'added_functions': []
    }
    
    sequence_data_list = diagramming_engine._python_ast_to_sequence_data(
        mock_python_functions_ast, pr_changes
    )
    
    assert len(sequence_data_list) == 1
    sequence_data = sequence_data_list[0]
    
    assert sequence_data['language'] == 'python'
    assert 'main_function' in sequence_data['entry_points']
    assert len(sequence_data['entry_points']) == 1  # Only the modified function


def test_java_ast_to_sequence_data_no_changes(diagramming_engine, mock_java_methods_ast):
    """Test extracting Java sequence data without PR changes."""
    sequence_data_list = diagramming_engine._java_ast_to_sequence_data(mock_java_methods_ast)
    
    assert len(sequence_data_list) == 1
    sequence_data = sequence_data_list[0]
    
    assert sequence_data['language'] == 'java'
    assert len(sequence_data['participants']) >= 2
    assert 'TestClass.mainMethod' in sequence_data['participants']
    assert 'TestClass.helperMethod' in sequence_data['participants']


def test_java_ast_to_sequence_data_with_changes(diagramming_engine, mock_java_methods_ast):
    """Test extracting Java sequence data with specific PR changes."""
    pr_changes = {
        'modified_methods': ['mainMethod'],
        'added_methods': []
    }
    
    sequence_data_list = diagramming_engine._java_ast_to_sequence_data(
        mock_java_methods_ast, pr_changes
    )
    
    assert len(sequence_data_list) == 1
    sequence_data = sequence_data_list[0]
    
    assert sequence_data['language'] == 'java'
    assert 'TestClass.mainMethod' in sequence_data['entry_points']
    assert len(sequence_data['entry_points']) == 1


def test_is_builtin_or_library_function(diagramming_engine):
    """Test built-in and library function detection."""
    # Python built-ins
    assert diagramming_engine._is_builtin_or_library_function('print') == True
    assert diagramming_engine._is_builtin_or_library_function('len') == True
    assert diagramming_engine._is_builtin_or_library_function('append') == True
    
    # Java built-ins
    assert diagramming_engine._is_builtin_or_library_function('println') == True
    assert diagramming_engine._is_builtin_or_library_function('toString') == True
    assert diagramming_engine._is_builtin_or_library_function('size') == True
    
    # Custom functions
    assert diagramming_engine._is_builtin_or_library_function('my_custom_function') == False
    assert diagramming_engine._is_builtin_or_library_function('calculateTotal') == False


def test_merge_sequence_data(diagramming_engine):
    """Test merging multiple sequence data structures."""
    sequence_data_list = [
        {
            'participants': ['func1', 'func2'],
            'interactions': [
                {'caller': 'func1', 'callee': 'func2', 'type': 'function_call'}
            ],
            'entry_points': ['func1'],
            'language': 'python'
        },
        {
            'participants': ['func2', 'func3'],
            'interactions': [
                {'caller': 'func2', 'callee': 'func3', 'type': 'function_call'}
            ],
            'entry_points': ['func2'],
            'language': 'python'
        }
    ]
    
    merged = diagramming_engine._merge_sequence_data(sequence_data_list)
    
    assert len(merged['participants']) == 3
    assert 'func1' in merged['participants']
    assert 'func2' in merged['participants']
    assert 'func3' in merged['participants']
    
    assert len(merged['interactions']) == 2
    assert merged['language'] == 'python'
    assert len(merged['entry_points']) == 2


def test_generate_plantuml_sequence_diagram(diagramming_engine):
    """Test generating PlantUML sequence diagram."""
    sequence_data = {
        'participants': ['main_function', 'helper_function'],
        'interactions': [
            {
                'caller': 'main_function',
                'callee': 'helper_function',
                'type': 'function_call',
                'line': 3
            }
        ],
        'entry_points': ['main_function'],
        'language': 'python'
    }
    
    diagram = diagramming_engine._generate_plantuml_sequence_diagram(sequence_data)
    
    assert '@startuml' in diagram
    assert '@enduml' in diagram
    assert 'title Python Sequence Diagram' in diagram
    assert 'participant "main_function" as main_function' in diagram
    assert 'participant "helper_function" as helper_function' in diagram
    assert 'main_function -> helper_function: function_call' in diagram
    assert 'Entry point: main_function' in diagram


def test_generate_mermaid_sequence_diagram(diagramming_engine):
    """Test generating Mermaid.js sequence diagram."""
    sequence_data = {
        'participants': ['TestClass.mainMethod', 'TestClass.helperMethod'],
        'interactions': [
            {
                'caller': 'TestClass.mainMethod',
                'callee': 'TestClass.helperMethod',
                'type': 'method_call',
                'line': 5
            }
        ],
        'entry_points': ['TestClass.mainMethod'],
        'language': 'java'
    }
    
    diagram = diagramming_engine._generate_mermaid_sequence_diagram(sequence_data)
    
    assert 'sequenceDiagram' in diagram
    assert 'title Java Sequence Diagram' in diagram
    assert 'participant TestClass_mainMethod as TestClass.mainMethod' in diagram
    assert 'participant TestClass_helperMethod as TestClass.helperMethod' in diagram
    assert 'TestClass_mainMethod ->> TestClass_helperMethod: method_call' in diagram
    assert 'note over TestClass_mainMethod: Entry point' in diagram


def test_generate_sequence_diagram_python_plantuml(diagramming_engine, mock_python_functions_ast):
    """Test generating complete Python sequence diagram in PlantUML format."""
    mock_ast = Mock()
    mock_ast.root_node = mock_python_functions_ast
    
    code_files = {'test.py': mock_ast}
    pr_changes = {'modified_functions': ['main_function']}
    
    diagram = diagramming_engine.generate_sequence_diagram(code_files, 'python', pr_changes)
    
    assert '@startuml' in diagram
    assert '@enduml' in diagram
    assert 'Python Sequence Diagram' in diagram
    assert 'participant' in diagram


def test_generate_sequence_diagram_java_mermaid(mermaid_engine, mock_java_methods_ast):
    """Test generating complete Java sequence diagram in Mermaid format."""
    mock_ast = Mock()
    mock_ast.root_node = mock_java_methods_ast
    
    code_files = {'Test.java': mock_ast}
    pr_changes = {'modified_methods': ['mainMethod']}
    
    diagram = mermaid_engine.generate_sequence_diagram(code_files, 'java', pr_changes)
    
    assert 'sequenceDiagram' in diagram
    assert 'Java Sequence Diagram' in diagram
    assert 'participant' in diagram


def test_generate_sequence_diagram_unsupported_language(diagramming_engine):
    """Test generating sequence diagram with unsupported language."""
    code_files = {'test.js': Mock()}
    
    with pytest.raises(ValueError, match="Unsupported language for sequence diagrams"):
        diagramming_engine.generate_sequence_diagram(code_files, 'javascript')


def test_generate_sequence_diagram_error_handling(diagramming_engine):
    """Test sequence diagram generation error handling."""
    # Mock code files that will cause an error in merge_sequence_data
    mock_ast = Mock()
    mock_ast.root_node = Mock()
    
    code_files = {'test.py': mock_ast}
    
    # Mock the _python_ast_to_sequence_data to raise an exception
    with patch.object(diagramming_engine, '_python_ast_to_sequence_data') as mock_extract:
        mock_extract.side_effect = Exception("Test sequence error")
        
        diagram = diagramming_engine.generate_sequence_diagram(code_files, 'python')
        
        # Should return error diagram instead of raising exception
        assert '@startuml' in diagram
        assert 'Error generating sequence diagram' in diagram
        assert 'Test sequence error' in diagram
        assert '@enduml' in diagram


def test_sequence_diagram_empty_interactions(diagramming_engine):
    """Test sequence diagram generation with no function calls."""
    sequence_data = {
        'participants': ['lone_function'],
        'interactions': [],  # No interactions
        'entry_points': ['lone_function'],
        'language': 'python'
    }
    
    diagram = diagramming_engine._generate_plantuml_sequence_diagram(sequence_data)
    
    assert '@startuml' in diagram
    assert '@enduml' in diagram
    assert 'No function/method calls found' in diagram


def test_sequence_diagram_mermaid_empty_interactions(diagramming_engine):
    """Test Mermaid sequence diagram generation with no method calls."""
    sequence_data = {
        'participants': ['TestClass.loneMethod'],
        'interactions': [],  # No interactions
        'entry_points': ['TestClass.loneMethod'],
        'language': 'java'
    }
    
    diagram = diagramming_engine._generate_mermaid_sequence_diagram(sequence_data)
    
    assert 'sequenceDiagram' in diagram
    assert 'No function/method calls found' in diagram


def test_trace_python_function_calls_depth_limit(diagramming_engine):
    """Test that function call tracing respects depth limits."""
    # Create a mock function that would cause infinite recursion
    mock_function = {
        'name': 'recursive_func',
        'body': Mock(spec=Node)
    }
    
    mock_language = Mock()
    mock_query = Mock()
    mock_query.captures.return_value = [
        (Mock(spec=Node, text=b'recursive_func'), 'called_func')
    ]
    mock_language.query.return_value = mock_query
    mock_function['body'].language = mock_language
    
    all_functions = [mock_function]
    
    # Should stop at max depth and not cause infinite recursion
    interactions = diagramming_engine._trace_python_function_calls(
        mock_function, all_functions, depth=0, visited=set()
    )
    
    # Should have limited interactions due to depth limit
    assert len(interactions) <= diagramming_engine.max_sequence_depth * diagramming_engine.max_calls_per_function


def test_trace_java_method_calls_visited_prevention(diagramming_engine):
    """Test that Java method call tracing prevents cycles."""
    # Create mock method
    mock_method = {
        'name': 'testMethod',
        'class': 'TestClass',
        'body': Mock(spec=Node)
    }
    
    mock_language = Mock()
    mock_query = Mock()
    mock_query.captures.return_value = []  # No method calls
    mock_language.query.return_value = mock_query
    mock_method['body'].language = mock_language
    
    all_methods = [mock_method]
    visited = {'TestClass.testMethod'}  # Already visited
    
    # Should return empty interactions due to already visited
    interactions = diagramming_engine._trace_java_method_calls(
        mock_method, all_methods, depth=0, visited=visited
    )
    
    assert len(interactions) == 0


# Tests for Kotlin and XML support
@pytest.fixture
def mock_kotlin_functions_ast():
    """Create a mock AST node with Kotlin functions for testing."""
    mock_node = Mock(spec=Node)
    mock_language = Mock()
    
    # Mock class node
    class_name_node = Mock(spec=Node)
    class_name_node.text = b'MainActivity'
    class_name_node.type = 'simple_identifier'
    
    # Mock function 1: onCreate
    func1_name_node = Mock(spec=Node)
    func1_name_node.text = b'onCreate'
    func1_name_node.type = 'simple_identifier'
    func1_name_node.start_point = (0, 0)
    
    func1_body_node = Mock(spec=Node)
    func1_body_node.type = 'function_body'
    func1_body_node.language = mock_language
    
    func1_def_node = Mock(spec=Node)
    func1_def_node.type = 'function_declaration'
    func1_def_node.children = [func1_name_node, func1_body_node]
    func1_def_node.start_point = (0, 0)
    
    # Mock function 2: setupView
    func2_name_node = Mock(spec=Node)
    func2_name_node.text = b'setupView'
    func2_name_node.type = 'simple_identifier'
    func2_name_node.start_point = (8, 4)
    
    func2_body_node = Mock(spec=Node)
    func2_body_node.type = 'function_body'
    func2_body_node.language = mock_language
    
    func2_def_node = Mock(spec=Node)
    func2_def_node.type = 'function_declaration'
    func2_def_node.children = [func2_name_node, func2_body_node]
    func2_def_node.start_point = (8, 4)
    
    # Mock class declaration
    class_def_node = Mock(spec=Node)
    class_def_node.type = 'class_declaration'
    class_def_node.children = [class_name_node]
    
    # Mock function call in onCreate
    call_func_name_node = Mock(spec=Node)
    call_func_name_node.text = b'setupView'
    call_func_name_node.type = 'simple_identifier'
    
    call_expr_node = Mock(spec=Node)
    call_expr_node.type = 'call_expression'
    call_expr_node.children = [call_func_name_node]
    
    # Setup query side effects
    def mock_query_side_effect(query_string):
        mock_query = Mock()
        if 'function_declaration' in query_string:
            mock_query.captures.return_value = [
                (func1_def_node, 'func_def'),
                (func2_def_node, 'func_def')
            ]
        elif 'call_expression' in query_string:
            mock_query.captures.return_value = [
                (call_expr_node, 'call_expr')
            ]
        elif 'class_declaration' in query_string:
            mock_query.captures.return_value = [
                (class_def_node, 'class_def')
            ]
        else:
            mock_query.captures.return_value = []
        return mock_query
    
    mock_language.query.side_effect = mock_query_side_effect
    mock_node.language = mock_language
    
    return mock_node


@pytest.fixture
def mock_xml_elements_ast():
    """Create a mock AST node with XML elements for testing."""
    mock_node = Mock(spec=Node)
    mock_language = Mock()
    
    # Mock root LinearLayout element
    element_name_node = Mock(spec=Node)
    element_name_node.text = b'LinearLayout'
    element_name_node.type = 'element_name'
    
    start_tag_node = Mock(spec=Node)
    start_tag_node.type = 'start_tag'
    start_tag_node.children = [element_name_node]
    
    element_node = Mock(spec=Node)
    element_node.type = 'element'
    element_node.start_point = (0, 0)
    element_node.children = [start_tag_node]
    
    # Mock attribute
    attr_name_node = Mock(spec=Node)
    attr_name_node.text = b'android:layout_width'
    attr_name_node.type = 'attribute_name'
    
    attr_value_node = Mock(spec=Node)
    attr_value_node.text = b'"match_parent"'
    attr_value_node.type = 'attribute_value'
    
    attribute_node = Mock(spec=Node)
    attribute_node.type = 'attribute'
    attribute_node.start_point = (1, 4)
    attribute_node.children = [attr_name_node, attr_value_node]
    
    # Setup query side effects
    def mock_query_side_effect(query_string):
        mock_query = Mock()
        if 'element' in query_string:
            mock_query.captures.return_value = [
                (element_node, 'element')
            ]
        elif 'attribute' in query_string:
            mock_query.captures.return_value = [
                (attribute_node, 'attribute')
            ]
        else:
            mock_query.captures.return_value = []
        return mock_query
    
    mock_language.query.side_effect = mock_query_side_effect
    mock_node.language = mock_language
    
    return mock_node


def test_kotlin_language_support(diagramming_engine):
    """Test that Kotlin is included in supported languages."""
    assert 'kotlin' in diagramming_engine.get_supported_languages()


def test_xml_language_support(diagramming_engine):
    """Test that XML is included in supported languages."""
    assert 'xml' in diagramming_engine.get_supported_languages()


def test_kotlin_ast_to_class_data(diagramming_engine, mock_kotlin_functions_ast):
    """Test extracting class data from Kotlin AST."""
    with patch.object(diagramming_engine, '_extract_kotlin_class_data') as mock_extract:
        mock_extract.return_value = {
            'type': 'class',
            'name': 'MainActivity',
            'line': 1,
            'access_modifier': 'public',
            'methods': [
                {'name': 'onCreate', 'access_modifier': 'public', 'parameters': ['Bundle']},
                {'name': 'setupView', 'access_modifier': 'private', 'parameters': []}
            ],
            'properties': []
        }
        
        result = diagramming_engine._kotlin_ast_to_class_data(mock_kotlin_functions_ast)
        
        assert isinstance(result, list)
        mock_extract.assert_called()


def test_xml_ast_to_class_data(diagramming_engine, mock_xml_elements_ast):
    """Test extracting class data from XML AST."""
    with patch.object(diagramming_engine, '_extract_xml_element_data') as mock_extract:
        mock_extract.return_value = {
            'type': 'element',
            'name': 'LinearLayout',
            'line': 1,
            'depth': 0,
            'attributes': [
                {'name': 'android:layout_width', 'value': 'match_parent'}
            ]
        }
        
        result = diagramming_engine._xml_ast_to_class_data(mock_xml_elements_ast)
        
        assert isinstance(result, list)
        mock_extract.assert_called()


def test_extract_kotlin_class_data(diagramming_engine):
    """Test extracting Kotlin class information."""
    # Mock class node
    class_name_node = Mock(spec=Node)
    class_name_node.text = b'MainActivity'
    class_name_node.type = 'simple_identifier'
    
    class_body_node = Mock(spec=Node)
    class_body_node.type = 'class_body'
    class_body_node.children = []
    
    class_node = Mock(spec=Node)
    class_node.type = 'class_declaration'
    class_node.start_point = (0, 0)
    class_node.children = [class_name_node, class_body_node]
    
    with patch.object(diagramming_engine, '_extract_kotlin_class_members') as mock_members:
        mock_members.return_value = ([], [])  # methods, properties
        
        result = diagramming_engine._extract_kotlin_class_data(class_node)
        
        assert result is not None
        assert result['name'] == 'MainActivity'
        assert result['type'] == 'class'
        assert result['line'] == 1
        mock_members.assert_called_once()


def test_extract_kotlin_function_data(diagramming_engine):
    """Test extracting Kotlin function information."""
    # Mock function node
    func_name_node = Mock(spec=Node)
    func_name_node.text = b'onCreate'
    func_name_node.type = 'simple_identifier'
    
    param_node = Mock(spec=Node)
    param_node.text = b'savedInstanceState'
    param_node.type = 'value_parameter'
    
    params_node = Mock(spec=Node)
    params_node.type = 'value_parameters'
    params_node.children = [param_node]
    
    function_node = Mock(spec=Node)
    function_node.type = 'function_declaration'
    function_node.start_point = (5, 4)
    function_node.children = [func_name_node, params_node]
    
    with patch.object(diagramming_engine, '_extract_kotlin_parameters') as mock_params:
        mock_params.return_value = ['Bundle?']
        
        result = diagramming_engine._extract_kotlin_function_data(function_node)
        
        assert result is not None
        assert result['name'] == 'onCreate'
        assert result['line'] == 6
        assert result['parameters'] == ['Bundle?']
        mock_params.assert_called_once()


def test_extract_kotlin_property_data(diagramming_engine):
    """Test extracting Kotlin property information."""
    # Mock property node
    prop_name_node = Mock(spec=Node)
    prop_name_node.text = b'binding'
    prop_name_node.type = 'simple_identifier'
    
    property_node = Mock(spec=Node)
    property_node.type = 'property_declaration'
    property_node.start_point = (3, 4)
    property_node.children = [prop_name_node]
    
    result = diagramming_engine._extract_kotlin_property_data(property_node)
    
    assert result is not None
    assert result['name'] == 'binding'
    assert result['line'] == 4


def test_extract_xml_element_data(diagramming_engine):
    """Test extracting XML element information."""
    # Mock element node
    element_name_node = Mock(spec=Node)
    element_name_node.text = b'LinearLayout'
    element_name_node.type = 'element_name'
    
    start_tag_node = Mock(spec=Node)
    start_tag_node.type = 'start_tag'
    start_tag_node.children = [element_name_node]
    
    element_node = Mock(spec=Node)
    element_node.type = 'element'
    element_node.start_point = (2, 0)
    element_node.children = [start_tag_node]
    
    result = diagramming_engine._extract_xml_element_data(element_node, depth=0)
    
    assert result is not None
    assert result['name'] == 'LinearLayout'
    assert result['type'] == 'element'
    assert result['line'] == 3
    assert result['depth'] == 0


def test_extract_xml_attribute_data(diagramming_engine):
    """Test extracting XML attribute information."""
    # Mock attribute node
    attr_name_node = Mock(spec=Node)
    attr_name_node.text = b'android:layout_width'
    attr_name_node.type = 'attribute_name'
    
    attr_value_node = Mock(spec=Node)
    attr_value_node.text = b'"wrap_content"'
    attr_value_node.type = 'attribute_value'
    
    attribute_node = Mock(spec=Node)
    attribute_node.type = 'attribute'
    attribute_node.start_point = (1, 4)
    attribute_node.children = [attr_name_node, attr_value_node]
    
    result = diagramming_engine._extract_xml_attribute_data(attribute_node)
    
    assert result is not None
    assert result['name'] == 'android:layout_width'
    assert result['value'] == 'wrap_content'
    assert result['line'] == 2


def test_generate_class_diagram_kotlin(diagramming_engine, mock_kotlin_functions_ast):
    """Test generating class diagram for Kotlin code."""
    code_files = {'MainActivity.kt': mock_kotlin_functions_ast}
    
    with patch.object(diagramming_engine, '_kotlin_ast_to_class_data') as mock_kotlin_data:
        mock_kotlin_data.return_value = [
            {
                'type': 'class',
                'name': 'MainActivity',
                'line': 1,
                'access_modifier': 'public',
                'methods': [
                    {'name': 'onCreate', 'access_modifier': 'public', 'parameters': ['Bundle']}
                ],
                'properties': [
                    {'name': 'binding', 'access_modifier': 'private'}
                ]
            }
        ]
        
        result = diagramming_engine.generate_class_diagram(code_files, 'kotlin')
        
        assert '@startuml' in result
        assert '@enduml' in result
        assert 'class MainActivity' in result
        assert 'onCreate' in result
        assert 'binding' in result
        mock_kotlin_data.assert_called_once()


def test_generate_class_diagram_xml(diagramming_engine, mock_xml_elements_ast):
    """Test generating class diagram for XML code."""
    code_files = {'activity_main.xml': mock_xml_elements_ast}
    
    with patch.object(diagramming_engine, '_xml_ast_to_class_data') as mock_xml_data:
        mock_xml_data.return_value = [
            {
                'type': 'element',
                'name': 'LinearLayout',
                'line': 1,
                'depth': 0,
                'attributes': [
                    {'name': 'android:layout_width', 'value': 'match_parent'}
                ]
            }
        ]
        
        result = diagramming_engine.generate_class_diagram(code_files, 'xml')
        
        assert '@startuml' in result
        assert '@enduml' in result
        assert 'LinearLayout' in result
        mock_xml_data.assert_called_once()


def test_kotlin_ast_to_sequence_data(diagramming_engine, mock_kotlin_functions_ast):
    """Test extracting sequence data from Kotlin AST."""
    with patch.object(diagramming_engine, '_extract_kotlin_functions') as mock_extract_funcs, \
         patch.object(diagramming_engine, '_trace_kotlin_function_calls') as mock_trace:
        
        mock_extract_funcs.return_value = [
            {'name': 'onCreate', 'class': 'MainActivity', 'body_node': Mock(), 'line': 1},
            {'name': 'setupView', 'class': 'MainActivity', 'body_node': Mock(), 'line': 8}
        ]
        
        mock_trace.return_value = [
            {'caller': 'MainActivity.onCreate', 'callee': 'MainActivity.setupView', 'type': 'function_call'}
        ]
        
        result = diagramming_engine._kotlin_ast_to_sequence_data(mock_kotlin_functions_ast)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['language'] == 'kotlin'
        assert 'participants' in result[0]
        assert 'interactions' in result[0]
        mock_extract_funcs.assert_called_once()


def test_extract_kotlin_functions(diagramming_engine, mock_kotlin_functions_ast):
    """Test extracting Kotlin functions for sequence analysis."""
    with patch.object(diagramming_engine, '_extract_kotlin_function_for_sequence') as mock_extract:
        mock_extract.side_effect = [
            {'name': 'onCreate', 'class': 'MainActivity', 'body_node': Mock(), 'line': 1},
            {'name': 'setupView', 'class': 'MainActivity', 'body_node': Mock(), 'line': 8}
        ]
        
        result = diagramming_engine._extract_kotlin_functions(mock_kotlin_functions_ast)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]['name'] == 'onCreate'
        assert result[1]['name'] == 'setupView'


def test_extract_kotlin_function_for_sequence(diagramming_engine):
    """Test extracting Kotlin function for sequence analysis."""
    # Mock function node
    func_name_node = Mock(spec=Node)
    func_name_node.text = b'onCreate'
    func_name_node.type = 'simple_identifier'
    
    func_body_node = Mock(spec=Node)
    func_body_node.type = 'function_body'
    
    function_node = Mock(spec=Node)
    function_node.type = 'function_declaration'
    function_node.start_point = (5, 0)
    function_node.children = [func_name_node, func_body_node]
    
    result = diagramming_engine._extract_kotlin_function_for_sequence(function_node, 'MainActivity')
    
    assert result is not None
    assert result['name'] == 'onCreate'
    assert result['class'] == 'MainActivity'
    assert result['line'] == 6
    assert result['body_node'] == func_body_node


def test_extract_kotlin_call_target(diagramming_engine):
    """Test extracting Kotlin call target from call expression."""
    # Mock simple call
    func_name_node = Mock(spec=Node)
    func_name_node.text = b'setupView'
    func_name_node.type = 'simple_identifier'
    
    call_node = Mock(spec=Node)
    call_node.type = 'call_expression'
    call_node.children = [func_name_node]
    
    result = diagramming_engine._extract_kotlin_call_target(call_node)
    
    assert result == 'setupView'


def test_generate_sequence_diagram_kotlin(diagramming_engine, mock_kotlin_functions_ast):
    """Test generating sequence diagram for Kotlin code."""
    code_files = {'MainActivity.kt': mock_kotlin_functions_ast}
    
    with patch.object(diagramming_engine, '_kotlin_ast_to_sequence_data') as mock_sequence_data:
        mock_sequence_data.return_value = [
            {
                'participants': ['MainActivity.onCreate', 'MainActivity.setupView'],
                'interactions': [
                    {'caller': 'MainActivity.onCreate', 'callee': 'MainActivity.setupView', 'type': 'function_call'}
                ],
                'entry_points': ['onCreate'],
                'language': 'kotlin'
            }
        ]
        
        result = diagramming_engine.generate_sequence_diagram(code_files, 'kotlin')
        
        assert '@startuml' in result
        assert '@enduml' in result
        assert 'Kotlin Sequence Diagram' in result
        assert 'MainActivity_onCreate' in result
        assert 'MainActivity_setupView' in result
        mock_sequence_data.assert_called_once()


def test_engine_info_updated_for_kotlin_xml(diagramming_engine):
    """Test that engine info reflects Kotlin and XML support."""
    info = diagramming_engine.get_engine_info()
    
    assert info['version'] == '1.2.0'
    assert 'kotlin' in info['supported_languages']
    assert 'xml' in info['supported_languages']
    assert 'kotlin_support' in info['capabilities']
    assert 'android_xml_support' in info['capabilities'] 