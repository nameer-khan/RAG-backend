from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer
import logging

logger = logging.getLogger(__name__)


class ChatSessionService:
    """
    Service class for chat session operations.
    """
    
    def create_session(self, user, title="New Chat"):
        """
        Create a new chat session for a user.
        """
        try:
            with transaction.atomic():
                session = ChatSession.objects.create(
                    user=user,
                    title=title
                )
                logger.info(f"Created chat session {session.id} for user {user.id}")
                return session
        except Exception as e:
            logger.error(f"Error creating chat session for user {user.id}: {str(e)}")
            raise
    
    def get_user_sessions(self, user, include_inactive=False):
        """
        Get all chat sessions for a user.
        """
        queryset = ChatSession.objects.filter(user=user)
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        return queryset.order_by('-last_message_at', '-created_at')
    
    def get_session_by_id(self, session_id, user):
        """
        Get a specific chat session by ID, ensuring it belongs to the user.
        """
        try:
            return ChatSession.objects.get(id=session_id, user=user, is_active=True)
        except ObjectDoesNotExist:
            logger.warning(f"Session {session_id} not found for user {user.id}")
            return None
    
    def update_session(self, session, **kwargs):
        """
        Update a chat session.
        """
        try:
            with transaction.atomic():
                for key, value in kwargs.items():
                    setattr(session, key, value)
                session.save()
                logger.info(f"Updated chat session {session.id}")
                return session
        except Exception as e:
            logger.error(f"Error updating chat session {session.id}: {str(e)}")
            raise
    
    def rename_session(self, session, new_title):
        """
        Rename a chat session.
        """
        return self.update_session(session, title=new_title)
    
    def toggle_favorite(self, session):
        """
        Toggle the favorite status of a chat session.
        """
        session.is_favorite = not session.is_favorite
        return self.update_session(session, is_favorite=session.is_favorite)
    
    def delete_session(self, session):
        """
        Soft delete a chat session and all its messages.
        """
        try:
            with transaction.atomic():
                # Soft delete all messages in the session
                session.messages.filter(is_active=True).update(
                    is_active=False,
                    deleted_at=timezone.now()
                )
                
                # Soft delete the session
                session.soft_delete()
                
                logger.info(f"Deleted chat session {session.id} and its messages")
                return True
        except Exception as e:
            logger.error(f"Error deleting chat session {session.id}: {str(e)}")
            raise


class ChatMessageService:
    """
    Service class for chat message operations.
    """
    
    def add_message(self, session, sender, content, context=None, metadata=None):
        """
        Add a new message to a chat session.
        """
        try:
            with transaction.atomic():
                message = ChatMessage.objects.create(
                    session=session,
                    sender=sender,
                    content=content,
                    context=context or {},
                    metadata=metadata or {}
                )
                
                # Update session's last message time
                session.update_last_message_time()
                
                logger.info(f"Added message {message.id} to session {session.id}")
                return message
        except Exception as e:
            logger.error(f"Error adding message to session {session.id}: {str(e)}")
            raise
    
    def get_session_messages(self, session, limit=None):
        """
        Get all messages for a chat session.
        """
        queryset = session.messages.filter(is_active=True).order_by('created_at')
        if limit:
            queryset = queryset[:limit]
        return queryset
    
    def get_message_by_id(self, message_id, session):
        """
        Get a specific message by ID within a session.
        """
        try:
            return ChatMessage.objects.get(id=message_id, session=session, is_active=True)
        except ObjectDoesNotExist:
            logger.warning(f"Message {message_id} not found in session {session.id}")
            return None
    
    def update_message(self, message, **kwargs):
        """
        Update a chat message.
        """
        try:
            with transaction.atomic():
                for key, value in kwargs.items():
                    setattr(message, key, value)
                message.save()
                logger.info(f"Updated message {message.id}")
                return message
        except Exception as e:
            logger.error(f"Error updating message {message.id}: {str(e)}")
            raise
    
    def delete_message(self, message):
        """
        Soft delete a chat message.
        """
        try:
            message.soft_delete()
            logger.info(f"Deleted message {message.id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting message {message.id}: {str(e)}")
            raise
    
    def get_conversation_history(self, session, limit=50):
        """
        Get conversation history for a session with pagination.
        """
        return self.get_session_messages(session, limit=limit)
