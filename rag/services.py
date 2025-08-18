import requests
import json
import logging
from django.conf import settings
from django.core.cache import cache
from .models import KnowledgeBase, Document, DocumentChunk, RAGQuery
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class NubiousRAGService:
    """
    Service class for interacting with Nubious RAG API.
    """
    
    def __init__(self):
        self.api_key = settings.NUBIOUS_API_KEY
        self.base_url = "https://api.nubious.ai"  # Replace with actual Nubious API URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """
        Make a request to the Nubious API.
        """
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Nubious API request failed: {str(e)}")
            raise Exception(f"Failed to communicate with Nubious API: {str(e)}")
    
    def search_documents(self, query: str, knowledge_base_id: str = None, limit: int = 5) -> List[Dict]:
        """
        Search for relevant documents using Nubious RAG.
        """
        try:
            data = {
                "query": query,
                "limit": limit
            }
            
            if knowledge_base_id:
                data["knowledge_base_id"] = knowledge_base_id
            
            response = self._make_request("/search", method="POST", data=data)
            
            # Extract relevant information from response
            results = []
            for result in response.get("results", []):
                results.append({
                    "content": result.get("content", ""),
                    "source": result.get("source", ""),
                    "score": result.get("score", 0.0),
                    "metadata": result.get("metadata", {})
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Document search failed: {str(e)}")
            return []
    
    def generate_response(self, query: str, context: List[Dict], conversation_history: List[Dict] = None) -> str:
        """
        Generate a response using Nubious RAG with retrieved context.
        """
        try:
            data = {
                "query": query,
                "context": context,
                "conversation_history": conversation_history or []
            }
            
            response = self._make_request("/generate", method="POST", data=data)
            
            return response.get("response", "")
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return "I apologize, but I'm unable to generate a response at the moment. Please try again later."
    
    def create_embedding(self, text: str) -> str:
        """
        Create an embedding for text using Nubious API.
        """
        try:
            data = {"text": text}
            response = self._make_request("/embeddings", method="POST", data=data)
            return response.get("embedding_id", "")
            
        except Exception as e:
            logger.error(f"Embedding creation failed: {str(e)}")
            return ""


class RAGPipelineService:
    """
    Service class for managing the complete RAG pipeline.
    """
    
    def __init__(self):
        self.nubious_service = NubiousRAGService()
    
    def process_query(self, user, query: str, session_id: str = None, knowledge_base_id: str = None) -> Dict[str, Any]:
        """
        Process a user query through the complete RAG pipeline.
        """
        try:
            # Step 1: Search for relevant documents
            search_results = self.nubious_service.search_documents(
                query=query,
                knowledge_base_id=knowledge_base_id,
                limit=5
            )
            
            # Step 2: Get conversation history if session is provided
            conversation_history = []
            if session_id:
                from chat.services import ChatSessionService, ChatMessageService
                session_service = ChatSessionService()
                message_service = ChatMessageService()
                
                session = session_service.get_session_by_id(session_id, user)
                if session:
                    messages = message_service.get_conversation_history(session, limit=10)
                    conversation_history = [
                        {
                            "role": msg.sender,
                            "content": msg.content
                        }
                        for msg in messages
                    ]
            
            # Step 3: Generate response with context
            response = self.nubious_service.generate_response(
                query=query,
                context=search_results,
                conversation_history=conversation_history
            )
            
            # Step 4: Store the RAG query
            rag_query = RAGQuery.objects.create(
                user=user,
                query=query,
                response=response,
                retrieved_context={
                    "sources": [result.get("source", "") for result in search_results],
                    "scores": [result.get("score", 0.0) for result in search_results],
                    "context_count": len(search_results)
                },
                knowledge_base_id=knowledge_base_id,
                metadata={
                    "session_id": session_id,
                    "conversation_history_length": len(conversation_history)
                }
            )
            
            # Step 5: Return the complete response
            return {
                "response": response,
                "context": search_results,
                "rag_query_id": str(rag_query.id),
                "sources": [result.get("source", "") for result in search_results]
            }
            
        except Exception as e:
            logger.error(f"RAG pipeline processing failed: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error while processing your query. Please try again.",
                "context": [],
                "rag_query_id": None,
                "sources": [],
                "error": str(e)
            }
    
    def add_document_to_knowledge_base(self, knowledge_base_id: str, title: str, content: str, file_path: str = None) -> Document:
        """
        Add a document to the knowledge base and create embeddings.
        """
        try:
            # Get or create knowledge base
            knowledge_base = KnowledgeBase.objects.get(id=knowledge_base_id, is_active=True)
            
            # Create document
            document = Document.objects.create(
                knowledge_base=knowledge_base,
                title=title,
                content=content,
                file_path=file_path or "",
                metadata={"source": "manual_upload"}
            )
            
            # Create embeddings for document chunks
            self._create_document_embeddings(document)
            
            logger.info(f"Added document {document.id} to knowledge base {knowledge_base_id}")
            return document
            
        except Exception as e:
            logger.error(f"Failed to add document to knowledge base: {str(e)}")
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


class KnowledgeBaseService:
    """
    Service class for managing knowledge bases.
    """
    
    def create_knowledge_base(self, user, name: str, description: str = "") -> KnowledgeBase:
        """
        Create a new knowledge base for a user.
        """
        try:
            knowledge_base = KnowledgeBase.objects.create(
                user=user,
                name=name,
                description=description
            )
            
            logger.info(f"Created knowledge base {knowledge_base.id} for user {user.id}")
            return knowledge_base
            
        except Exception as e:
            logger.error(f"Failed to create knowledge base for user {user.id}: {str(e)}")
            raise
    
    def get_user_knowledge_bases(self, user) -> List[KnowledgeBase]:
        """
        Get all knowledge bases for a user.
        """
        return KnowledgeBase.objects.filter(user=user, is_active=True).order_by('-created_at')
    
    def get_knowledge_base_by_id(self, knowledge_base_id: str, user) -> Optional[KnowledgeBase]:
        """
        Get a specific knowledge base by ID.
        """
        try:
            return KnowledgeBase.objects.get(id=knowledge_base_id, user=user, is_active=True)
        except KnowledgeBase.DoesNotExist:
            return None
    
    def delete_knowledge_base(self, knowledge_base: KnowledgeBase):
        """
        Soft delete a knowledge base and all its documents.
        """
        try:
            # Soft delete all documents
            knowledge_base.documents.filter(is_active=True).update(is_active=False)
            
            # Soft delete the knowledge base
            knowledge_base.soft_delete()
            
            logger.info(f"Deleted knowledge base {knowledge_base.id}")
            
        except Exception as e:
            logger.error(f"Failed to delete knowledge base {knowledge_base.id}: {str(e)}")
            raise
