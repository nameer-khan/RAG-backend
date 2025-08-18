from rest_framework import status
from django.shortcuts import get_object_or_404
from core.views import BaseAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from core.authentication import JWTAuthentication
from .models import ChatSession, ChatMessage
from .serializers import (
    ChatSessionSerializer, ChatSessionListSerializer, CreateChatSessionSerializer,
    UpdateChatSessionSerializer, ChatMessageSerializer, CreateChatMessageSerializer,
    ChatMessageListSerializer
)
from .services import ChatSessionService, ChatMessageService
from .controllers import ChatSessionController, ChatMessageController
import logging

logger = logging.getLogger(__name__)


class ChatSessionListCreateAPIView(BaseAPIView):
    """
    API to list and create chat sessions.
    """
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, *args, **kwargs):
        """Get all chat sessions for the current user."""
        controller = ChatSessionController()
        result = controller.list_sessions(request.user, request)
        return Response(result['data'], status=result['status'])
    
    def post(self, request, *args, **kwargs):
        """Create a new chat session."""
        controller = ChatSessionController()
        result = controller.create_session(request.user, request.data)
        return Response(result['data'], status=result['status'])


class ChatSessionDetailAPIView(BaseAPIView):
    """
    API to retrieve, update, and delete a specific chat session.
    """
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, session_id, *args, **kwargs):
        """Get a specific chat session."""
        controller = ChatSessionController()
        result = controller.get_session(request.user, session_id)
        return Response(result['data'], status=result['status'])
    
    def put(self, request, session_id, *args, **kwargs):
        """Update a chat session."""
        controller = ChatSessionController()
        result = controller.update_session(request.user, session_id, request.data)
        return Response(result['data'], status=result['status'])
    
    def patch(self, request, session_id, *args, **kwargs):
        """Partially update a chat session."""
        controller = ChatSessionController()
        result = controller.update_session(request.user, session_id, request.data)
        return Response(result['data'], status=result['status'])
    
    def delete(self, request, session_id, *args, **kwargs):
        """Delete a chat session."""
        controller = ChatSessionController()
        result = controller.delete_session(request.user, session_id)
        return Response(result['data'], status=result['status'])


class ChatSessionRenameAPIView(BaseAPIView):
    """
    API to rename a chat session.
    """
    authentication_classes = [JWTAuthentication]
    
    def patch(self, request, session_id, *args, **kwargs):
        """Rename a chat session."""
        controller = ChatSessionController()
        new_title = request.data.get('title')
        result = controller.rename_session(request.user, session_id, new_title)
        return Response(result['data'], status=result['status'])


class ChatSessionToggleFavoriteAPIView(BaseAPIView):
    """
    API to toggle favorite status of a chat session.
    """
    authentication_classes = [JWTAuthentication]
    
    def patch(self, request, session_id, *args, **kwargs):
        """Toggle favorite status of a chat session."""
        controller = ChatSessionController()
        result = controller.toggle_favorite(request.user, session_id)
        return Response(result['data'], status=result['status'])


class ChatMessageListCreateAPIView(BaseAPIView):
    """
    API to list and create chat messages for a session.
    """
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, session_id, *args, **kwargs):
        """Get all messages in a chat session."""
        controller = ChatMessageController()
        result = controller.list_messages(request.user, session_id, request)
        return Response(result['data'], status=result['status'])
    
    def post(self, request, session_id, *args, **kwargs):
        """Create a new chat message."""
        controller = ChatMessageController()
        result = controller.create_message(request.user, session_id, request.data)
        return Response(result['data'], status=result['status'])


class ChatMessageDetailAPIView(BaseAPIView):
    """
    API to retrieve, update, and delete a specific chat message.
    """
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, session_id, message_id, *args, **kwargs):
        """Get a specific message."""
        controller = ChatMessageController()
        result = controller.get_message(request.user, session_id, message_id)
        return Response(result['data'], status=result['status'])
    
    def put(self, request, session_id, message_id, *args, **kwargs):
        """Update a message."""
        controller = ChatMessageController()
        result = controller.update_message(request.user, session_id, message_id, request.data)
        return Response(result['data'], status=result['status'])
    
    def patch(self, request, session_id, message_id, *args, **kwargs):
        """Partially update a message."""
        controller = ChatMessageController()
        result = controller.update_message(request.user, session_id, message_id, request.data)
        return Response(result['data'], status=result['status'])
    
    def delete(self, request, session_id, message_id, *args, **kwargs):
        """Delete a message."""
        controller = ChatMessageController()
        result = controller.delete_message(request.user, session_id, message_id)
        return Response(result['data'], status=result['status'])


class ChatConversationHistoryAPIView(BaseAPIView):
    """
    API to get conversation history for a chat session with pagination.
    """
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, session_id, *args, **kwargs):
        """Get conversation history for a chat session."""
        controller = ChatMessageController()
        result = controller.get_conversation_history(request.user, session_id, request)
        return Response(result['data'], status=result['status'])
