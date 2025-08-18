from rest_framework import serializers
from core.serializers import BaseModelSerializer, UserSerializer
from .models import Document, DocumentChunk, RAGQuery


class DocumentSerializer(BaseModelSerializer):
    """
    Serializer for Document model.
    """
    user = UserSerializer(read_only=True)
    chunk_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'user', 'title', 'content', 'category', 'source_url', 
            'file_path', 'metadata', 'is_active', 'chunk_count', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'chunk_count', 'created_at', 'updated_at']
    
    def get_chunk_count(self, obj):
        """Get the count of chunks in this document."""
        return obj.chunks.count()
    
    def create(self, validated_data):
        """Override create to set the user automatically."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class CreateDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new documents.
    """
    class Meta:
        model = Document
        fields = ['title', 'content', 'category', 'source_url', 'metadata']
        extra_kwargs = {
            'category': {'required': False},
            'source_url': {'required': False},
            'metadata': {'required': False},
        }


class RAGQuerySerializer(BaseModelSerializer):
    """
    Serializer for RAGQuery model.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = RAGQuery
        fields = [
            'id', 'user', 'query', 'response', 'document_category', 
            'metadata', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'response', 'created_at', 'updated_at']


class RAGQueryListSerializer(BaseModelSerializer):
    """
    Serializer for listing RAG queries (simplified version).
    """
    class Meta:
        model = RAGQuery
        fields = [
            'id', 'query', 'response', 'document_category', 
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DocumentChunkSerializer(BaseModelSerializer):
    """
    Serializer for DocumentChunk model.
    """
    class Meta:
        model = DocumentChunk
        fields = [
            'id', 'document', 'content', 'chunk_index', 
            'embedding_id', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
