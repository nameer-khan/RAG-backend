from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from .models import ChatSession, ChatMessage
from .serializers import (
    ChatSessionSerializer, CreateChatSessionSerializer,
    ChatMessageSerializer, CreateChatMessageSerializer, ChatConversationSerializer
)
import logging

logger = logging.getLogger(__name__)


class ChatController:
    """Controller for chat business logic with integrated RAG functionality"""
    
    def list_sessions(self, user, request):
        """Get all chat sessions for a user"""
        try:
            sessions = ChatSession.objects.filter(user=user, is_active=True)
            serializer = ChatSessionSerializer(sessions, many=True)
            
            return {
                'data': serializer.data,
                'message': 'Chat sessions retrieved successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to retrieve chat sessions: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def create_session(self, user, request_data):
        """Create a new chat session"""
        try:
            serializer = CreateChatSessionSerializer(data=request_data)
            if not serializer.is_valid():
                return {
                    'data': None,
                    'message': 'Invalid data provided',
                    'status': status.HTTP_400_BAD_REQUEST,
                    'errors': serializer.errors
                }
            
            session = serializer.save(user=user)
            response_serializer = ChatSessionSerializer(session)
            
            return {
                'data': response_serializer.data,
                'message': 'Chat session created successfully',
                'status': status.HTTP_201_CREATED
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to create chat session: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def get_session(self, user, session_id):
        """Get a specific chat session"""
        try:
            session = ChatSession.objects.get(id=session_id, user=user, is_active=True)
            serializer = ChatSessionSerializer(session)
            
            return {
                'data': serializer.data,
                'message': 'Chat session retrieved successfully',
                'status': status.HTTP_200_OK
            }
        except ChatSession.DoesNotExist:
            return {
                'data': None,
                'message': 'Chat session not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to retrieve chat session: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def update_session(self, user, session_id, request_data):
        """Update a chat session"""
        try:
            session = ChatSession.objects.get(id=session_id, user=user, is_active=True)
            serializer = ChatSessionSerializer(session, data=request_data, partial=True)
            
            if not serializer.is_valid():
                return {
                    'data': None,
                    'message': 'Invalid data provided',
                    'status': status.HTTP_400_BAD_REQUEST,
                    'errors': serializer.errors
                }
            
            updated_session = serializer.save()
            response_serializer = ChatSessionSerializer(updated_session)
            
            return {
                'data': response_serializer.data,
                'message': 'Chat session updated successfully',
                'status': status.HTTP_200_OK
            }
        except ChatSession.DoesNotExist:
            return {
                'data': None,
                'message': 'Chat session not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to update chat session: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def delete_session(self, user, session_id):
        """Soft delete a chat session"""
        try:
            session = ChatSession.objects.get(id=session_id, user=user, is_active=True)
            session.is_active = False
            session.save()
            
            return {
                'data': None,
                'message': 'Chat session deleted successfully',
                'status': status.HTTP_204_NO_CONTENT
            }
        except ChatSession.DoesNotExist:
            return {
                'data': None,
                'message': 'Chat session not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to delete chat session: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def list_messages(self, user, session_id, request):
        """Get all messages in a chat session"""
        try:
            session = ChatSession.objects.get(id=session_id, user=user, is_active=True)
            messages = session.messages.all()
            serializer = ChatConversationSerializer(messages, many=True)
            
            return {
                'data': serializer.data,
                'message': 'Messages retrieved successfully',
                'status': status.HTTP_200_OK
            }
        except ChatSession.DoesNotExist:
            return {
                'data': None,
                'message': 'Chat session not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to retrieve messages: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def create_message(self, user, session_id, request_data):
        """Create a new message with integrated RAG response"""
        try:
            session = ChatSession.objects.get(id=session_id, user=user, is_active=True)
            
            serializer = CreateChatMessageSerializer(
                data=request_data,
                context={'request': type('Request', (), {'user': user})(), 'session': session}
            )
            
            if not serializer.is_valid():
                return {
                    'data': None,
                    'message': 'Invalid data provided',
                    'status': status.HTTP_400_BAD_REQUEST,
                    'errors': serializer.errors
                }
            
            # The serializer will automatically handle RAG response generation
            message = serializer.save()
            response_serializer = ChatMessageSerializer(message)
            
            return {
                'data': response_serializer.data,
                'message': 'Message sent and response generated successfully',
                'status': status.HTTP_201_CREATED
            }
        except ChatSession.DoesNotExist:
            return {
                'data': None,
                'message': 'Chat session not found',
                'status': status.HTTP_404_NOT_FOUND
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to create message: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
