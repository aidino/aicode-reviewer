from typing import Dict, List, Optional, Any
from neo4j import GraphDatabase
from pydantic_settings import BaseSettings

from .schema import CodeNode, CodeEdge, CodeGraph, CYPHER_QUERIES

class Neo4jSettings(BaseSettings):
    """Neo4j connection settings"""
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    class Config:
        env_file = ".env"

class Neo4jClient:
    def __init__(self, settings: Optional[Neo4jSettings] = None):
        """Initialize Neo4j client with optional custom settings"""
        self.settings = settings or Neo4jSettings()
        self.driver = GraphDatabase.driver(
            self.settings.NEO4J_URI,
            auth=(self.settings.NEO4J_USER, self.settings.NEO4J_PASSWORD)
        )

    def close(self):
        """Close the database connection"""
        self.driver.close()

    def create_node(self, node: CodeNode) -> str:
        """Create a node in the graph and return its ID"""
        with self.driver.session() as session:
            result = session.write_transaction(self._create_node_tx, node)
            return result

    def create_edge(self, edge: CodeEdge):
        """Create an edge between two nodes"""
        with self.driver.session() as session:
            session.write_transaction(self._create_edge_tx, edge)

    def create_graph(self, graph: CodeGraph):
        """Create multiple nodes and edges in batch"""
        with self.driver.session() as session:
            session.write_transaction(self._create_graph_tx, graph)

    def find_inheritors(self, class_name: str) -> List[CodeNode]:
        """Find all classes that inherit from a given class"""
        with self.driver.session() as session:
            result = session.read_transaction(
                self._run_query_tx,
                CYPHER_QUERIES['find_inheritors'],
                {'parent_name': class_name}
            )
            return [CodeNode(**record['c']) for record in result]

    def find_usages(self, target_name: str) -> List[CodeNode]:
        """Find all usages of a class/method"""
        with self.driver.session() as session:
            result = session.read_transaction(
                self._run_query_tx,
                CYPHER_QUERIES['find_usages'],
                {'target_name': target_name}
            )
            return [CodeNode(**record['n']) for record in result]

    def find_call_hierarchy(self, method_name: str) -> List[Dict[str, Any]]:
        """Find call hierarchy for a method"""
        with self.driver.session() as session:
            result = session.read_transaction(
                self._run_query_tx,
                CYPHER_QUERIES['find_call_hierarchy'],
                {'method_name': method_name}
            )
            return [self._path_to_dict(record['path']) for record in result]

    def find_dependencies(self, file_name: str) -> List[Dict[str, Any]]:
        """Find dependencies for a file"""
        with self.driver.session() as session:
            result = session.read_transaction(
                self._run_query_tx,
                CYPHER_QUERIES['find_dependencies'],
                {'file_name': file_name}
            )
            return [self._path_to_dict(record['path']) for record in result]

    def find_related(self, name: str, max_distance: int = 2) -> List[Dict[str, Any]]:
        """Find related components based on multiple relationship types"""
        with self.driver.session() as session:
            result = session.read_transaction(
                self._run_query_tx,
                CYPHER_QUERIES['find_related'],
                {'name': name}
            )
            return [self._path_to_dict(record['path']) for record in result]

    @staticmethod
    def _create_node_tx(tx, node: CodeNode) -> str:
        """Create node transaction"""
        query = (
            f"CREATE (n:{node.type} $props) "
            "RETURN id(n) as node_id"
        )
        result = tx.run(query, props=node.dict())
        return result.single()["node_id"]

    @staticmethod
    def _create_edge_tx(tx, edge: CodeEdge):
        """Create edge transaction"""
        query = (
            "MATCH (source), (target) "
            f"WHERE id(source) = $source_id AND id(target) = $target_id "
            f"CREATE (source)-[r:{edge.type} $props]->(target)"
        )
        tx.run(query, edge.dict())

    @staticmethod
    def _create_graph_tx(tx, graph: CodeGraph):
        """Create multiple nodes and edges transaction"""
        # Create nodes
        for node in graph.nodes:
            query = (
                f"CREATE (n:{node.type} $props) "
                "RETURN id(n) as node_id"
            )
            tx.run(query, props=node.dict())

        # Create edges
        for edge in graph.edges:
            query = (
                "MATCH (source), (target) "
                f"WHERE id(source) = $source_id AND id(target) = $target_id "
                f"CREATE (source)-[r:{edge.type} $props]->(target)"
            )
            tx.run(query, edge.dict())

    @staticmethod
    def _run_query_tx(tx, query: str, params: Dict[str, Any]):
        """Run a Cypher query transaction"""
        return list(tx.run(query, params))

    @staticmethod
    def _path_to_dict(path) -> Dict[str, Any]:
        """Convert Neo4j path to dictionary"""
        return {
            'nodes': [dict(node) for node in path.nodes],
            'relationships': [dict(rel) for rel in path.relationships]
        } 