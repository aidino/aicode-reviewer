"""
RAG Context Agent for providing relevant code context during analysis.

This module implements a RAG (Retrieval Augmented Generation) agent that:
1. Chunks code using AST-aware splitting
2. Embeds code chunks using sentence transformers
3. Stores vectors in Qdrant
4. Retrieves relevant context for queries
"""

import os
from typing import List, Dict, Optional
from pathlib import Path

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer
from llama_index.core.node_parser import CodeSplitter
from tree_sitter import Node

import logging

logger = logging.getLogger(__name__)

class RAGContextAgent:
    """Agent for managing code context using RAG (Retrieval Augmented Generation)."""
    
    def __init__(
        self,
        collection_name: str = "project_kb",
        qdrant_url: str = "http://localhost:6333",
        qdrant_api_key: Optional[str] = None
    ):
        """
        Initialize the RAGContextAgent.
        
        Args:
            collection_name (str): Name of the Qdrant collection to use
            qdrant_url (str): URL of the Qdrant server
            qdrant_api_key (Optional[str]): API key for Qdrant authentication
        """
        self.collection_name = collection_name
        self.qdrant_url = qdrant_url
        self.qdrant_api_key = qdrant_api_key
        
        # Initialize Qdrant client
        self.client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key
        )
        
        # Initialize sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Good balance of speed/quality
        self.vector_size = self.model.get_sentence_embedding_dimension()
        
        # Initialize code splitter with fallback
        try:
            # Try to create CodeSplitter - it may need additional dependencies
            self.code_splitter = CodeSplitter(
                language="python",
                chunk_lines=50,  # Reasonable number of lines for code chunks
                chunk_lines_overlap=10  # Some overlap to maintain context
            )
            self.use_llama_splitter = True
        except ImportError as e:
            logger.warning(f"CodeSplitter not available, using simple splitter: {str(e)}")
            self.code_splitter = None
            self.use_llama_splitter = False
        
        # Create collection if it doesn't exist
        self._create_collection_if_not_exists()
    
    def _create_collection_if_not_exists(self) -> None:
        """Create Qdrant collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection {self.collection_name}")
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
    
    def _chunk_code(self, code: str, file_path: str = "") -> List[str]:
        """
        Split code into semantic chunks using AST-aware splitting.
        
        Args:
            code (str): Source code to chunk
            file_path (str): Path of the source file (for better chunk naming)
            
        Returns:
            List[str]: List of code chunks
        """
        if self.use_llama_splitter and self.code_splitter is not None:
            try:
                # Use LlamaIndex CodeSplitter for AST-aware splitting
                nodes = self.code_splitter.split_text(code)
                return [node.text for node in nodes]
            except Exception as e:
                logger.warning(f"AST parsing failed for {file_path}, falling back to simple chunking: {str(e)}")
        
        # Simple fallback: split by newlines into roughly equal chunks
        lines = code.split('\n')
        chunks = []
        chunk_size = 50  # Same as CodeSplitter default
        overlap = 10  # Overlap between chunks
        
        for i in range(0, len(lines), chunk_size - overlap):
            end_idx = min(i + chunk_size, len(lines))
            chunk = '\n'.join(lines[i:end_idx])
            if chunk.strip():  # Only add non-empty chunks
                chunks.append(chunk)
            
            # Break if we've reached the end
            if end_idx >= len(lines):
                break
        
        return chunks
    
    def build_knowledge_base(self, code_files: Dict[str, str]) -> None:
        """
        Process code files and build the knowledge base in Qdrant.
        
        Args:
            code_files (Dict[str, str]): Dictionary mapping file paths to code content
        """
        try:
            for file_path, code in code_files.items():
                # Split code into chunks
                chunks = self._chunk_code(code, file_path)
                
                # Generate embeddings
                embeddings = self.model.encode(chunks, convert_to_numpy=True)
                
                # Prepare payload with metadata
                payloads = [{
                    'file_path': file_path,
                    'content': chunk,
                    'chunk_index': i
                } for i, chunk in enumerate(chunks)]
                
                # Upsert vectors to Qdrant
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=[{
                        'id': f"{file_path}_{i}",
                        'vector': embedding.tolist(),
                        'payload': payload
                    } for i, (embedding, payload) in enumerate(zip(embeddings, payloads))]
                )
                logger.info(f"Added {len(chunks)} chunks from {file_path} to knowledge base")
        except Exception as e:
            logger.error(f"Error building knowledge base: {str(e)}")
    
    def query_knowledge_base(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Query the knowledge base for relevant code snippets.
        
        Args:
            query (str): Query string to search for
            top_k (int): Number of results to return
            
        Returns:
            List[Dict]: List of results with content and metadata
        """
        try:
            # Generate query embedding
            query_vector = self.model.encode(query, convert_to_numpy=True)
            
            # Search Qdrant
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector.tolist(),
                limit=top_k
            )
            
            # Format results
            return [{
                'content': hit.payload['content'],
                'file_path': hit.payload['file_path'],
                'chunk_index': hit.payload['chunk_index'],
                'score': hit.score
            } for hit in results]
        except Exception as e:
            logger.error(f"Error querying knowledge base: {str(e)}")
            return [] 