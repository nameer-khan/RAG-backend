from rest_framework import serializers
from core.serializers import BaseModelSerializer, UserSerializer
from .models import ChatSession, ChatMessage


class ChatMessageSerializer(BaseModelSerializer):
    """
    Serializer for ChatMessage model.
    """
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'session', 'sender', 'content', 'context', 
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_session(self, value):
        """Validate that the session belongs to the current user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if value.user != request.user:
                raise serializers.ValidationError("You can only add messages to your own sessions.")
        return value


class ChatSessionSerializer(BaseModelSerializer):
    """
    Serializer for ChatSession model.
    """
    user = UserSerializer(read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.ReadOnlyField()
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'user', 'title', 'is_favorite', 'last_message_at',
            'message_count', 'messages', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'last_message_at', 'message_count', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Override create to set the user automatically."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class ChatSessionListSerializer(BaseModelSerializer):
    """
    Simplified serializer for listing chat sessions.
    """
    user = UserSerializer(read_only=True)
    message_count = serializers.ReadOnlyField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'user', 'title', 'is_favorite', 'last_message_at',
            'message_count', 'last_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'last_message_at', 'message_count', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        """Get the last message in the session."""
        last_message = obj.messages.filter(is_active=True).order_by('-created_at').first()
        if last_message:
            return {
                'id': str(last_message.id),
                'sender': last_message.sender,
                'content': last_message.content[:100] + '...' if len(last_message.content) > 100 else last_message.content,
                'created_at': last_message.created_at
            }
        return None


class CreateChatSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new chat sessions.
    """
    class Meta:
        model = ChatSession
        fields = ['title']
    
    def create(self, validated_data):
        """Override create to set the user automatically."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class UpdateChatSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for updating chat sessions.
    """
    class Meta:
        model = ChatSession
        fields = ['title', 'is_favorite']


class CreateChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new chat messages.
    """
    class Meta:
        model = ChatMessage
        fields = ['session', 'sender', 'content', 'context', 'metadata']
    
    def validate_session(self, value):
        """Validate that the session belongs to the current user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if value.user != request.user:
                raise serializers.ValidationError("You can only add messages to your own sessions.")
        return value


class ChatMessageListSerializer(BaseModelSerializer):
    """
    Serializer for listing chat messages with pagination.
    """
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'sender', 'content', 'context', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
