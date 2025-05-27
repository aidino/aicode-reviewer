"""
RAG Context Agent for providing relevant code context during analysis.

This module implements a RAG (Retrieval Augmented Generation) agent that:
1. Chunks code using AST-aware splitting
2. Embeds code chunks using sentence transformers
3. Stores vectors in Qdrant
4. Retrieves relevant context for queries
"""

import os
from typing import List, Dict, Optional, Any
from pathlib import Path

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer
from llama_index.core.node_parser import CodeSplitter
from tree_sitter import Node
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel

import logging

from .knowledge_graph.neo4j_client import Neo4jClient
from .knowledge_graph.schema import CodeNode, CodeEdge, CodeGraph

logger = logging.getLogger(__name__)

class RAGContext(BaseModel):
    """Context information from both vector store and knowledge graph"""
    text_chunks: List[str]
    graph_context: Dict[str, Any]
    confidence_score: float

class RAGContextAgent:
    """Agent for managing code context using RAG (Retrieval Augmented Generation)."""
    
    def __init__(
        self,
        vector_store_path: str = "./vector_store",
        embeddings_model: Optional[Any] = None,
        neo4j_client: Optional[Neo4jClient] = None
    ):
        """Initialize RAG context agent with vector store and knowledge graph"""
        self.embeddings = embeddings_model or OpenAIEmbeddings()
        self.vector_store = Chroma(
            persist_directory=vector_store_path,
            embedding_function=self.embeddings
        )
        self.neo4j_client = neo4j_client or Neo4jClient()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
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

    def add_code_to_context(self, code: str, metadata: Dict[str, str]):
        """Add code to both vector store and knowledge graph"""
        # Split code into chunks for vector store
        chunks = self.text_splitter.split_text(code)
        self.vector_store.add_texts(chunks, metadatas=[metadata] * len(chunks))

        # Extract code structure for knowledge graph
        # This would use AST parsing in practice
        # For now, just create placeholder nodes
        file_node = CodeNode(
            id=metadata.get('file_path', ''),
            type='File',
            name=metadata.get('file_name', ''),
            file_path=metadata.get('file_path', ''),
            language=metadata.get('language', '')
        )
        
        graph = CodeGraph(nodes=[file_node], edges=[])
        self.neo4j_client.create_graph(graph)

    def get_context(
        self,
        query: str,
        k_vector: int = 3,
        max_graph_distance: int = 2
    ) -> RAGContext:
        """Get combined context from vector store and knowledge graph"""
        # Get relevant text chunks from vector store
        vector_results = self.vector_store.similarity_search_with_scores(
            query,
            k=k_vector
        )
        chunks = [doc.page_content for doc, _ in vector_results]
        scores = [score for _, score in vector_results]
        avg_score = sum(scores) / len(scores) if scores else 0

        # Get graph context based on query
        # This is a simplified example - in practice would parse query
        # to determine what graph patterns to look for
        graph_context = self.neo4j_client.find_related(
            query,
            max_distance=max_graph_distance
        )

        return RAGContext(
            text_chunks=chunks,
            graph_context=graph_context,
            confidence_score=avg_score
        )

    def get_code_structure(self, file_path: str) -> Dict[str, Any]:
        """Get code structure from knowledge graph"""
        return self.neo4j_client.find_dependencies(file_path)

    def get_call_hierarchy(self, method_name: str) -> Dict[str, Any]:
        """Get method call hierarchy from knowledge graph"""
        return self.neo4j_client.find_call_hierarchy(method_name)

    def find_related_components(
        self,
        name: str,
        max_distance: int = 2
    ) -> Dict[str, Any]:
        """Find related code components from knowledge graph"""
        return self.neo4j_client.find_related(name, max_distance)

    def close(self):
        """Clean up resources"""
        self.vector_store.persist()
        self.neo4j_client.close() 