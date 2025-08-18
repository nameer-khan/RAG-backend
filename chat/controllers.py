from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from .services import ChatSessionService, ChatMessageService
from .serializers import (
    ChatSessionSerializer, ChatSessionListSerializer, CreateChatSessionSerializer,
    UpdateChatSessionSerializer, ChatMessageSerializer, CreateChatMessageSerializer,
    ChatMessageListSerializer
)


class ChatSessionController:
    """Controller for chat session business logic"""
    
    def __init__(self):
        self.session_service = ChatSessionService()
    
    def list_sessions(self, user, request):
        """Get all chat sessions for a user"""
        try:
            sessions = self.session_service.get_user_sessions(user)
            serializer = ChatSessionListSerializer(sessions, many=True)
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
            
            session = self.session_service.create_session(
                user=user,
                title=serializer.validated_data.get('title', 'New Chat')
            )
            
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
            session = self.session_service.get_session_by_id(session_id, user)
            if not session:
                return {
                    'data': None,
                    'message': 'Chat session not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            serializer = ChatSessionSerializer(session)
            return {
                'data': serializer.data,
                'message': 'Chat session retrieved successfully',
                'status': status.HTTP_200_OK
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
            session = self.session_service.get_session_by_id(session_id, user)
            if not session:
                return {
                    'data': None,
                    'message': 'Chat session not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            serializer = UpdateChatSessionSerializer(session, data=request_data, partial=True)
            if not serializer.is_valid():
                return {
                    'data': None,
                    'message': 'Invalid data provided',
                    'status': status.HTTP_400_BAD_REQUEST,
                    'errors': serializer.errors
                }
            
            updated_session = self.session_service.update_session(session, serializer.validated_data)
            response_serializer = ChatSessionSerializer(updated_session)
            
            return {
                'data': response_serializer.data,
                'message': 'Chat session updated successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to update chat session: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def delete_session(self, user, session_id):
        """Soft delete a chat session and its messages"""
        try:
            session = self.session_service.get_session_by_id(session_id, user)
            if not session:
                return {
                    'data': None,
                    'message': 'Chat session not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            self.session_service.delete_session(session)
            return {
                'data': None,
                'message': 'Chat session deleted successfully',
                'status': status.HTTP_204_NO_CONTENT
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to delete chat session: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def rename_session(self, user, session_id, new_title):
        """Rename a chat session"""
        try:
            session = self.session_service.get_session_by_id(session_id, user)
            if not session:
                return {
                    'data': None,
                    'message': 'Chat session not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            if not new_title or new_title.strip() == '':
                return {
                    'data': None,
                    'message': 'Title cannot be empty',
                    'status': status.HTTP_400_BAD_REQUEST
                }
            
            updated_session = self.session_service.rename_session(session, new_title.strip())
            serializer = ChatSessionSerializer(updated_session)
            
            return {
                'data': serializer.data,
                'message': 'Chat session renamed successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to rename chat session: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def toggle_favorite(self, user, session_id):
        """Toggle favorite status of a chat session"""
        try:
            session = self.session_service.get_session_by_id(session_id, user)
            if not session:
                return {
                    'data': None,
                    'message': 'Chat session not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            updated_session = self.session_service.toggle_favorite(session)
            serializer = ChatSessionSerializer(updated_session)
            
            action = 'marked as favorite' if updated_session.is_favorite else 'unmarked as favorite'
            return {
                'data': serializer.data,
                'message': f'Chat session {action} successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to toggle favorite status: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }


class ChatMessageController:
    """Controller for chat message business logic"""
    
    def __init__(self):
        self.message_service = ChatMessageService()
        self.session_service = ChatSessionService()
    
    def list_messages(self, user, session_id, request):
        """Get all messages in a chat session"""
        try:
            session = self.session_service.get_session_by_id(session_id, user)
            if not session:
                return {
                    'data': None,
                    'message': 'Chat session not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            messages = self.message_service.get_session_messages(session)
            serializer = ChatMessageListSerializer(messages, many=True)
            
            return {
                'data': serializer.data,
                'message': 'Messages retrieved successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to retrieve messages: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def create_message(self, user, session_id, request_data):
        """Add a new message to a chat session"""
        try:
            session = self.session_service.get_session_by_id(session_id, user)
            if not session:
                return {
                    'data': None,
                    'message': 'Chat session not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            serializer = CreateChatMessageSerializer(data=request_data)
            if not serializer.is_valid():
                return {
                    'data': None,
                    'message': 'Invalid data provided',
                    'status': status.HTTP_400_BAD_REQUEST,
                    'errors': serializer.errors
                }
            
            message = self.message_service.add_message(
                session=session,
                sender=serializer.validated_data['sender'],
                content=serializer.validated_data['content'],
                context=serializer.validated_data.get('context'),
                metadata=serializer.validated_data.get('metadata')
            )
            
            response_serializer = ChatMessageSerializer(message)
            return {
                'data': response_serializer.data,
                'message': 'Message added successfully',
                'status': status.HTTP_201_CREATED
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to add message: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def get_message(self, user, session_id, message_id):
        """Get a specific message"""
        try:
            session = self.session_service.get_session_by_id(session_id, user)
            if not session:
                return {
                    'data': None,
                    'message': 'Chat session not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            message = self.message_service.get_message_by_id(message_id, session)
            if not message:
                return {
                    'data': None,
                    'message': 'Message not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            serializer = ChatMessageSerializer(message)
            return {
                'data': serializer.data,
                'message': 'Message retrieved successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to retrieve message: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def update_message(self, user, session_id, message_id, request_data):
        """Update a message"""
        try:
            session = self.session_service.get_session_by_id(session_id, user)
            if not session:
                return {
                    'data': None,
                    'message': 'Chat session not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            message = self.message_service.get_message_by_id(message_id, session)
            if not message:
                return {
                    'data': None,
                    'message': 'Message not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            serializer = ChatMessageSerializer(message, data=request_data, partial=True)
            if not serializer.is_valid():
                return {
                    'data': None,
                    'message': 'Invalid data provided',
                    'status': status.HTTP_400_BAD_REQUEST,
                    'errors': serializer.errors
                }
            
            updated_message = self.message_service.update_message(message, serializer.validated_data)
            response_serializer = ChatMessageSerializer(updated_message)
            
            return {
                'data': response_serializer.data,
                'message': 'Message updated successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to update message: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def delete_message(self, user, session_id, message_id):
        """Soft delete a message"""
        try:
            session = self.session_service.get_session_by_id(session_id, user)
            if not session:
                return {
                    'data': None,
                    'message': 'Chat session not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            message = self.message_service.get_message_by_id(message_id, session)
            if not message:
                return {
                    'data': None,
                    'message': 'Message not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            self.message_service.delete_message(message)
            return {
                'data': None,
                'message': 'Message deleted successfully',
                'status': status.HTTP_204_NO_CONTENT
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to delete message: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
    
    def get_conversation_history(self, user, session_id, request):
        """Get conversation history with pagination"""
        try:
            session = self.session_service.get_session_by_id(session_id, user)
            if not session:
                return {
                    'data': None,
                    'message': 'Chat session not found',
                    'status': status.HTTP_404_NOT_FOUND
                }
            
            # Get pagination parameters
            page = request.query_params.get('page', 1)
            page_size = request.query_params.get('page_size', 20)
            
            try:
                page = int(page)
                page_size = int(page_size)
            except ValueError:
                return {
                    'data': None,
                    'message': 'Invalid pagination parameters',
                    'status': status.HTTP_400_BAD_REQUEST
                }
            
            messages, total_count = self.message_service.get_conversation_history(
                session, page=page, page_size=page_size
            )
            
            serializer = ChatMessageListSerializer(messages, many=True)
            
            # Calculate pagination metadata
            total_pages = (total_count + page_size - 1) // page_size
            
            meta = {
                'pagination': {
                    'current_page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_previous': page > 1
                }
            }
            
            return {
                'data': serializer.data,
                'message': 'Conversation history retrieved successfully',
                'status': status.HTTP_200_OK,
                'meta': meta
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to retrieve conversation history: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
