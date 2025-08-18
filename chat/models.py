from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel
import uuid


class ChatSession(BaseModel):
    """
    Model to store chat sessions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    is_favorite = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['is_favorite']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"


class ChatMessage(BaseModel):
    """
    Model to store chat messages with integrated RAG functionality.
    Simplified: No separate RAG API needed.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=20, choices=[
        ('user', 'User'),
        ('assistant', 'Assistant')
    ])
    content = models.TextField()
    
    # RAG-specific fields (integrated into chat messages)
    document_category = models.CharField(max_length=100, blank=True, help_text='Category of documents used for RAG response')
    rag_context = models.JSONField(default=dict, blank=True, help_text='Context retrieved from documents')
    rag_sources = models.JSONField(default=list, blank=True, help_text='Sources used for RAG response')
    
    # Standard chat fields
    context = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['sender']),
            models.Index(fields=['document_category']),
        ]
    
    def __str__(self):
        return f"{self.sender}: {self.content[:50]}... - {self.session.title}"
