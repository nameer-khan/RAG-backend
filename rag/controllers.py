from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from .services import RAGPipelineService, OpenAIRAGService
from .serializers import (
    DocumentSerializer, CreateDocumentSerializer, RAGQuerySerializer, RAGQueryListSerializer
)


class RAGController:
    """Controller for RAG pipeline business logic"""
    
    def __init__(self):
        self.rag_service = RAGPipelineService()
        self.openai_service = OpenAIRAGService()
    
    def process_rag_query(self, user, request_data):
        """Process a RAG query with search and generation"""
        try:
            # Validate required fields
            query = request_data.get('query')
            document_category = request_data.get('document_category')
            conversation_history = request_data.get('conversation_history', [])
            
            if not query or not query.strip():
                return {
                    'data': None,
                    'message': 'Query is required',
                    'status': status.HTTP_400_BAD_REQUEST
                }
            
            # Process the RAG query
            result = self.rag_service.process_query(
                user=user,
                query=query.strip(),
                document_category=document_category,
                conversation_history=conversation_history
            )
            
            if not result:
                return {
                    'data': None,
                    'message': 'Failed to process RAG query',
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR
                }
            
            # Return the result directly since it's already a dictionary with the response data
            return {
                'data': result,
                'message': 'RAG query processed successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to process RAG query: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def get_rag_history(self, user, request):
        """Get RAG query history for a user"""
        try:
            # Get pagination parameters
            page = request.query_params.get('page', 1)
            page_size = request.query_params.get('page_size', 20)
            document_category = request.query_params.get('document_category')
            
            try:
                page = int(page)
                page_size = int(page_size)
            except ValueError:
                return {
                    'data': None,
                    'message': 'Invalid pagination parameters',
                    'status': status.HTTP_400_BAD_REQUEST
                }
            
            queries, total_count = self.rag_service.get_user_rag_history(
                user=user,
                page=page,
                page_size=page_size,
                document_category=document_category
            )
            
            serializer = RAGQueryListSerializer(queries, many=True)
            
            # Calculate pagination metadata
            total_pages = (total_count + page_size - 1) // page_size
            
            meta = {
                'pagination': {
                    'current_page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_previous': page > 1
                }
            }
            
            return {
                'data': serializer.data,
                'message': 'RAG history retrieved successfully',
                'status': status.HTTP_200_OK,
                'meta': meta
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to retrieve RAG history: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }


class DocumentController:
    """Controller for document management business logic"""
    
    def __init__(self):
        self.rag_service = RAGPipelineService()
    
    def list_documents(self, user, request):
        """Get all documents for a user"""
        try:
            # Get pagination and filter parameters
            page = request.query_params.get('page', 1)
            page_size = request.query_params.get('page_size', 20)
            category = request.query_params.get('category')
            
            try:
                page = int(page)
                page_size = int(page_size)
            except ValueError:
                return {
                    'data': None,
                    'message': 'Invalid pagination parameters',
                    'status': status.HTTP_400_BAD_REQUEST
                }
            
            documents, total_count = self.rag_service.get_user_documents(
                user=user,
                category=category,
                page=page,
                page_size=page_size
            )
            
            serializer = DocumentSerializer(documents, many=True)
            
            # Calculate pagination metadata
            total_pages = (total_count + page_size - 1) // page_size
            
            meta = {
                'pagination': {
                    'current_page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_previous': page > 1
                }
            }
            
            return {
                'data': serializer.data,
                'message': 'Documents retrieved successfully',
                'status': status.HTTP_200_OK,
                'meta': meta
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to retrieve documents: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def create_document(self, user, request_data):
        """Create a new document"""
        try:
            serializer = CreateDocumentSerializer(data=request_data)
            if not serializer.is_valid():
                return {
                    'data': None,
                    'message': 'Invalid data provided',
                    'status': status.HTTP_400_BAD_REQUEST,
                    'errors': serializer.errors
                }
            
            document = self.rag_service.add_document(
                user=user,
                title=serializer.validated_data['title'],
                content=serializer.validated_data['content'],
                category=serializer.validated_data.get('category', 'general'),
                source_url=serializer.validated_data.get('source_url'),
                metadata=serializer.validated_data.get('metadata')
            )
            
            response_serializer = DocumentSerializer(document)
            return {
                'data': response_serializer.data,
                'message': 'Document created successfully',
                'status': status.HTTP_201_CREATED
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to create document: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def get_document(self, user, doc_id):
        """Get a specific document"""
        try:
            document = self.rag_service.get_document_by_id(doc_id, user)
            if not document:
                return {
                    'data': None,
                    'message': 'Document not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            serializer = DocumentSerializer(document)
            return {
                'data': serializer.data,
                'message': 'Document retrieved successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to retrieve document: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def update_document(self, user, doc_id, request_data):
        """Update a document"""
        try:
            document = self.rag_service.get_document_by_id(doc_id, user)
            if not document:
                return {
                    'data': None,
                    'message': 'Document not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            serializer = DocumentSerializer(document, data=request_data, partial=True)
            if not serializer.is_valid():
                return {
                    'data': None,
                    'message': 'Invalid data provided',
                    'status': status.HTTP_400_BAD_REQUEST,
                    'errors': serializer.errors
                }
            
            updated_document = self.rag_service.update_document(document, **serializer.validated_data)
            response_serializer = DocumentSerializer(updated_document)
            
            return {
                'data': response_serializer.data,
                'message': 'Document updated successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to update document: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def delete_document(self, user, doc_id):
        """Soft delete a document"""
        try:
            document = self.rag_service.get_document_by_id(doc_id, user)
            if not document:
                return {
                    'data': None,
                    'message': 'Document not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            self.rag_service.delete_document(document)
            return {
                'data': None,
                'message': 'Document deleted successfully',
                'status': status.HTTP_204_NO_CONTENT
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to delete document: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def get_document_categories(self, user):
        """Get document categories for a user"""
        try:
            categories = self.rag_service.get_document_categories(user)
            return {
                'data': {'categories': categories},
                'message': 'Document categories retrieved successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to retrieve document categories: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def search_documents(self, user, request):
        """Search user's documents"""
        try:
            query = request.query_params.get('query', '').strip()
            category = request.query_params.get('category')
            limit = request.query_params.get('limit', 10)
            
            if not query:
                return {
                    'data': None,
                    'message': 'Search query is required',
                    'status': status.HTTP_400_BAD_REQUEST
                }
            
            try:
                limit = int(limit)
            except ValueError:
                limit = 10
            
            documents = self.rag_service.search_user_documents(
                user=user,
                query=query,
                category=category,
                limit=limit
            )
            
            serializer = DocumentSerializer(documents, many=True)
            return {
                'data': serializer.data,
                'message': f'Found {len(documents)} documents matching "{query}"',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to search documents: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
