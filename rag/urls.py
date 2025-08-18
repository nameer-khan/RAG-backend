from django.urls import path
from .views import (
    RAGQueryAPIView,
    KnowledgeBaseListCreateAPIView,
    KnowledgeBaseDetailAPIView,
    DocumentListCreateAPIView,
    DocumentDetailAPIView,
    RAGQueryHistoryAPIView,
)

urlpatterns = [
    # RAG Query Processing
    path('query/', RAGQueryAPIView.as_view(), name='rag-query'),
    path('queries/history/', RAGQueryHistoryAPIView.as_view(), name='rag-query-history'),
    
    # Knowledge Bases
    path('knowledge-bases/', KnowledgeBaseListCreateAPIView.as_view(), name='knowledge-base-list-create'),
    path('knowledge-bases/<uuid:pk>/', KnowledgeBaseDetailAPIView.as_view(), name='knowledge-base-detail'),
    
    # Documents
    path('knowledge-bases/<uuid:knowledge_base_id>/documents/', DocumentListCreateAPIView.as_view(), name='document-list-create'),
    path('knowledge-bases/<uuid:knowledge_base_id>/documents/<uuid:pk>/', DocumentDetailAPIView.as_view(), name='document-detail'),
]
