from django.contrib import admin
from .models import Document, DocumentChunk, RAGQuery


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'content', 'user__username')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('document', 'chunk_index', 'embedding_id', 'created_at')
    list_filter = ('chunk_index', 'created_at')
    search_fields = ('document__title', 'content')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('document', 'chunk_index')


@admin.register(RAGQuery)
class RAGQueryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'document_category', 'is_active', 'created_at')
    list_filter = ('document_category', 'is_active', 'created_at')
    search_fields = ('query', 'response', 'user__username')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
