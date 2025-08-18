from rest_framework import serializers
from django.contrib.auth.models import User


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Base serializer that provides common functionality for all model serializers.
    """
    
    def to_representation(self, instance):
        """
        Override to exclude is_active=False objects from responses.
        """
        if hasattr(instance, 'is_active') and not instance.is_active:
            return None
        return super().to_representation(instance)


class UserSerializer(BaseModelSerializer):
    """
    Serializer for User model.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class StandardResponseSerializer(serializers.Serializer):
    """
    Standard response serializer for consistent API responses.
    """
    data = serializers.JSONField(required=False)
    message = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    errors = serializers.JSONField(required=False)
    meta = serializers.JSONField(required=False)
