from rest_framework import status
from rest_framework.response import Response
from core.views import BaseAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from core.authentication import JWTAuthentication
from .models import Document, RAGQuery
from .serializers import (
    DocumentSerializer, RAGQuerySerializer,
    CreateDocumentSerializer
)
from .controllers import RAGController, DocumentController
import logging

logger = logging.getLogger(__name__)


class RAGQueryAPIView(BaseAPIView):
    """
    API to process RAG queries and generate responses.
    """
    authentication_classes = [JWTAuthentication]
    
    def post(self, request, *args, **kwargs):
        try:
            """Process a RAG query and generate a response."""
            controller = RAGController()
            result = controller.process_rag_query(request.user, request.data)
            print(result)
        except Exception as e:
            print(e)
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


class DocumentListCreateAPIView(ListCreateAPIView):
    """
    API to list and create documents.
    """
    authentication_classes = [JWTAuthentication]
    serializer_class = DocumentSerializer
    
    def get_queryset(self):
        """Get documents for the current user."""
        return Document.objects.filter(user=self.request.user, is_active=True)
    
    def get(self, request, *args, **kwargs):
        """Get all documents for the current user."""
        controller = DocumentController()
        result = controller.list_documents(request.user, request)
        return Response(result['data'], status=result['status'])
    
    def post(self, request, *args, **kwargs):
        """Create a new document."""
        controller = DocumentController()
        result = controller.create_document(request.user, request.data)
        return Response(result['data'], status=result['status'])


class DocumentDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    API to retrieve, update, and delete a specific document.
    """
    authentication_classes = [JWTAuthentication]
    serializer_class = DocumentSerializer
    
    def get_queryset(self):
        """Get documents for the current user."""
        return Document.objects.filter(user=self.request.user, is_active=True)
    
    def get(self, request, pk, *args, **kwargs):
        """Get a specific document."""
        controller = DocumentController()
        result = controller.get_document(request.user, pk)
        return Response(result['data'], status=result['status'])
    
    def put(self, request, pk, *args, **kwargs):
        """Update a document."""
        controller = DocumentController()
        result = controller.update_document(request.user, pk, request.data)
        return Response(result['data'], status=result['status'])
    
    def patch(self, request, pk, *args, **kwargs):
        """Partially update a document."""
        controller = DocumentController()
        result = controller.update_document(request.user, pk, request.data)
        return Response(result['data'], status=result['status'])
    
    def delete(self, request, pk, *args, **kwargs):
        """Delete a document."""
        controller = DocumentController()
        result = controller.delete_document(request.user, pk)
        return Response(result['data'], status=result['status'])


class DocumentCategoriesAPIView(BaseAPIView):
    """
    API to get document categories for a user.
    """
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, *args, **kwargs):
        """Get document categories for the current user."""
        controller = DocumentController()
        result = controller.get_document_categories(request.user)
        return Response(result['data'], status=result['status'])


class DocumentSearchAPIView(BaseAPIView):
    """
    API to search user's documents.
    """
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, *args, **kwargs):
        """Search user's documents."""
        controller = DocumentController()
        result = controller.search_documents(request.user, request)
        return Response(result['data'], status=result['status'])
