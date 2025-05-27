# Schema cho knowledge graph codebase
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel

class NodeType(str, Enum):
    FILE = "File"
    CLASS = "Class" 
    METHOD = "Method"
    FUNCTION = "Function"
    VARIABLE = "Variable"
    MODULE = "Module"
    PACKAGE = "Package"

class EdgeType(str, Enum):
    CONTAINS = "CONTAINS"  # Package contains modules, files contain classes
    IMPORTS = "IMPORTS"    # Module imports another module
    CALLS = "CALLS"       # Method/function calls another method/function
    INHERITS = "INHERITS" # Class inherits from another class
    IMPLEMENTS = "IMPLEMENTS" # Class implements interface
    USES = "USES"         # Method uses variable/class
    RETURNS = "RETURNS"   # Method returns type
    DEPENDS = "DEPENDS"   # File/module depends on another

class CodeNode(BaseModel):
    """Base model for all nodes in the code knowledge graph"""
    id: str  # Unique identifier 
    type: NodeType
    name: str
    file_path: Optional[str] = None
    language: Optional[str] = None
    properties: Dict[str, str] = {}
    vector_id: Optional[str] = None  # Reference to vector store embedding

class CodeEdge(BaseModel):
    """Represents relationships between code nodes"""
    source_id: str
    target_id: str
    type: EdgeType
    properties: Dict[str, str] = {}

class CodeGraph(BaseModel):
    """Represents the entire code knowledge graph"""
    nodes: List[CodeNode]
    edges: List[CodeEdge]

# Cypher query templates
CYPHER_QUERIES = {
    # Find all classes that inherit from a given class
    'find_inheritors': '''
    MATCH (c:Class)-[:INHERITS]->(parent:Class {name: $parent_name})
    RETURN c
    ''',
    
    # Find all usages of a class/method
    'find_usages': '''
    MATCH (n)-[:USES]->(target {name: $target_name})
    RETURN n
    ''',
    
    # Find call hierarchy for a method
    'find_call_hierarchy': '''
    MATCH path = (caller)-[:CALLS*1..3]->(callee {name: $method_name})
    RETURN path
    ''',
    
    # Find dependencies for a file
    'find_dependencies': '''
    MATCH path = (f:File {name: $file_name})-[:DEPENDS*1..2]->(dep:File)
    RETURN path
    ''',
    
    # Find related components based on multiple relationship types
    'find_related': '''
    MATCH path = (start {name: $name})-[:CALLS|USES|DEPENDS*1..2]-(related)
    RETURN path
    '''
} 