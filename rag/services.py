import logging
import hashlib
import requests
from typing import List, Dict, Any, Optional, Tuple
from django.conf import settings
from django.core.paginator import Paginator
from .models import Document, DocumentChunk, RAGQuery

logger = logging.getLogger(__name__)


class NubiousRAGService:
    """
    Service to interact with Nubious RAG API.
    Mocked for development - replace with actual API calls when ready.
    """
    
    def __init__(self):
        self.base_url = getattr(settings, 'NUBIOUS_API_URL', 'https://api.nubious.ai')
        self.api_key = getattr(settings, 'NUBIOUS_API_KEY', 'mock_key')
    
    def search_documents(self, query: str, category: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using Nubious API.
        Mocked for development.
        """
        try:
            # Mock response for development
            mock_results = [
                {
                    'id': f"doc_{hashlib.md5(f'{query}_{i}'.encode()).hexdigest()[:8]}",
                    'content': f"Mock document content {i} related to: {query}",
                    'score': 0.9 - (i * 0.1),
                    'metadata': {'source': 'mock', 'category': category or 'general'}
                }
                for i in range(min(limit, 3))
            ]
            
            logger.info(f"Mock search results for query: {query}")
            return mock_results
            
            # Uncomment when ready to use real API:
            # url = f"{self.base_url}/search"
            # headers = {'Authorization': f'Bearer {self.api_key}'}
            # params = {'query': query, 'limit': limit}
            # if category:
            #     params['category'] = category
            # 
            # response = requests.get(url, headers=headers, params=params)
            # response.raise_for_status()
            # return response.json()['results']
            
        except Exception as e:
            logger.error(f"Failed to search documents: {str(e)}")
            return []
    
    def generate_response(self, query: str, context: List[str]) -> str:
        """
        Generate response using Nubious API.
        Mocked for development.
        """
        try:
            # Mock response for development
            context_text = " ".join(context[:2])  # Use first 2 context items
            mock_response = f"Based on the provided context, here's what I found about '{query}': {context_text}. This is a mock response generated for development purposes."
            
            logger.info(f"Mock response generated for query: {query}")
            return mock_response
            
            # Uncomment when ready to use real API:
            # url = f"{self.base_url}/generate"
            # headers = {'Authorization': f'Bearer {self.api_key}'}
            # data = {
            #     'query': query,
            #     'context': context
            # }
            # 
            # response = requests.post(url, headers=headers, json=data)
            # response.raise_for_status()
            # return response.json()['response']
            
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            return f"I apologize, but I encountered an error while processing your query: {query}"
    
    def create_embedding(self, text: str) -> str:
        """
        Create embedding using Nubious API.
        Mocked for development.
        """
        try:
            # Mock embedding ID for development
            embedding_id = f"emb_{hashlib.md5(text.encode()).hexdigest()[:16]}"
            
            logger.info(f"Mock embedding created for text: {text[:50]}...")
            return embedding_id
            
            # Uncomment when ready to use real API:
            # url = f"{self.base_url}/embeddings"
            # headers = {'Authorization': f'Bearer {self.api_key}'}
            # data = {'text': text}
            # 
            # response = requests.post(url, headers=headers, json=data)
            # response.raise_for_status()
            # return response.json()['embedding_id']
            
        except Exception as e:
            logger.error(f"Failed to create embedding: {str(e)}")
            return f"mock_embedding_{hashlib.md5(text.encode()).hexdigest()[:8]}"


class RAGPipelineService:
    """
    Service for RAG pipeline operations.
    Simplified: Works directly with documents, no knowledge bases.
    """
    
    def __init__(self):
        self.nubious_service = NubiousRAGService()
    
    def process_query(self, user, query: str, document_category: str = None, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Process a RAG query and generate a response.
        Simplified: Uses document category instead of knowledge base ID.
        """
        try:
            # Search for relevant documents
            search_results = self.nubious_service.search_documents(
                query=query, 
                category=document_category,
                limit=5
            )
            
            if not search_results:
                return {
                    'query': query,
                    'response': "I couldn't find any relevant information to answer your question.",
                    'context': [],
                    'sources': []
                }
            
            # Extract context from search results
            context = [result['content'] for result in search_results]
            sources = [result['metadata'] for result in search_results]
            
            # Generate response
            response = self.nubious_service.generate_response(query, context)
            
            # Store the query
            rag_query = RAGQuery.objects.create(
                user=user,
                query=query,
                response=response,
                document_category=document_category or 'general',
                metadata={
                    'context_count': len(context),
                    'sources': sources,
                    'conversation_history_length': len(conversation_history or [])
                }
            )
            
            logger.info(f"RAG query processed successfully: {rag_query.id}")
            
            return {
                'query': query,
                'response': response,
                'context': context,
                'sources': sources,
                'query_id': str(rag_query.id)
            }
            
        except Exception as e:
            logger.error(f"Failed to process RAG query: {str(e)}")
            return None
    
    def add_document(self, user, title: str, content: str, category: str = 'general', source_url: str = None, metadata: Dict = None) -> Document:
        """
        Add a document and create embeddings.
        Simplified: No knowledge base required.
        """
        try:
            # Create document
            document = Document.objects.create(
                user=user,
                title=title,
                content=content,
                category=category,
                source_url=source_url,
                metadata=metadata or {}
            )
            
            # Create embeddings for document chunks
            self._create_document_embeddings(document)
            
            logger.info(f"Added document {document.id} for user {user.id}")
            return document
            
        except Exception as e:
            logger.error(f"Failed to add document: {str(e)}")
            raise
    
    def _create_document_embeddings(self, document: Document):
        """
        Create embeddings for document chunks.
        """
        try:
            # Split document into chunks (simple splitting for now)
            chunk_size = 1000
            content = document.content
            chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
            
            for i, chunk_content in enumerate(chunks):
                # Create embedding using Nubious API
                embedding_id = self.nubious_service.create_embedding(chunk_content)
                
                # Store chunk with embedding ID
                DocumentChunk.objects.create(
                    document=document,
                    content=chunk_content,
                    chunk_index=i,
                    embedding_id=embedding_id,
                    metadata={"chunk_size": len(chunk_content)}
                )
            
            logger.info(f"Created {len(chunks)} embeddings for document {document.id}")
            
        except Exception as e:
            logger.error(f"Failed to create embeddings for document {document.id}: {str(e)}")
            raise
    
    def get_user_documents(self, user, category: str = None, page: int = 1, page_size: int = 20) -> Tuple[List[Document], int]:
        """
        Get documents for a user with optional category filtering.
        """
        try:
            queryset = Document.objects.filter(user=user, is_active=True)
            
            if category:
                queryset = queryset.filter(category=category)
            
            paginator = Paginator(queryset, page_size)
            documents = paginator.get_page(page)
            
            return list(documents), paginator.count
            
        except Exception as e:
            logger.error(f"Failed to get user documents: {str(e)}")
            return [], 0
    
    def get_document_by_id(self, document_id: str, user) -> Optional[Document]:
        """
        Get a specific document by ID.
        """
        try:
            return Document.objects.get(id=document_id, user=user, is_active=True)
        except Document.DoesNotExist:
            return None
    
    def update_document(self, document: Document, **kwargs) -> Document:
        """
        Update a document and regenerate embeddings if content changed.
        """
        try:
            content_changed = 'content' in kwargs and kwargs['content'] != document.content
            
            # Update document
            for field, value in kwargs.items():
                setattr(document, field, value)
            document.save()
            
            # Regenerate embeddings if content changed
            if content_changed:
                # Delete old chunks
                document.chunks.all().delete()
                # Create new embeddings
                self._create_document_embeddings(document)
            
            logger.info(f"Updated document {document.id}")
            return document
            
        except Exception as e:
            logger.error(f"Failed to update document {document.id}: {str(e)}")
            raise
    
    def delete_document(self, document: Document):
        """
        Soft delete a document.
        """
        try:
            document.is_active = False
            document.save()
            logger.info(f"Deleted document {document.id}")
        except Exception as e:
            logger.error(f"Failed to delete document {document.id}: {str(e)}")
            raise
    
    def get_user_rag_history(self, user, page: int = 1, page_size: int = 20, document_category: str = None) -> Tuple[List[RAGQuery], int]:
        """
        Get RAG query history for a user with pagination.
        """
        try:
            queryset = RAGQuery.objects.filter(user=user, is_active=True)
            
            if document_category:
                queryset = queryset.filter(document_category=document_category)
            
            paginator = Paginator(queryset, page_size)
            queries = paginator.get_page(page)
            
            return list(queries), paginator.count
            
        except Exception as e:
            logger.error(f"Failed to get RAG history: {str(e)}")
            return [], 0
