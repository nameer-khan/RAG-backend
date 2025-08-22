from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel
import uuid


class Document(BaseModel):
    """
    Model to store documents for RAG processing.
    Simplified: No separate knowledge base, just documents with categories.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=100, default='general', help_text='Document category for organization')
    source_url = models.URLField(blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"


class DocumentChunk(BaseModel):
    """
    Model to store document chunks with embeddings for RAG.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    content = models.TextField()
    chunk_index = models.IntegerField()
    embedding_id = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'document_chunks'
        ordering = ['chunk_index']
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
        ]
    
    def __str__(self):
        return f"Chunk {self.chunk_index} of {self.document.title}"


class RAGQuery(BaseModel):
    """
    Model to store RAG queries and responses.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rag_queries')
    query = models.TextField()
    response = models.TextField()
    document_category = models.CharField(max_length=100, blank=True, help_text='Category of documents used for this query')
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'rag_queries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['document_category']),
        ]
    
    def __str__(self):
        return f"Query: {self.query[:50]}... - {self.user.username}"
