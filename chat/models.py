from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel
import uuid


class ChatSession(BaseModel):
    """
    Model to store chat sessions for users.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, default="New Chat")
    is_favorite = models.BooleanField(default=False)
    last_message_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-last_message_at', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['user', 'is_favorite']),
            models.Index(fields=['last_message_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def update_last_message_time(self):
        """Update the last message timestamp."""
        from django.utils import timezone
        self.last_message_at = timezone.now()
        self.save(update_fields=['last_message_at'])
    
    @property
    def message_count(self):
        """Get the count of messages in this session."""
        return self.messages.filter(is_active=True).count()


class ChatMessage(BaseModel):
    """
    Model to store individual chat messages within sessions.
    """
    SENDER_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    context = models.JSONField(default=dict, blank=True, help_text="Retrieved context for RAG responses")
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional metadata about the message")
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender} - {self.content[:50]}..."
    
    def save(self, *args, **kwargs):
        """Override save to update session's last message time."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.session.update_last_message_time()
    
    @property
    def formatted_content(self):
        """Get formatted content with context if available."""
        if self.context and self.sender == 'assistant':
            context_info = f"\n\n**Retrieved Context:**\n{self.context.get('sources', [])}"
            return self.content + context_info
        return self.content
