from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)


class APIKeyAuthentication(BaseAuthentication):
    """
    Custom authentication class for API key authentication.
    """
    
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY') or request.META.get('HTTP_AUTHORIZATION')
        
        if not api_key:
            return None
        
        # Remove 'Bearer ' prefix if present
        if api_key.startswith('Bearer '):
            api_key = api_key[7:]
        
        # Check if API key matches the configured key
        if api_key != settings.API_KEY:
            logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
            raise AuthenticationFailed('Invalid API key')
        
        # For API key authentication, we can use a system user or return None
        # In this case, we'll create a system user for API key requests
        User = get_user_model()
        system_user, created = User.objects.get_or_create(
            username='system_api_user',
            defaults={
                'email': 'system@api.com',
                'is_staff': False,
                'is_superuser': False
            }
        )
        
        return (system_user, None)


class JWTAuthentication(BaseAuthentication):
    """
    JWT authentication class (placeholder for future implementation).
    """
    
    def authenticate(self, request):
        # This is a placeholder for JWT authentication
        # In a real implementation, you would validate JWT tokens here
        return None
