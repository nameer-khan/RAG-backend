from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .serializers import StandardResponseSerializer, UserRegistrationSerializer, UserProfileSerializer
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class BaseAPIView(APIView):
    """
    Base API view that provides common functionality for all API views.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def success_response(self, data=None, message="Success", status_code=status.HTTP_200_OK, meta=None):
        """
        Return a standardized success response.
        """
        response_data = {
            "data": data,
            "message": message,
            "status": "success"
        }
        if meta:
            response_data["meta"] = meta
        return Response(response_data, status=status_code)

    def error_response(self, message="Error", errors=None, status_code=status.HTTP_400_BAD_REQUEST, meta=None):
        """
        Return a standardized error response.
        """
        response_data = {
            "message": message,
            "status": "error"
        }
        if errors:
            response_data["errors"] = errors
        if meta:
            response_data["meta"] = meta
        return Response(response_data, status=status_code)

    def handle_exception(self, exc):
        """
        Handle exceptions and return standardized error responses.
        """
        if isinstance(exc, ValidationError):
            return self.error_response(
                message="Validation error",
                errors=exc.message_dict if hasattr(exc, 'message_dict') else str(exc),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        logger.error(f"Exception in {self.__class__.__name__}: {str(exc)}")
        return self.error_response(
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to add transaction management and logging.
        """
        try:
            with transaction.atomic():
                response = super().dispatch(request, *args, **kwargs)
                return response
        except Exception as exc:
            return self.handle_exception(exc)


class ListCreateAPIView(BaseAPIView):
    """
    Base view for list and create operations.
    """
    def get(self, request, *args, **kwargs):
        """
        Handle GET request for listing objects.
        """
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return self.success_response(data=serializer.data)
        except Exception as exc:
            return self.handle_exception(exc)

    def post(self, request, *args, **kwargs):
        """
        Handle POST request for creating objects.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return self.success_response(
                    data=serializer.data,
                    message="Created successfully",
                    status_code=status.HTTP_201_CREATED
                )
            return self.error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as exc:
            return self.handle_exception(exc)

    def get_queryset(self):
        """
        Get the queryset for the view. Override in subclasses.
        """
        raise NotImplementedError

    def get_serializer(self, *args, **kwargs):
        """
        Get the serializer for the view. Override in subclasses.
        """
        raise NotImplementedError


class RetrieveUpdateDestroyAPIView(BaseAPIView):
    """
    Base view for retrieve, update, and destroy operations.
    """
    def get(self, request, pk, *args, **kwargs):
        """
        Handle GET request for retrieving a single object.
        """
        try:
            instance = self.get_object(pk)
            serializer = self.get_serializer(instance)
            return self.success_response(data=serializer.data)
        except Exception as exc:
            return self.handle_exception(exc)

    def put(self, request, pk, *args, **kwargs):
        """
        Handle PUT request for updating an object.
        """
        try:
            instance = self.get_object(pk)
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return self.success_response(
                    data=serializer.data,
                    message="Updated successfully"
                )
            return self.error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as exc:
            return self.handle_exception(exc)

    def patch(self, request, pk, *args, **kwargs):
        """
        Handle PATCH request for partial updates.
        """
        try:
            instance = self.get_object(pk)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return self.success_response(
                    data=serializer.data,
                    message="Updated successfully"
                )
            return self.error_response(
                message="Validation error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as exc:
            return self.handle_exception(exc)

    def delete(self, request, pk, *args, **kwargs):
        """
        Handle DELETE request for soft deleting an object.
        """
        try:
            instance = self.get_object(pk)
            instance.soft_delete()
            return self.success_response(
                message="Deleted successfully",
                status_code=status.HTTP_204_NO_CONTENT
            )
        except Exception as exc:
            return self.handle_exception(exc)

    def get_object(self, pk):
        """
        Get a single object by primary key. Override in subclasses.
        """
        raise NotImplementedError

    def get_serializer(self, *args, **kwargs):
        """
        Get the serializer for the view. Override in subclasses.
        """
        raise NotImplementedError


class HealthCheckAPIView(APIView):
    """
    Health check endpoint to verify API is running.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'message': 'RAG Backend API is running',
            'version': '1.0.0'
        })


class UserRegistrationAPIView(APIView):
    """
    User registration endpoint.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Register a new user.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"New user registered: {user.username}")
            return Response({
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
    """
    User profile management endpoint.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get current user's profile.
        """
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """
        Update current user's profile.
        """
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User profile updated: {request.user.username}")
            return Response({
                'message': 'Profile updated successfully',
                'user': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIView(APIView):
    """
    Change password endpoint.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Change user's password.
        """
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')
        
        if not old_password or not new_password or not new_password_confirm:
            return Response({
                'error': 'All password fields are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != new_password_confirm:
            return Response({
                'error': 'New passwords do not match'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not request.user.check_password(old_password):
            return Response({
                'error': 'Current password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.set_password(new_password)
        request.user.save()
        
        logger.info(f"Password changed for user: {request.user.username}")
        return Response({
            'message': 'Password changed successfully'
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint.
    """
    return Response({
        'status': 'healthy',
        'message': 'RAG Backend API is running',
        'version': '1.0.0'
    })
