from django.contrib import admin
from .models import ChatSession, ChatMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """
    Admin interface for ChatSession model.
    """
    list_display = [
        'id', 'title', 'user', 'is_favorite', 'message_count',
        'last_message_at', 'is_active', 'created_at'
    ]
    list_filter = [
        'is_favorite', 'is_active', 'created_at', 'last_message_at', 'user'
    ]
    search_fields = ['title', 'user__username', 'user__email']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'last_message_at', 'message_count'
    ]
    date_hierarchy = 'created_at'
    
    def message_count(self, obj):
        return obj.message_count
    message_count.short_description = 'Messages'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for ChatMessage model.
    """
    list_display = [
        'id', 'session', 'sender', 'content_preview', 'created_at', 'is_active'
    ]
    list_filter = [
        'sender', 'is_active', 'created_at', 'session__user'
    ]
    search_fields = [
        'content', 'session__title', 'session__user__username'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'
