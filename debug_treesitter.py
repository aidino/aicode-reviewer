#!/usr/bin/env python3
"""Debug script to check Tree-sitter query capture format."""

import tree_sitter
from tree_sitter import Language, Parser

# Try to load Python language
try:
    import tree_sitter_python as tspython
    PY_LANGUAGE = Language(tspython.language())
    print(f"Successfully loaded Python language: {PY_LANGUAGE}")
except Exception as e:
    print(f"Could not load Python language: {e}")
    exit(1)

# Create parser
parser = Parser(PY_LANGUAGE)

# Sample Python code
sample_code = """
import pdb

def test_function():
    print("Hello World")
    pdb.set_trace()
    return True
"""

# Parse code
tree = parser.parse(bytes(sample_code, "utf8"))
root_node = tree.root_node

print("=== Tree-sitter Query Debug ===")
print(f"Root node type: {root_node.type}")
print(f"Code:\n{sample_code}")

# Test pdb query
pdb_query_string = """
(call
  function: (attribute
    object: (identifier) @obj
    attribute: (identifier) @attr)
  arguments: (argument_list)) @call
(#eq? @obj "pdb")
(#eq? @attr "set_trace")
"""

print("\n=== PDB Query Test ===")
try:
    query = PY_LANGUAGE.query(pdb_query_string)
    captures = query.captures(root_node)
    print(f"Captures type: {type(captures)}")
    print(f"Captures content: {captures}")
    
    # Access captured nodes by name
    if 'call' in captures:
        print(f"Call nodes: {captures['call']}")
        for node in captures['call']:
            print(f"  Call node: {node}, start: {node.start_point}")
    
    if 'obj' in captures:
        print(f"Obj nodes: {captures['obj']}")
    
    if 'attr' in captures:
        print(f"Attr nodes: {captures['attr']}")
        
except Exception as e:
    print(f"PDB Query error: {e}")

# Test print query
print_query_string = """
(call
  function: (identifier) @func
  arguments: (argument_list)) @call
(#eq? @func "print")
"""

print("\n=== Print Query Test ===")
try:
    query = PY_LANGUAGE.query(print_query_string)
    captures = query.captures(root_node)
    print(f"Captures type: {type(captures)}")
    print(f"Captures content: {captures}")
    
    # Access captured nodes by name
    if 'call' in captures:
        print(f"Call nodes: {captures['call']}")
        for node in captures['call']:
            print(f"  Call node: {node}, start: {node.start_point}")
    
    if 'func' in captures:
        print(f"Func nodes: {captures['func']}")
        for node in captures['func']:
            print(f"  Func node: {node}, text: {node.text}")
        
except Exception as e:
    print(f"Print Query error: {e}")

print("\n=== Done ===") 