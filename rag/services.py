import logging
import hashlib
import requests
from typing import List, Dict, Any, Optional, Tuple
from django.conf import settings
from django.core.paginator import Paginator
import openai
import httpx
from .models import Document, DocumentChunk, RAGQuery

logger = logging.getLogger(__name__)


def init_openai(api_key: str, proxy_url: str = None):
    """Initialize OpenAI client with proper HTTP client configuration"""
    logger.info(f"Initializing OpenAI client with API key: {api_key[:20]}...")

    try:
        http_client = None
        if proxy_url:
            http_client = httpx.Client(proxies=proxy_url)
        else:
            # Create a simple HTTP client without proxy configuration
            http_client = httpx.Client()

        client = openai.OpenAI(
            api_key=api_key,
            http_client=http_client
        )
        logger.info("OpenAI client initialized successfully")
        return client

    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        # Fallback to basic initialization
        try:
            client = openai.OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized with fallback method")
            return client
        except Exception as e2:
            logger.error(f"Fallback initialization also failed: {e2}")
            raise


class OpenAIRAGService:
    """
    Service to interact with OpenAI API for RAG functionality.
    """
    
    def __init__(self):
        api_key = getattr(settings, 'OPENAI_API_KEY', 'your-openai-api-key-here')
        proxy_url = getattr(settings, 'OPENAI_PROXY_URL', None)
        
        # Initialize OpenAI client with proper HTTP client configuration
        self.client = init_openai(api_key, proxy_url)
    
    def search_documents(self, query: str, category: str = None, limit: int = 5, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using OpenAI embeddings and similarity search.
        For now, this will return documents from our database that match the query.
        """
        try:
            # Get documents from database for this user
            documents = Document.objects.filter(
                user_id=user_id,
                is_active=True
            )
            
            if category:
                documents = documents.filter(category=category)
            
            # For now, return documents that contain the query terms
            # In a full implementation, you'd use embeddings for semantic search
            matching_docs = []
            query_terms = query.lower().split()
            
            for doc in documents[:limit]:
                doc_text = f"{doc.title} {doc.content}".lower()
                if any(term in doc_text for term in query_terms):
                    matching_docs.append({
                        'id': doc.metadata.get('openai_document_id', f"doc_{doc.id}") if doc.metadata else f"doc_{doc.id}",
                        'content': doc.content,
                        'score': 0.8,  # Mock score
                        'metadata': {
                            'source': 'openai_search', 
                            'category': doc.category, 
                            'user_id': str(doc.user.id),
                            'title': doc.title
                        }
                    })
            
            logger.info(f"OpenAI search results for query: {query}, user_id: {user_id}, found {len(matching_docs)} documents")
            return matching_docs
            
        except Exception as e:
            logger.error(f"Failed to search documents with OpenAI: {str(e)}")
            return []
    
    def generate_response(self, query: str, context: List[str]) -> str:
        """
        Generate response using OpenAI GPT model with context.
        """
        try:
            # Prepare context for the prompt
            context_text = " ".join(context[:2])  # Use first 2 context items
            
            # Create the prompt
            if context_text:
                prompt = f"""Based on the following context, please answer the question. If the context doesn't contain relevant information, say so.

Context:
{context_text}

Question: {query}

Answer:"""
            else:
                prompt = f"Please answer the following question: {query}"

            # Generate response using OpenAI (new API format)
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides accurate and relevant answers based on the given context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            response_text = response.choices[0].message.content
            logger.info(f"OpenAI response generated for query: {query}")
            return response_text
            
        except Exception as e:
            logger.error(f"Failed to generate response with OpenAI: {str(e)}")
            return f"I apologize, but I encountered an error while processing your query: {query}"
    
    def create_embedding(self, text: str) -> str:
        """
        Create embedding using OpenAI's text-embedding-ada-002 model.
        """
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            
            embedding_id = f"emb_{hashlib.md5(text.encode()).hexdigest()[:16]}"
            logger.info(f"OpenAI embedding created for text: {text[:50]}...")
            return embedding_id
            
        except Exception as e:
            logger.error(f"Failed to create embedding with OpenAI: {str(e)}")
            return f"error_embedding_{hashlib.md5(text.encode()).hexdigest()[:8]}"
    
    def upload_document(self, title: str, content: str, category: str = 'general', metadata: Dict = None) -> str:
        """
        Process document with OpenAI (create embeddings, store metadata).
        """
        try:
            # Create embedding for the document content
            embedding_id = self.create_embedding(content)
            
            # Generate a unique document ID
            import uuid
            doc_id = f"openai_doc_{uuid.uuid4().hex[:12]}"
            
            logger.info(f"OpenAI document processed: {title}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to process document with OpenAI: {str(e)}")
            raise
    
    def delete_document_from_openai(self, document_id: str) -> bool:
        """
        Delete document from OpenAI storage (if applicable).
        For now, just return success as we're storing in our database.
        """
        try:
            logger.info(f"OpenAI document deletion requested: {document_id}")
            # In a full implementation, you might delete from vector database
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document from OpenAI: {str(e)}")
            return False


class RAGPipelineService:
    """
    Service for RAG pipeline operations.
    Simplified: Works directly with documents, no knowledge bases.
    """
    
    def __init__(self):
        self.openai_service = OpenAIRAGService()
    
    def process_query(self, user, query: str, document_category: str = None, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Process a RAG query and generate a response.
        Simplified: Uses document category instead of knowledge base ID.
        """
        try:
            # Search for relevant documents
            search_results = self.openai_service.search_documents(
                query=query, 
                category=document_category,
                limit=5,
                user_id=str(user.id)
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
            response = self.openai_service.generate_response(query, context)
            
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
        Add a document and process with OpenAI for indexing.
        """
        try:
            # Process document with OpenAI first
            openai_metadata = {
                'user_id': str(user.id),
                'source_url': source_url,
                **(metadata or {})
            }
            
            openai_document_id = self.openai_service.upload_document(
                title=title,
                content=content,
                category=category,
                metadata=openai_metadata
            )
            
            # Create document in our database
            document = Document.objects.create(
                user=user,
                title=title,
                content=content,
                category=category,
                source_url=source_url,
                metadata={
                    **(metadata or {}),
                    'openai_document_id': openai_document_id
                }
            )
            
            # Create embeddings for document chunks (for local storage)
            self._create_document_embeddings(document)
            
            logger.info(f"Added document {document.id} for user {user.id} with OpenAI ID: {openai_document_id}")
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
                # Create embedding using OpenAI API
                embedding_id = self.openai_service.create_embedding(chunk_content)
                
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
        Soft delete a document and remove from OpenAI.
        """
        try:
            # Delete from OpenAI if we have the document ID
            openai_document_id = document.metadata.get('openai_document_id')
            if openai_document_id:
                self.openai_service.delete_document_from_openai(openai_document_id)
            
            # Soft delete from our database
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
    
    def get_document_categories(self, user) -> List[str]:
        """
        Get unique document categories for a user.
        """
        try:
            categories = Document.objects.filter(
                user=user, 
                is_active=True
            ).values_list('category', flat=True).distinct()
            
            return list(categories)
        except Exception as e:
            logger.error(f"Failed to get document categories: {str(e)}")
            return []
    
    def search_user_documents(self, user, query: str, category: str = None, limit: int = 10) -> List[Document]:
        """
        Search user's documents using OpenAI API.
        """
        try:
            # Search in OpenAI with user filter
            search_results = self.openai_service.search_documents(
                query=query,
                category=category,
                limit=limit,
                user_id=str(user.id)
            )
            
            # Filter results to only include user's documents
            user_document_ids = []
            for result in search_results:
                result_metadata = result.get('metadata', {})
                if result_metadata.get('user_id') == str(user.id):
                    user_document_ids.append(result.get('id'))
            
            # Get documents from our database
            documents = Document.objects.filter(
                user=user,
                is_active=True,
                metadata__openai_document_id__in=user_document_ids
            )
            
            logger.info(f"Found {len(documents)} documents for user {user.id} with query: {query}")
            return list(documents)
            
        except Exception as e:
            logger.error(f"Failed to search user documents: {str(e)}")
            return []
