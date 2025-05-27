"""Unit tests for RAGContextAgent."""

import os
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from qdrant_client.http.models import Distance, VectorParams, CollectionsResponse, CollectionDescription
from sentence_transformers import SentenceTransformer

from src.core_engine.agents.rag_context_agent import RAGContextAgent, RAGContext
from src.core_engine.agents.knowledge_graph.schema import CodeNode, CodeGraph

@pytest.fixture
def mock_collections_response():
    """Mock collections response for testing."""
    collections_response = Mock(spec=CollectionsResponse)
    collections_response.collections = []
    return collections_response

@pytest.fixture
def mock_qdrant_client(mock_collections_response):
    """Mock Qdrant client for testing."""
    with patch('src.core_engine.agents.rag_context_agent.QdrantClient') as mock:
        client = Mock()
        
        # Mock get_collections response
        client.get_collections.return_value = mock_collections_response
        
        # Mock search response
        mock_hit = Mock()
        mock_hit.payload = {
            'content': 'def test():',
            'file_path': 'test.py',
            'chunk_index': 0
        }
        mock_hit.score = 0.95
        client.search.return_value = [mock_hit]
        
        mock.return_value = client
        yield client

@pytest.fixture
def mock_sentence_transformer():
    """Mock sentence transformer for testing."""
    with patch('src.core_engine.agents.rag_context_agent.SentenceTransformer') as mock:
        model = Mock()
        model.get_sentence_embedding_dimension.return_value = 384  # Common dimension
        model.encode.return_value = np.array([[0.1] * 384])  # Mock embeddings as numpy array
        mock.return_value = model
        yield model

@pytest.fixture
def mock_code_splitter():
    """Mock LlamaIndex CodeSplitter for testing."""
    with patch('src.core_engine.agents.rag_context_agent.CodeSplitter') as mock:
        splitter = Mock()
        mock_chunk = Mock()
        mock_chunk.text = "def test():"
        splitter.split_text.return_value = [mock_chunk]
        mock.return_value = splitter
        yield splitter

@pytest.fixture
def mock_neo4j_client():
    return Mock()

@pytest.fixture
def mock_vector_store():
    return Mock()

@pytest.fixture
def mock_embeddings():
    return Mock()

@pytest.fixture
def rag_agent(mock_qdrant_client, mock_sentence_transformer, mock_code_splitter, mock_neo4j_client, mock_vector_store, mock_embeddings):
    """Create RAGContextAgent with mocked dependencies."""
    with patch('src.core_engine.agents.rag_context_agent.Chroma', return_value=mock_vector_store):
        agent = RAGContextAgent(
            vector_store_path="./test_vector_store",
            embeddings_model=mock_embeddings,
            neo4j_client=mock_neo4j_client
        )
        yield agent

def test_init_with_defaults(mock_qdrant_client, mock_sentence_transformer, mock_code_splitter):
    """Test RAGContextAgent initialization with default values."""
    agent = RAGContextAgent()
    
    assert agent.collection_name == "project_kb"
    assert agent.qdrant_url == "http://localhost:6333"
    assert agent.qdrant_api_key is None
    assert agent.vector_size == 384

def test_init_with_custom_values(mock_qdrant_client, mock_sentence_transformer, mock_code_splitter):
    """Test RAGContextAgent initialization with custom values."""
    agent = RAGContextAgent(
        collection_name="custom_kb",
        qdrant_url="http://custom:6333",
        qdrant_api_key="test_key"
    )
    
    assert agent.collection_name == "custom_kb"
    assert agent.qdrant_url == "http://custom:6333"
    assert agent.qdrant_api_key == "test_key"

def test_create_collection_if_not_exists_new(mock_collections_response, mock_qdrant_client):
    """Test collection creation when it doesn't exist."""
    # Mock empty collections list
    mock_collections_response.collections = []
    
    agent = RAGContextAgent()
    
    mock_qdrant_client.create_collection.assert_called_once_with(
        collection_name="project_kb",
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )

def test_create_collection_if_not_exists_existing(mock_collections_response, mock_qdrant_client):
    """Test collection creation when it already exists."""
    # Mock existing collection
    mock_collection = Mock(spec=CollectionDescription)
    mock_collection.name = "project_kb"
    mock_collections_response.collections = [mock_collection]
    
    agent = RAGContextAgent()
    
    mock_qdrant_client.create_collection.assert_not_called()

def test_chunk_code_with_function(rag_agent, mock_code_splitter):
    """Test code chunking with a Python function."""
    code = """def example_function(param1: str, param2: int = 0) -> bool:
    '''Example function docstring.'''
    result = param1.strip() + str(param2)
    return len(result) > 0"""
    
    mock_chunk = Mock()
    mock_chunk.text = code
    mock_code_splitter.split_text.return_value = [mock_chunk]
    
    chunks = rag_agent._chunk_code(code)
    assert len(chunks) == 1
    assert chunks[0] == code
    mock_code_splitter.split_text.assert_called_once_with(code)

def test_chunk_code_with_class(rag_agent, mock_code_splitter):
    """Test code chunking with a Python class."""
    code = """class ExampleClass:
    '''Example class docstring.'''
    
    def __init__(self, value: str):
        self.value = value
        
    def process(self) -> str:
        return self.value.upper()"""
    
    mock_chunks = [Mock(text=chunk) for chunk in [
        "class ExampleClass:",
        "def __init__(self, value: str):",
        "def process(self) -> str:"
    ]]
    mock_code_splitter.split_text.return_value = mock_chunks
    
    chunks = rag_agent._chunk_code(code)
    assert len(chunks) == 3
    mock_code_splitter.split_text.assert_called_once_with(code)

def test_chunk_code_with_imports(rag_agent, mock_code_splitter):
    """Test code chunking with import statements."""
    code = """import os
from typing import List, Dict, Optional
import numpy as np
from pathlib import Path

def main():
    pass"""
    
    mock_chunks = [Mock(text=chunk) for chunk in [
        "import os\nfrom typing import List, Dict, Optional",
        "def main():\n    pass"
    ]]
    mock_code_splitter.split_text.return_value = mock_chunks
    
    chunks = rag_agent._chunk_code(code)
    assert len(chunks) == 2
    mock_code_splitter.split_text.assert_called_once_with(code)

def test_chunk_code_empty_input(rag_agent, mock_code_splitter):
    """Test code chunking with empty input."""
    code = ""
    mock_code_splitter.split_text.return_value = []
    
    chunks = rag_agent._chunk_code(code)
    assert len(chunks) == 0
    mock_code_splitter.split_text.assert_called_once_with(code)

def test_build_knowledge_base_with_multiple_files(rag_agent, mock_qdrant_client, mock_sentence_transformer, mock_code_splitter):
    """Test building knowledge base with multiple Python files."""
    code_files = {
        "file1.py": "def func1(): pass",
        "file2.py": "class Class2: pass",
        "file3.py": "import os\ndef func3(): pass"
    }
    
    # Setup mock chunks
    mock_chunks = {
        "file1.py": [Mock(text="def func1(): pass")],
        "file2.py": [Mock(text="class Class2: pass")],
        "file3.py": [Mock(text="import os"), Mock(text="def func3(): pass")]
    }
    
    def mock_split_text(code):
        for file_path, chunks in mock_chunks.items():
            if code in code_files[file_path]:
                return chunks
        return []
    
    mock_code_splitter.split_text.side_effect = mock_split_text
    
    # Setup mock embeddings
    mock_embeddings = np.array([[0.1] * 384] * 4)  # 4 chunks total
    mock_sentence_transformer.encode.return_value = mock_embeddings
    
    rag_agent.build_knowledge_base(code_files)
    
    # Verify embeddings were generated for all chunks
    assert mock_sentence_transformer.encode.call_count == 3  # Once per file
    
    # Verify Qdrant upsert was called with correct data
    assert mock_qdrant_client.upsert.call_count == 3  # Once per file

def test_query_knowledge_base_with_multiple_results(rag_agent, mock_qdrant_client, mock_sentence_transformer):
    """Test querying knowledge base with multiple results."""
    query = "test function"
    
    # Setup multiple mock search results
    mock_hits = [
        Mock(payload={'content': 'def test1():', 'file_path': 'test1.py', 'chunk_index': 0}, score=0.95),
        Mock(payload={'content': 'def test2():', 'file_path': 'test2.py', 'chunk_index': 0}, score=0.85),
        Mock(payload={'content': 'class TestClass:', 'file_path': 'test3.py', 'chunk_index': 0}, score=0.75)
    ]
    mock_qdrant_client.search.return_value = mock_hits
    
    # Generate query embedding
    mock_query_embedding = np.array([0.1] * 384)
    mock_sentence_transformer.encode.return_value = mock_query_embedding
    
    results = rag_agent.query_knowledge_base(query, top_k=3)
    
    # Verify results
    assert len(results) == 3
    assert results[0]['score'] == 0.95
    assert results[1]['score'] == 0.85
    assert results[2]['score'] == 0.75
    
    # Verify search was called with correct parameters
    mock_qdrant_client.search.assert_called_once_with(
        collection_name="project_kb",
        query_vector=mock_query_embedding.tolist(),
        limit=3
    )

def test_query_knowledge_base_error_handling(rag_agent, mock_qdrant_client, mock_sentence_transformer):
    """Test error handling in knowledge base querying."""
    query = "test function"
    
    # Mock embedding generation error
    mock_sentence_transformer.encode.side_effect = Exception("Embedding error")
    
    results = rag_agent.query_knowledge_base(query)
    
    # Should return empty results on error
    assert len(results) == 0
    
    # Reset mock and test search error
    mock_sentence_transformer.encode.side_effect = None
    mock_qdrant_client.search.side_effect = Exception("Search error")
    
    results = rag_agent.query_knowledge_base(query)
    
    # Should return empty results on error
    assert len(results) == 0

def test_initialization(rag_agent, mock_neo4j_client, mock_vector_store):
    """Test RAGContextAgent initialization"""
    assert rag_agent.neo4j_client == mock_neo4j_client
    assert rag_agent.vector_store == mock_vector_store
    assert isinstance(rag_agent.text_splitter.chunk_size, int)

def test_add_code_to_context(rag_agent, mock_vector_store, mock_neo4j_client):
    """Test adding code to both vector store and knowledge graph"""
    code = "def test_function():\\n    pass"
    metadata = {
        "file_path": "test.py",
        "file_name": "test.py",
        "language": "python"
    }

    # Test vector store addition
    rag_agent.add_code_to_context(code, metadata)
    mock_vector_store.add_texts.assert_called_once()

    # Test knowledge graph addition
    mock_neo4j_client.create_graph.assert_called_once()
    graph = mock_neo4j_client.create_graph.call_args[0][0]
    assert isinstance(graph, CodeGraph)
    assert len(graph.nodes) == 1
    assert graph.nodes[0].file_path == "test.py"

def test_get_context(rag_agent, mock_vector_store, mock_neo4j_client):
    """Test getting combined context from vector store and knowledge graph"""
    # Mock vector store results
    mock_doc = Mock()
    mock_doc.page_content = "test content"
    mock_vector_store.similarity_search_with_scores.return_value = [
        (mock_doc, 0.8),
        (mock_doc, 0.9)
    ]

    # Mock graph results
    mock_neo4j_client.find_related.return_value = {
        "nodes": ["test_node"],
        "relationships": ["test_rel"]
    }

    # Get context
    context = rag_agent.get_context("test query")
    
    # Verify results
    assert isinstance(context, RAGContext)
    assert len(context.text_chunks) == 2
    assert context.confidence_score == 0.85
    assert "nodes" in context.graph_context

def test_get_code_structure(rag_agent, mock_neo4j_client):
    """Test getting code structure from knowledge graph"""
    mock_neo4j_client.find_dependencies.return_value = {
        "nodes": ["test_node"],
        "relationships": ["test_rel"]
    }

    result = rag_agent.get_code_structure("test.py")
    mock_neo4j_client.find_dependencies.assert_called_once_with("test.py")
    assert "nodes" in result
    assert "relationships" in result

def test_get_call_hierarchy(rag_agent, mock_neo4j_client):
    """Test getting method call hierarchy from knowledge graph"""
    mock_neo4j_client.find_call_hierarchy.return_value = {
        "nodes": ["test_node"],
        "relationships": ["test_rel"]
    }

    result = rag_agent.get_call_hierarchy("test_method")
    mock_neo4j_client.find_call_hierarchy.assert_called_once_with("test_method")
    assert "nodes" in result
    assert "relationships" in result

def test_find_related_components(rag_agent, mock_neo4j_client):
    """Test finding related components from knowledge graph"""
    mock_neo4j_client.find_related.return_value = {
        "nodes": ["test_node"],
        "relationships": ["test_rel"]
    }

    result = rag_agent.find_related_components("test_component", max_distance=3)
    mock_neo4j_client.find_related.assert_called_once_with("test_component", 3)
    assert "nodes" in result
    assert "relationships" in result

def test_close(rag_agent, mock_vector_store, mock_neo4j_client):
    """Test cleanup of resources"""
    rag_agent.close()
    mock_vector_store.persist.assert_called_once()
    mock_neo4j_client.close.assert_called_once()

def test_error_handling(rag_agent, mock_vector_store, mock_neo4j_client):
    """Test error handling in RAGContextAgent"""
    # Test vector store error
    mock_vector_store.similarity_search_with_scores.side_effect = Exception("Vector store error")
    with pytest.raises(Exception):
        rag_agent.get_context("test query")

    # Test knowledge graph error
    mock_neo4j_client.find_related.side_effect = Exception("Graph error")
    with pytest.raises(Exception):
        rag_agent.get_context("test query")

def test_empty_results(rag_agent, mock_vector_store, mock_neo4j_client):
    """Test handling of empty results"""
    # Empty vector store results
    mock_vector_store.similarity_search_with_scores.return_value = []
    mock_neo4j_client.find_related.return_value = {}

    context = rag_agent.get_context("test query")
    assert len(context.text_chunks) == 0
    assert context.confidence_score == 0
    assert context.graph_context == {} 