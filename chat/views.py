from rest_framework import status
from rest_framework.response import Response
from core.views import BaseAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from core.authentication import JWTAuthentication
from .models import ChatSession, ChatMessage
from .serializers import (
    ChatSessionSerializer, ChatMessageSerializer,
    CreateChatSessionSerializer, CreateChatMessageSerializer
)
from .controllers import ChatController
import logging

logger = logging.getLogger(__name__)


class ChatSessionListCreateAPIView(ListCreateAPIView):
    """
    API to list and create chat sessions.
    """
    authentication_classes = [JWTAuthentication]
    serializer_class = ChatSessionSerializer
    
    def get_queryset(self):
        """Get chat sessions for the current user."""
        return ChatSession.objects.filter(user=self.request.user, is_active=True)
    
    def get(self, request, *args, **kwargs):
        """Get all chat sessions for the current user."""
        controller = ChatController()
        result = controller.list_sessions(request.user, request)
        return Response(result, status=result['status'])
    
    def post(self, request, *args, **kwargs):
        """Create a new chat session."""
        controller = ChatController()
        result = controller.create_session(request.user, request.data)
        return Response(result, status=result['status'])


class ChatSessionDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    API to retrieve, update, and delete a specific chat session.
    """
    authentication_classes = [JWTAuthentication]
    serializer_class = ChatSessionSerializer
    
    def get_queryset(self):
        """Get chat sessions for the current user."""
        return ChatSession.objects.filter(user=self.request.user, is_active=True)
    
    def get(self, request, pk, *args, **kwargs):
        """Get a specific chat session."""
        controller = ChatController()
        result = controller.get_session(request.user, pk)
        return Response(result, status=result['status'])
    
    def put(self, request, pk, *args, **kwargs):
        """Update a chat session."""
        controller = ChatController()
        result = controller.update_session(request.user, pk, request.data)
        return Response(result, status=result['status'])
    
    def patch(self, request, pk, *args, **kwargs):
        """Partially update a chat session."""
        controller = ChatController()
        result = controller.update_session(request.user, pk, request.data)
        return Response(result, status=result['status'])
    
    def delete(self, request, pk, *args, **kwargs):
        """Delete a chat session."""
        controller = ChatController()
        result = controller.delete_session(request.user, pk)
        return Response(result, status=result['status'])


class ChatMessageListCreateAPIView(BaseAPIView):
    """
    API to list and create messages in a chat session with integrated RAG.
    """
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, session_id, *args, **kwargs):
        """Get all messages in a chat session."""
        controller = ChatController()
        result = controller.list_messages(request.user, session_id, request)
        return Response(result, status=result['status'])
    
    def post(self, request, session_id, *args, **kwargs):
        """Create a new message with automatic RAG response generation."""
        controller = ChatController()
        result = controller.create_message(request.user, session_id, request.data)
        return Response(result, status=result['status'])
