from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.http import Http404
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the error response format
        response.data = {
            'message': 'An error occurred',
            'status': 'error',
            'errors': response.data
        }
        return response
    
    # Handle Django-specific exceptions
    if isinstance(exc, ValidationError):
        return Response({
            'message': 'Validation error',
            'status': 'error',
            'errors': exc.message_dict if hasattr(exc, 'message_dict') else str(exc)
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if isinstance(exc, Http404):
        return Response({
            'message': 'Not found',
            'status': 'error',
            'errors': {'detail': 'The requested resource was not found.'}
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Log unexpected exceptions
    logger.error(f"Unexpected exception in {context['view'].__class__.__name__}: {str(exc)}")
    
    # Return generic error response for unexpected exceptions
    return Response({
        'message': 'An unexpected error occurred',
        'status': 'error',
        'errors': {'detail': 'Internal server error.'}
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
