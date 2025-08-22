from django.urls import path
from .views import (
    ChatSessionListCreateAPIView,
    ChatSessionDetailAPIView,
    ChatSessionRenameAPIView,
    ChatSessionFavoriteAPIView,
    ChatMessageListCreateAPIView,
)

urlpatterns = [
    # Chat Sessions
    path('sessions/', ChatSessionListCreateAPIView.as_view(), name='chat-session-list-create'),
    path('sessions/<uuid:pk>/', ChatSessionDetailAPIView.as_view(), name='chat-session-detail'),
    path('sessions/<uuid:pk>/rename/', ChatSessionRenameAPIView.as_view(), name='chat-session-rename'),
    path('sessions/<uuid:pk>/favorite/', ChatSessionFavoriteAPIView.as_view(), name='chat-session-favorite'),
    
    # Chat Messages (with integrated RAG)
    path('sessions/<uuid:session_id>/messages/', ChatMessageListCreateAPIView.as_view(), name='chat-message-list-create'),
]
