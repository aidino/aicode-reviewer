"""Unit tests for RAGContextAgent."""

import os
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from qdrant_client.http.models import Distance, VectorParams, CollectionsResponse, CollectionDescription
from sentence_transformers import SentenceTransformer

from src.core_engine.agents.rag_context_agent import RAGContextAgent

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
def rag_agent(mock_qdrant_client, mock_sentence_transformer, mock_code_splitter):
    """Create RAGContextAgent with mocked dependencies."""
    return RAGContextAgent()

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