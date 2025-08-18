from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import ChatSession, ChatMessage
from .services import ChatSessionService, ChatMessageService


class ChatSessionModelTest(TestCase):
    """Test cases for ChatSession model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_chat_session(self):
        """Test creating a chat session."""
        session = ChatSession.objects.create(
            user=self.user,
            title="Test Session"
        )
        self.assertEqual(session.title, "Test Session")
        self.assertEqual(session.user, self.user)
        self.assertFalse(session.is_favorite)
        self.assertTrue(session.is_active)
    
    def test_session_message_count(self):
        """Test message count property."""
        session = ChatSession.objects.create(
            user=self.user,
            title="Test Session"
        )
        
        # Create some messages
        ChatMessage.objects.create(
            session=session,
            sender='user',
            content="Hello"
        )
        ChatMessage.objects.create(
            session=session,
            sender='assistant',
            content="Hi there!"
        )
        
        self.assertEqual(session.message_count, 2)
    
    def test_soft_delete_session(self):
        """Test soft delete functionality."""
        session = ChatSession.objects.create(
            user=self.user,
            title="Test Session"
        )
        
        session.soft_delete()
        session.refresh_from_db()
        
        self.assertFalse(session.is_active)
        self.assertIsNotNone(session.deleted_at)


class ChatMessageModelTest(TestCase):
    """Test cases for ChatMessage model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.session = ChatSession.objects.create(
            user=self.user,
            title="Test Session"
        )
    
    def test_create_chat_message(self):
        """Test creating a chat message."""
        message = ChatMessage.objects.create(
            session=self.session,
            sender='user',
            content="Hello, how are you?",
            context={'source': 'test'},
            metadata={'timestamp': '2023-01-01'}
        )
        
        self.assertEqual(message.sender, 'user')
        self.assertEqual(message.content, "Hello, how are you?")
        self.assertEqual(message.context, {'source': 'test'})
        self.assertEqual(message.metadata, {'timestamp': '2023-01-01'})
    
    def test_message_updates_session_timestamp(self):
        """Test that creating a message updates session timestamp."""
        initial_time = self.session.last_message_at
        
        ChatMessage.objects.create(
            session=self.session,
            sender='user',
            content="Test message"
        )
        
        self.session.refresh_from_db()
        self.assertIsNotNone(self.session.last_message_at)
        if initial_time:
            self.assertGreater(self.session.last_message_at, initial_time)


class ChatSessionServiceTest(TestCase):
    """Test cases for ChatSessionService."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.service = ChatSessionService()
    
    def test_create_session(self):
        """Test creating a session via service."""
        session = self.service.create_session(
            user=self.user,
            title="Service Test Session"
        )
        
        self.assertEqual(session.title, "Service Test Session")
        self.assertEqual(session.user, self.user)
        self.assertTrue(session.is_active)
    
    def test_get_user_sessions(self):
        """Test getting user sessions."""
        # Create multiple sessions
        self.service.create_session(self.user, "Session 1")
        self.service.create_session(self.user, "Session 2")
        
        sessions = self.service.get_user_sessions(self.user)
        self.assertEqual(sessions.count(), 2)
    
    def test_rename_session(self):
        """Test renaming a session."""
        session = self.service.create_session(self.user, "Original Title")
        
        updated_session = self.service.rename_session(session, "New Title")
        self.assertEqual(updated_session.title, "New Title")
    
    def test_toggle_favorite(self):
        """Test toggling favorite status."""
        session = self.service.create_session(self.user, "Test Session")
        
        # Toggle to favorite
        updated_session = self.service.toggle_favorite(session)
        self.assertTrue(updated_session.is_favorite)
        
        # Toggle back to not favorite
        updated_session = self.service.toggle_favorite(updated_session)
        self.assertFalse(updated_session.is_favorite)


class ChatMessageServiceTest(TestCase):
    """Test cases for ChatMessageService."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.session = ChatSession.objects.create(
            user=self.user,
            title="Test Session"
        )
        self.service = ChatMessageService()
    
    def test_add_message(self):
        """Test adding a message via service."""
        message = self.service.add_message(
            session=self.session,
            sender='user',
            content="Test message",
            context={'source': 'test'},
            metadata={'type': 'text'}
        )
        
        self.assertEqual(message.sender, 'user')
        self.assertEqual(message.content, "Test message")
        self.assertEqual(message.context, {'source': 'test'})
        self.assertEqual(message.metadata, {'type': 'text'})
    
    def test_get_session_messages(self):
        """Test getting session messages."""
        # Add multiple messages
        self.service.add_message(self.session, 'user', "Message 1")
        self.service.add_message(self.session, 'assistant', "Message 2")
        
        messages = self.service.get_session_messages(self.session)
        self.assertEqual(messages.count(), 2)
    
    def test_get_conversation_history(self):
        """Test getting conversation history with limit."""
        # Add multiple messages
        for i in range(10):
            self.service.add_message(
                self.session,
                'user' if i % 2 == 0 else 'assistant',
                f"Message {i}"
            )
        
        history = self.service.get_conversation_history(self.session, limit=5)
        self.assertEqual(len(history), 5)


class ChatAPITest(APITestCase):
    """Test cases for Chat API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_chat_session(self):
        """Test creating a chat session via API."""
        url = reverse('chat-session-list-create')
        data = {'title': 'API Test Session'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['title'], 'API Test Session')
        self.assertEqual(response.data['status'], 'success')
    
    def test_list_chat_sessions(self):
        """Test listing chat sessions via API."""
        # Create a session first
        ChatSession.objects.create(
            user=self.user,
            title="Test Session"
        )
        
        url = reverse('chat-session-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['status'], 'success')
    
    def test_rename_session(self):
        """Test renaming a session via API."""
        session = ChatSession.objects.create(
            user=self.user,
            title="Original Title"
        )
        
        url = reverse('chat-session-rename', kwargs={'session_id': session.id})
        data = {'title': 'New Title'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['title'], 'New Title')
        self.assertEqual(response.data['message'], 'Session renamed successfully')
    
    def test_toggle_favorite(self):
        """Test toggling favorite status via API."""
        session = ChatSession.objects.create(
            user=self.user,
            title="Test Session"
        )
        
        url = reverse('chat-session-toggle-favorite', kwargs={'session_id': session.id})
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['data']['is_favorite'])
        self.assertIn('favorited', response.data['message'])
