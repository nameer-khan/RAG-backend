from rest_framework import serializers
from core.serializers import BaseModelSerializer, UserSerializer
from .models import KnowledgeBase, Document, DocumentChunk, RAGQuery


class KnowledgeBaseSerializer(BaseModelSerializer):
    """
    Serializer for KnowledgeBase model.
    """
    user = UserSerializer(read_only=True)
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeBase
        fields = [
            'id', 'user', 'name', 'description', 'is_active',
            'document_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_document_count(self, obj):
        """Get the count of documents in this knowledge base."""
        return obj.documents.filter(is_active=True).count()
    
    def create(self, validated_data):
        """Override create to set the user automatically."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class CreateKnowledgeBaseSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new knowledge bases.
    """
    class Meta:
        model = KnowledgeBase
        fields = ['name', 'description']
    
    def create(self, validated_data):
        """Override create to set the user automatically."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class DocumentSerializer(BaseModelSerializer):
    """
    Serializer for Document model.
    """
    knowledge_base = KnowledgeBaseSerializer(read_only=True)
    chunk_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'knowledge_base', 'title', 'content', 'file_path',
            'file_type', 'metadata', 'chunk_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'knowledge_base', 'created_at', 'updated_at']
    
    def get_chunk_count(self, obj):
        """Get the count of chunks for this document."""
        return obj.chunks.filter(is_active=True).count()


class CreateDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new documents.
    """
    class Meta:
        model = Document
        fields = ['title', 'content', 'file_path', 'file_type', 'metadata']
    
    def create(self, validated_data):
        """Override create to set the knowledge base automatically."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['knowledge_base'] = self.context.get('knowledge_base')
        return super().create(validated_data)


class DocumentChunkSerializer(BaseModelSerializer):
    """
    Serializer for DocumentChunk model.
    """
    document = DocumentSerializer(read_only=True)
    
    class Meta:
        model = DocumentChunk
        fields = [
            'id', 'document', 'content', 'chunk_index', 'embedding_id',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'document', 'created_at', 'updated_at']


class RAGQuerySerializer(BaseModelSerializer):
    """
    Serializer for RAGQuery model.
    """
    user = UserSerializer(read_only=True)
    knowledge_base = KnowledgeBaseSerializer(read_only=True)
    
    class Meta:
        model = RAGQuery
        fields = [
            'id', 'user', 'query', 'response', 'retrieved_context',
            'knowledge_base', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class RAGQueryListSerializer(BaseModelSerializer):
    """
    Simplified serializer for listing RAG queries.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = RAGQuery
        fields = [
            'id', 'user', 'query', 'response', 'knowledge_base',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
