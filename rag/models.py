from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel
import uuid


class KnowledgeBase(BaseModel):
    """
    Model to store knowledge base information for RAG.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='knowledge_bases')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'knowledge_bases'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"


class Document(BaseModel):
    """
    Model to store documents in the knowledge base.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    content = models.TextField()
    file_path = models.CharField(max_length=500, blank=True)
    file_type = models.CharField(max_length=50, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['knowledge_base', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.knowledge_base.name}"


class DocumentChunk(BaseModel):
    """
    Model to store document chunks for vector search.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    content = models.TextField()
    chunk_index = models.IntegerField()
    embedding_id = models.CharField(max_length=255, blank=True, help_text="ID in the vector database")
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'document_chunks'
        ordering = ['document', 'chunk_index']
        indexes = [
            models.Index(fields=['document', 'is_active']),
            models.Index(fields=['embedding_id']),
        ]
    
    def __str__(self):
        return f"Chunk {self.chunk_index} - {self.document.title}"


class RAGQuery(BaseModel):
    """
    Model to store RAG queries and their results.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rag_queries')
    query = models.TextField()
    response = models.TextField()
    retrieved_context = models.JSONField(default=dict, blank=True)
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.SET_NULL, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'rag_queries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['knowledge_base', 'created_at']),
        ]
    
    def __str__(self):
        return f"Query: {self.query[:50]}... - {self.user.username}"
