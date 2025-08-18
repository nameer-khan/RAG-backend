from django.contrib import admin
from .models import KnowledgeBase, Document, DocumentChunk, RAGQuery


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    """
    Admin interface for KnowledgeBase model.
    """
    list_display = [
        'id', 'name', 'user', 'document_count', 'is_active', 'created_at'
    ]
    list_filter = [
        'is_active', 'created_at', 'user'
    ]
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'
    
    def document_count(self, obj):
        return obj.documents.filter(is_active=True).count()
    document_count.short_description = 'Documents'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """
    Admin interface for Document model.
    """
    list_display = [
        'id', 'title', 'knowledge_base', 'file_type', 'chunk_count', 'is_active', 'created_at'
    ]
    list_filter = [
        'file_type', 'is_active', 'created_at', 'knowledge_base__user'
    ]
    search_fields = [
        'title', 'content', 'knowledge_base__name'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'
    
    def chunk_count(self, obj):
        return obj.chunks.filter(is_active=True).count()
    chunk_count.short_description = 'Chunks'


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    """
    Admin interface for DocumentChunk model.
    """
    list_display = [
        'id', 'document', 'chunk_index', 'content_preview', 'embedding_id', 'is_active'
    ]
    list_filter = [
        'is_active', 'created_at', 'document__knowledge_base'
    ]
    search_fields = [
        'content', 'document__title', 'embedding_id'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'


@admin.register(RAGQuery)
class RAGQueryAdmin(admin.ModelAdmin):
    """
    Admin interface for RAGQuery model.
    """
    list_display = [
        'id', 'user', 'query_preview', 'response_preview', 'knowledge_base', 'created_at'
    ]
    list_filter = [
        'created_at', 'user', 'knowledge_base'
    ]
    search_fields = [
        'query', 'response', 'user__username'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'
    
    def query_preview(self, obj):
        return obj.query[:50] + '...' if len(obj.query) > 50 else obj.query
    query_preview.short_description = 'Query'
    
    def response_preview(self, obj):
        return obj.response[:50] + '...' if len(obj.response) > 50 else obj.response
    response_preview.short_description = 'Response'
