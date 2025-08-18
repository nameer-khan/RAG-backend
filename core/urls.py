from django.urls import path
from .views import (
    HealthCheckAPIView,
    UserRegistrationAPIView,
    UserProfileAPIView,
    ChangePasswordAPIView,
    health_check
)

urlpatterns = [
    path('', health_check, name='health-check'),
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
]
