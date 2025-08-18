from rest_framework import status
from core.views import BaseAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from core.authentication import JWTAuthentication
from .models import KnowledgeBase, Document, RAGQuery
from .services import RAGPipelineService, KnowledgeBaseService
from .serializers import (
    KnowledgeBaseSerializer, DocumentSerializer, RAGQuerySerializer,
    CreateKnowledgeBaseSerializer, CreateDocumentSerializer
)
from .controllers import RAGController, KnowledgeBaseController, DocumentController
import logging

logger = logging.getLogger(__name__)


class RAGQueryAPIView(BaseAPIView):
    """
    API to process RAG queries and generate responses.
    """
    authentication_classes = [JWTAuthentication]
    
    def post(self, request, *args, **kwargs):
        """Process a RAG query and generate a response."""
        controller = RAGController()
        result = controller.process_rag_query(request.user, request.data)
        return Response(result['data'], status=result['status'])


class KnowledgeBaseListCreateAPIView(BaseAPIView):
    """
    API to list and create knowledge bases.
    """
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, *args, **kwargs):
        """Get all knowledge bases for the current user."""
        controller = KnowledgeBaseController()
        result = controller.list_knowledge_bases(request.user, request)
        return Response(result['data'], status=result['status'])
    
    def post(self, request, *args, **kwargs):
        """Create a new knowledge base."""
        controller = KnowledgeBaseController()
        result = controller.create_knowledge_base(request.user, request.data)
        return Response(result['data'], status=result['status'])


class KnowledgeBaseDetailAPIView(BaseAPIView):
    """
    API to retrieve, update, and delete a specific knowledge base.
    """
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, kb_id, *args, **kwargs):
        """Get a specific knowledge base."""
        controller = KnowledgeBaseController()
        result = controller.get_knowledge_base(request.user, kb_id)
        return Response(result['data'], status=result['status'])
    
    def put(self, request, kb_id, *args, **kwargs):
        """Update a knowledge base."""
        controller = KnowledgeBaseController()
        result = controller.update_knowledge_base(request.user, kb_id, request.data)
        return Response(result['data'], status=result['status'])
    
    def patch(self, request, kb_id, *args, **kwargs):
        """Partially update a knowledge base."""
        controller = KnowledgeBaseController()
        result = controller.update_knowledge_base(request.user, kb_id, request.data)
        return Response(result['data'], status=result['status'])
    
    def delete(self, request, kb_id, *args, **kwargs):
        """Delete a knowledge base."""
        controller = KnowledgeBaseController()
        result = controller.delete_knowledge_base(request.user, kb_id)
        return Response(result['data'], status=result['status'])


class DocumentListCreateAPIView(BaseAPIView):
    """
    API to list and create documents in a knowledge base.
    """
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, kb_id, *args, **kwargs):
        """Get all documents in a knowledge base."""
        controller = DocumentController()
        result = controller.list_documents(request.user, kb_id, request)
        return Response(result['data'], status=result['status'])
    
    def post(self, request, kb_id, *args, **kwargs):
        """Create a new document in the knowledge base."""
        controller = DocumentController()
        result = controller.add_document(request.user, kb_id, request.data)
        return Response(result['data'], status=result['status'])


class DocumentDetailAPIView(BaseAPIView):
    """
    API to retrieve, update, and delete a specific document.
    """
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, kb_id, doc_id, *args, **kwargs):
        """Get a specific document."""
        controller = DocumentController()
        result = controller.get_document(request.user, kb_id, doc_id)
        return Response(result['data'], status=result['status'])
    
    def put(self, request, kb_id, doc_id, *args, **kwargs):
        """Update a document."""
        controller = DocumentController()
        result = controller.update_document(request.user, kb_id, doc_id, request.data)
        return Response(result['data'], status=result['status'])
    
    def patch(self, request, kb_id, doc_id, *args, **kwargs):
        """Partially update a document."""
        controller = DocumentController()
        result = controller.update_document(request.user, kb_id, doc_id, request.data)
        return Response(result['data'], status=result['status'])
    
    def delete(self, request, kb_id, doc_id, *args, **kwargs):
        """Delete a document."""
        controller = DocumentController()
        result = controller.delete_document(request.user, kb_id, doc_id)
        return Response(result['data'], status=result['status'])


class RAGQueryHistoryAPIView(BaseAPIView):
    """
    API to get RAG query history for a user.
    """
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, *args, **kwargs):
        """Get RAG query history for the current user."""
        controller = RAGController()
        result = controller.get_rag_history(request.user, request)
        return Response(result['data'], status=result['status'])
