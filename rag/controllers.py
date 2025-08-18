from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from .services import RAGPipelineService, KnowledgeBaseService, NubiousRAGService
from .serializers import (
    KnowledgeBaseSerializer, CreateKnowledgeBaseSerializer, DocumentSerializer,
    CreateDocumentSerializer, RAGQuerySerializer, RAGQueryListSerializer
)


class RAGController:
    """Controller for RAG pipeline business logic"""
    
    def __init__(self):
        self.rag_service = RAGPipelineService()
        self.nubious_service = NubiousRAGService()
    
    def process_rag_query(self, user, request_data):
        """Process a RAG query with search and generation"""
        try:
            # Validate required fields
            query = request_data.get('query')
            knowledge_base_id = request_data.get('knowledge_base_id')
            conversation_history = request_data.get('conversation_history', [])
            
            if not query or not query.strip():
                return {
                    'data': None,
                    'message': 'Query is required',
                    'status': status.HTTP_400_BAD_REQUEST
                }
            
            if not knowledge_base_id:
                return {
                    'data': None,
                    'message': 'Knowledge base ID is required',
                    'status': status.HTTP_400_BAD_REQUEST
                }
            
            # Process the RAG query
            result = self.rag_service.process_query(
                user=user,
                query=query.strip(),
                knowledge_base_id=knowledge_base_id,
                conversation_history=conversation_history
            )
            
            if not result:
                return {
                    'data': None,
                    'message': 'Failed to process RAG query',
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR
                }
            
            serializer = RAGQuerySerializer(result)
            return {
                'data': serializer.data,
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
            knowledge_base_id = request.query_params.get('knowledge_base_id')
            
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
                knowledge_base_id=knowledge_base_id
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


class KnowledgeBaseController:
    """Controller for knowledge base business logic"""
    
    def __init__(self):
        self.kb_service = KnowledgeBaseService()
    
    def list_knowledge_bases(self, user, request):
        """Get all knowledge bases for a user"""
        try:
            knowledge_bases = self.kb_service.get_user_knowledge_bases(user)
            serializer = KnowledgeBaseSerializer(knowledge_bases, many=True)
            
            return {
                'data': serializer.data,
                'message': 'Knowledge bases retrieved successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to retrieve knowledge bases: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def create_knowledge_base(self, user, request_data):
        """Create a new knowledge base"""
        try:
            serializer = CreateKnowledgeBaseSerializer(data=request_data)
            if not serializer.is_valid():
                return {
                    'data': None,
                    'message': 'Invalid data provided',
                    'status': status.HTTP_400_BAD_REQUEST,
                    'errors': serializer.errors
                }
            
            knowledge_base = self.kb_service.create_knowledge_base(
                user=user,
                name=serializer.validated_data['name'],
                description=serializer.validated_data.get('description', '')
            )
            
            response_serializer = KnowledgeBaseSerializer(knowledge_base)
            return {
                'data': response_serializer.data,
                'message': 'Knowledge base created successfully',
                'status': status.HTTP_201_CREATED
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to create knowledge base: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def get_knowledge_base(self, user, kb_id):
        """Get a specific knowledge base"""
        try:
            knowledge_base = self.kb_service.get_knowledge_base_by_id(kb_id, user)
            if not knowledge_base:
                return {
                    'data': None,
                    'message': 'Knowledge base not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            serializer = KnowledgeBaseSerializer(knowledge_base)
            return {
                'data': serializer.data,
                'message': 'Knowledge base retrieved successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to retrieve knowledge base: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def update_knowledge_base(self, user, kb_id, request_data):
        """Update a knowledge base"""
        try:
            knowledge_base = self.kb_service.get_knowledge_base_by_id(kb_id, user)
            if not knowledge_base:
                return {
                    'data': None,
                    'message': 'Knowledge base not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            serializer = KnowledgeBaseSerializer(knowledge_base, data=request_data, partial=True)
            if not serializer.is_valid():
                return {
                    'data': None,
                    'message': 'Invalid data provided',
                    'status': status.HTTP_400_BAD_REQUEST,
                    'errors': serializer.errors
                }
            
            updated_kb = self.kb_service.update_knowledge_base(knowledge_base, serializer.validated_data)
            response_serializer = KnowledgeBaseSerializer(updated_kb)
            
            return {
                'data': response_serializer.data,
                'message': 'Knowledge base updated successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to update knowledge base: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def delete_knowledge_base(self, user, kb_id):
        """Soft delete a knowledge base"""
        try:
            knowledge_base = self.kb_service.get_knowledge_base_by_id(kb_id, user)
            if not knowledge_base:
                return {
                    'data': None,
                    'message': 'Knowledge base not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            self.kb_service.delete_knowledge_base(knowledge_base)
            return {
                'data': None,
                'message': 'Knowledge base deleted successfully',
                'status': status.HTTP_204_NO_CONTENT
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to delete knowledge base: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }


class DocumentController:
    """Controller for document management business logic"""
    
    def __init__(self):
        self.rag_service = RAGPipelineService()
        self.kb_service = KnowledgeBaseService()
    
    def list_documents(self, user, kb_id, request):
        """Get all documents in a knowledge base"""
        try:
            knowledge_base = self.kb_service.get_knowledge_base_by_id(kb_id, user)
            if not knowledge_base:
                return {
                    'data': None,
                    'message': 'Knowledge base not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            documents = self.rag_service.get_knowledge_base_documents(knowledge_base)
            serializer = DocumentSerializer(documents, many=True)
            
            return {
                'data': serializer.data,
                'message': 'Documents retrieved successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to retrieve documents: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def add_document(self, user, kb_id, request_data):
        """Add a document to a knowledge base and create embeddings"""
        try:
            knowledge_base = self.kb_service.get_knowledge_base_by_id(kb_id, user)
            if not knowledge_base:
                return {
                    'data': None,
                    'message': 'Knowledge base not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            serializer = CreateDocumentSerializer(data=request_data)
            if not serializer.is_valid():
                return {
                    'data': None,
                    'message': 'Invalid data provided',
                    'status': status.HTTP_400_BAD_REQUEST,
                    'errors': serializer.errors
                }
            
            # Add document and create embeddings
            document = self.rag_service.add_document_to_knowledge_base(
                knowledge_base=knowledge_base,
                title=serializer.validated_data['title'],
                content=serializer.validated_data['content'],
                source_url=serializer.validated_data.get('source_url'),
                metadata=serializer.validated_data.get('metadata')
            )
            
            response_serializer = DocumentSerializer(document)
            return {
                'data': response_serializer.data,
                'message': 'Document added and embeddings created successfully',
                'status': status.HTTP_201_CREATED
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to add document: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def get_document(self, user, kb_id, doc_id):
        """Get a specific document"""
        try:
            knowledge_base = self.kb_service.get_knowledge_base_by_id(kb_id, user)
            if not knowledge_base:
                return {
                    'data': None,
                    'message': 'Knowledge base not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            document = self.rag_service.get_document_by_id(doc_id, knowledge_base)
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
    
    def update_document(self, user, kb_id, doc_id, request_data):
        """Update a document and regenerate embeddings"""
        try:
            knowledge_base = self.kb_service.get_knowledge_base_by_id(kb_id, user)
            if not knowledge_base:
                return {
                    'data': None,
                    'message': 'Knowledge base not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            document = self.rag_service.get_document_by_id(doc_id, knowledge_base)
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
            
            updated_document = self.rag_service.update_document_and_embeddings(
                document, serializer.validated_data
            )
            response_serializer = DocumentSerializer(updated_document)
            
            return {
                'data': response_serializer.data,
                'message': 'Document updated and embeddings regenerated successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to update document: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def delete_document(self, user, kb_id, doc_id):
        """Soft delete a document"""
        try:
            knowledge_base = self.kb_service.get_knowledge_base_by_id(kb_id, user)
            if not knowledge_base:
                return {
                    'data': None,
                    'message': 'Knowledge base not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            document = self.rag_service.get_document_by_id(doc_id, knowledge_base)
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
