"""Integration tests for Phase 2 RAG functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from qdrant_client.http.models import Distance, VectorParams, CollectionsResponse, CollectionDescription

from src.core_engine.agents.llm_orchestrator_agent import LLMOrchestratorAgent
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
        
        # Mock search response with relevant code context
        mock_hits = [
            Mock(payload={
                'content': 'def process_data(data: dict) -> dict:\n    """Process input data."""\n    return data',
                'file_path': 'src/utils/data_processor.py',
                'chunk_index': 0
            }, score=0.95),
            Mock(payload={
                'content': 'class DataProcessor:\n    """Data processing utility class."""',
                'file_path': 'src/utils/data_processor.py',
                'chunk_index': 1
            }, score=0.85)
        ]
        client.search.return_value = mock_hits
        
        mock.return_value = client
        yield client

@pytest.fixture
def mock_sentence_transformer():
    """Mock sentence transformer for testing."""
    with patch('src.core_engine.agents.rag_context_agent.SentenceTransformer') as mock:
        model = Mock()
        model.get_sentence_embedding_dimension.return_value = 384
        model.encode.return_value = np.array([[0.1] * 384])
        mock.return_value = model
        yield model

@pytest.fixture
def mock_code_splitter():
    """Mock LlamaIndex CodeSplitter for testing."""
    with patch('src.core_engine.agents.rag_context_agent.CodeSplitter') as mock:
        splitter = Mock()
        mock_chunks = [
            Mock(text="def process_data(data: dict) -> dict:"),
            Mock(text='class DataProcessor:')
        ]
        splitter.split_text.return_value = mock_chunks
        mock.return_value = splitter
        yield splitter

@pytest.fixture
def rag_agent(mock_qdrant_client, mock_sentence_transformer, mock_code_splitter):
    """Create RAGContextAgent with mocked dependencies."""
    return RAGContextAgent()

@pytest.fixture
def llm_agent(rag_agent):
    """Create LLMOrchestratorAgent with RAG enabled."""
    return LLMOrchestratorAgent(llm_provider='mock', use_rag=True)

def test_llm_rag_integration_code_analysis(llm_agent, rag_agent, mock_qdrant_client, mock_sentence_transformer):
    """Test integration between LLM and RAG agents during code analysis."""
    # Test code to analyze
    code_snippet = """def analyze_data(input_data: dict) -> dict:
        '''Analyze input data and return results.'''
        processed = process_data(input_data)
        return {'analysis': processed}"""
    
    # Mock static analysis findings
    static_findings = [{
        'rule_id': 'function_naming',
        'message': 'Function name follows convention',
        'line': 1,
        'category': 'style'
    }]
    
    # Call LLM analysis
    result = llm_agent.invoke_llm(
        prompt="Analyze this code and suggest improvements",
        code_snippet=code_snippet,
        static_findings=static_findings
    )
    
    # Verify RAG context was queried
    mock_sentence_transformer.encode.assert_called()
    mock_qdrant_client.search.assert_called()
    
    # Verify RAG context was included in the response
    assert 'process_data' in result
    assert 'DataProcessor' in result

def test_llm_rag_integration_multiple_files(llm_agent, rag_agent, mock_qdrant_client, mock_sentence_transformer):
    """Test integration with multiple code files."""
    # Test code files
    code_files = {
        'src/main.py': 'def main(): process_data({})',
        'src/utils.py': 'def helper(): return True'
    }
    
    # Build knowledge base
    llm_agent.rag_agent.build_knowledge_base(code_files)
    
    # Verify knowledge base was built
    assert mock_sentence_transformer.encode.call_count >= len(code_files)
    assert mock_qdrant_client.upsert.call_count >= len(code_files)
    
    # Analyze code files
    result = llm_agent.analyze_code_with_context(
        code_files=code_files,
        static_findings=[]
    )
    
    # Verify RAG was used in analysis
    assert isinstance(result, str)
    assert 'process_data' in result
    assert 'DataProcessor' in result

def test_llm_rag_integration_error_handling(llm_agent, rag_agent, mock_qdrant_client, mock_sentence_transformer):
    """Test error handling in LLM-RAG integration."""
    code_snippet = "def test(): pass"
    
    # Mock RAG error
    mock_qdrant_client.search.side_effect = Exception("RAG query failed")
    
    # Analysis should still work without RAG context
    result = llm_agent.invoke_llm(
        prompt="Analyze this code",
        code_snippet=code_snippet
    )
    
    # Verify result contains analysis even without RAG
    assert isinstance(result, str)
    assert 'Analysis Results' in result

def test_llm_rag_integration_pr_analysis(llm_agent, rag_agent, mock_qdrant_client, mock_sentence_transformer):
    """Test integration during PR analysis."""
    # Mock PR diff
    pr_diff = """diff --git a/src/utils.py b/src/utils.py
    --- a/src/utils.py
    +++ b/src/utils.py
    @@ -1,3 +1,4 @@
    +def new_function(): pass
     def process_data(): pass"""
    
    # Mock static findings
    static_findings = [{
        'rule_id': 'function_docstring',
        'message': 'Missing function docstring',
        'line': 1,
        'category': 'documentation'
    }]
    
    # Analyze PR
    result = llm_agent.analyze_pr_diff(pr_diff, static_findings)
    
    # Verify RAG context was used
    mock_sentence_transformer.encode.assert_called()
    mock_qdrant_client.search.assert_called()
    
    # Verify analysis includes both PR changes and RAG context
    assert 'new_function' in result
    assert 'process_data' in result

def test_llm_rag_integration_prompt_construction(llm_agent, rag_agent, mock_qdrant_client):
    """Test RAG context inclusion in prompt construction."""
    code_snippet = "def test(): pass"
    prompt = "Analyze this code"
    
    # Mock RAG results
    mock_hits = [
        Mock(payload={
            'content': 'def related_function(): pass',
            'file_path': 'src/related.py',
            'chunk_index': 0
        }, score=0.9)
    ]
    mock_qdrant_client.search.return_value = mock_hits
    
    # Get constructed prompt
    result = llm_agent._construct_analysis_prompt(
        prompt=prompt,
        code_snippet=code_snippet,
        rag_context=llm_agent.rag_agent.query_knowledge_base("test")
    )
    
    # Verify RAG context is included in prompt
    assert 'Relevant Code Context' in result
    assert 'related_function' in result
    assert 'src/related.py' in result
    assert '0.9' in result  # Score should be included 