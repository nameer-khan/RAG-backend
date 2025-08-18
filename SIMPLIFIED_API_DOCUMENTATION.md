# Simplified RAG Backend API Documentation

## Overview
This is a simplified RAG (Retrieval-Augmented Generation) backend with just **3 core APIs**:

1. **Authentication API** - JWT-based user management
2. **Chat API** - Handle conversations and RAG queries  
3. **Documents API** - Manage documents for RAG processing

## Base URL
```
http://localhost:8000/api/v1/
```

## Authentication
All APIs require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 1. Authentication API

### Register User
```http
POST /api/v1/users/register/
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "first_name": "Test",
  "last_name": "User"
}
```

### Login (Get JWT Token)
```http
POST /api/v1/token/
Content-Type: application/json

{
  "username": "testuser",
  "password": "securepassword123"
}
```

### Refresh Token
```http
POST /api/v1/token/refresh/
Content-Type: application/json

{
  "refresh": "<your_refresh_token>"
}
```

### Get User Profile
```http
GET /api/v1/users/profile/
Authorization: Bearer <your_jwt_token>
```

---

## 2. Chat API

### Create Chat Session
```http
POST /api/v1/sessions/
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "title": "My Chat Session",
  "metadata": {}
}
```

### List Chat Sessions
```http
GET /api/v1/sessions/
Authorization: Bearer <your_jwt_token>
```

### Send Message
```http
POST /api/v1/sessions/{session_id}/messages/
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "sender": "user",
  "content": "Hello, how are you?",
  "context": {},
  "metadata": {}
}
```

### Get Session Messages
```http
GET /api/v1/sessions/{session_id}/messages/
Authorization: Bearer <your_jwt_token>
```

---

## 3. Documents API

### Create Document
```http
POST /api/v1/documents/
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "title": "Machine Learning Basics",
  "content": "Machine learning is a subset of artificial intelligence...",
  "category": "technology",
  "source_url": "https://example.com/article",
  "metadata": {
    "author": "John Doe",
    "tags": ["AI", "ML"]
  }
}
```

### List Documents
```http
GET /api/v1/documents/
Authorization: Bearer <your_jwt_token>

# Optional query parameters:
# ?category=technology
# ?page=1&page_size=20
```

### Get Document
```http
GET /api/v1/documents/{document_id}/
Authorization: Bearer <your_jwt_token>
```

### Update Document
```http
PUT /api/v1/documents/{document_id}/
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "Updated content...",
  "category": "updated_category"
}
```

### Delete Document
```http
DELETE /api/v1/documents/{document_id}/
Authorization: Bearer <your_jwt_token>
```

---

## 4. RAG Query API

### Process RAG Query
```http
POST /api/v1/rag/query/
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "query": "What is machine learning?",
  "document_category": "technology",
  "conversation_history": [
    {
      "role": "user",
      "content": "Tell me about AI"
    },
    {
      "role": "assistant", 
      "content": "AI is..."
    }
  ]
}
```

### Get RAG History
```http
GET /api/v1/rag/queries/history/
Authorization: Bearer <your_jwt_token>

# Optional query parameters:
# ?document_category=technology
# ?page=1&page_size=20
```

---

## Response Format

All APIs return responses in this format:
```json
{
  "data": {...},
  "message": "Success message",
  "status": 200
}
```

For paginated responses:
```json
{
  "data": [...],
  "message": "Success message", 
  "status": 200,
  "meta": {
    "pagination": {
      "current_page": 1,
      "page_size": 20,
      "total_count": 100,
      "total_pages": 5,
      "has_next": true,
      "has_previous": false
    }
  }
}
```

---

## Key Simplifications

1. **No Knowledge Bases**: Documents are organized by categories instead of separate knowledge bases
2. **Simplified Document Management**: Direct document CRUD operations without knowledge base hierarchy
3. **Streamlined RAG**: Query by document category instead of knowledge base ID
4. **Reduced API Complexity**: From 15+ endpoints down to 12 core endpoints

## Error Responses

```json
{
  "data": null,
  "message": "Error description",
  "status": 400,
  "errors": {
    "field_name": ["Error details"]
  }
}
```

Common HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error
