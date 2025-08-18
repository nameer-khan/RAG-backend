from rest_framework_simplejwt.authentication import JWTAuthentication as SimpleJWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class JWTAuthentication(SimpleJWTAuthentication):
    """
    JWT authentication class using djangorestframework-simplejwt.
    """
    
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except (InvalidToken, TokenError) as e:
            logger.warning(f"JWT authentication failed: {str(e)}")
            raise AuthenticationFailed('Invalid or expired token')
        except Exception as e:
            logger.error(f"JWT authentication error: {str(e)}")
            raise AuthenticationFailed('Authentication failed')
