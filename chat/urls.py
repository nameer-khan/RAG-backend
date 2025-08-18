from django.urls import path
from .views import (
    ChatSessionListCreateAPIView,
    ChatSessionDetailAPIView,
    ChatSessionRenameAPIView,
    ChatSessionToggleFavoriteAPIView,
    ChatMessageListCreateAPIView,
    ChatMessageDetailAPIView,
    ChatConversationHistoryAPIView,
)

urlpatterns = [
    # Chat Sessions
    path('sessions/', ChatSessionListCreateAPIView.as_view(), name='chat-session-list-create'),
    path('sessions/<uuid:pk>/', ChatSessionDetailAPIView.as_view(), name='chat-session-detail'),
    path('sessions/<uuid:session_id>/rename/', ChatSessionRenameAPIView.as_view(), name='chat-session-rename'),
    path('sessions/<uuid:session_id>/toggle-favorite/', ChatSessionToggleFavoriteAPIView.as_view(), name='chat-session-toggle-favorite'),
    
    # Chat Messages
    path('sessions/<uuid:session_id>/messages/', ChatMessageListCreateAPIView.as_view(), name='chat-message-list-create'),
    path('sessions/<uuid:session_id>/messages/<uuid:pk>/', ChatMessageDetailAPIView.as_view(), name='chat-message-detail'),
    
    # Conversation History
    path('sessions/<uuid:session_id>/history/', ChatConversationHistoryAPIView.as_view(), name='chat-conversation-history'),
]
