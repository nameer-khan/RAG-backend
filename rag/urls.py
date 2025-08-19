from django.urls import path
from .views import (
    RAGQueryAPIView,
    RAGQueryHistoryAPIView,
    DocumentListCreateAPIView,
    DocumentDetailAPIView,
    DocumentCategoriesAPIView,
    DocumentSearchAPIView,
)

urlpatterns = [
    # RAG Query Processing
    path('query/', RAGQueryAPIView.as_view(), name='rag-query'),
    path('queries/history/', RAGQueryHistoryAPIView.as_view(), name='rag-query-history'),
    
    # Documents (simplified - no knowledge base required)
    path('documents/', DocumentListCreateAPIView.as_view(), name='document-list-create'),
    path('documents/<uuid:pk>/', DocumentDetailAPIView.as_view(), name='document-detail'),
    path('documents/categories/', DocumentCategoriesAPIView.as_view(), name='document-categories'),
    path('documents/search/', DocumentSearchAPIView.as_view(), name='document-search'),
]
