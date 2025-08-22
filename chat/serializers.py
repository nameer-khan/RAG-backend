from rest_framework import serializers
from core.serializers import BaseModelSerializer, UserSerializer
from .models import ChatSession, ChatMessage


class ChatSessionSerializer(BaseModelSerializer):
    """
    Serializer for ChatSession model.
    """
    user = UserSerializer(read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'user', 'title', 'is_favorite', 'is_active', 
            'message_count', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'message_count', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        """Get the count of messages in this session."""
        return obj.messages.count()
    
    def create(self, validated_data):
        """Override create to set the user automatically."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class CreateChatSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new chat sessions.
    """
    class Meta:
        model = ChatSession
        fields = ['title', 'metadata']
        extra_kwargs = {
            'title': {'required': False},
            'metadata': {'required': False},
        }


class ChatMessageSerializer(BaseModelSerializer):
    """
    Serializer for ChatMessage model with integrated RAG functionality.
    """
    session = ChatSessionSerializer(read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'session', 'sender', 'content', 'document_category',
            'rag_context', 'rag_sources', 'context', 'metadata', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'session', 'created_at', 'updated_at']


class CreateChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new chat messages with RAG integration.
    """
    class Meta:
        model = ChatMessage
        fields = [
            'sender', 'content', 'document_category', 'context', 'metadata'
        ]
        extra_kwargs = {
            'sender': {'required': False, 'default': 'user'},
            'document_category': {'required': False},
            'context': {'required': False},
            'metadata': {'required': False},
        }
    
    def create(self, validated_data):
        """Override create to set the session automatically and handle RAG responses."""
        request = self.context.get('request')
        session = self.context.get('session')
        
        if not session:
            raise serializers.ValidationError("Session is required")
        
        # Set the session
        validated_data['session'] = session
        
        # If this is a user message, automatically generate assistant response
        if validated_data.get('sender') == 'user':
            # Create the user message first
            user_message = super().create(validated_data)
            
            # Generate RAG response
            from rag.services import RAGPipelineService
            rag_service = RAGPipelineService()
            
            # Get conversation history for context
            conversation_history = []
            previous_messages = session.messages.filter(sender='user').order_by('-created_at')[:5]
            for msg in reversed(previous_messages):
                conversation_history.append({
                    'role': 'user',
                    'content': msg.content
                })
            
            # Process RAG query
            rag_result = rag_service.process_query(
                user=request.user,
                query=validated_data['content'],
                document_category=validated_data.get('document_category'),
                conversation_history=conversation_history
            )
            
            if rag_result:
                # Create assistant response
                assistant_data = {
                    'session': session,
                    'sender': 'assistant',
                    'content': rag_result['response'],
                    'document_category': validated_data.get('document_category', ''),
                    'rag_context': rag_result.get('context', []),
                    'rag_sources': rag_result.get('sources', []),
                    'context': validated_data.get('context', {}),
                    'metadata': {
                        'rag_query_id': rag_result.get('query_id'),
                        'context_count': len(rag_result.get('context', [])),
                        **validated_data.get('metadata', {})
                    }
                }
                
                assistant_message = ChatMessage.objects.create(**assistant_data)
                return assistant_message
            
            return user_message
        
        return super().create(validated_data)


class ChatConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for chat conversation history.
    """
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'sender', 'content', 'document_category',
            'rag_context', 'rag_sources', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
