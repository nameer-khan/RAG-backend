from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
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


class HealthCheckAPIView(BaseAPIView):
    """
    Health check endpoint for monitoring the application status.
    """
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, *args, **kwargs):
        """
        Return health status of the application.
        """
        from django.db import connection
        from django.core.cache import cache
        
        health_status = {
            'status': 'healthy',
            'database': 'connected',
            'cache': 'connected',
            'timestamp': timezone.now().isoformat()
        }
        
        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status['database'] = 'connected'
        except Exception as e:
            health_status['database'] = 'disconnected'
            health_status['status'] = 'unhealthy'
            logger.error(f"Database health check failed: {str(e)}")
        
        # Check cache connection
        try:
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                health_status['cache'] = 'connected'
            else:
                health_status['cache'] = 'disconnected'
                health_status['status'] = 'unhealthy'
        except Exception as e:
            health_status['cache'] = 'disconnected'
            health_status['status'] = 'unhealthy'
            logger.error(f"Cache health check failed: {str(e)}")
        
        status_code = status.HTTP_200_OK if health_status['status'] == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return self.success_response(
            data=health_status,
            message="Health check completed",
            status_code=status_code
        )
