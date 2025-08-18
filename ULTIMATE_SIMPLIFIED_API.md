# 🚀 ULTIMATE SIMPLIFIED RAG API

## Overview
**Only 2 Core APIs** - That's it! Super simple and clean:

1. **Authentication API** - JWT-based user management
2. **Chat API** - Handle conversations with **automatic RAG responses**

## Base URL
```
http://localhost:8000/api/v1/
```

## Authentication
All APIs require JWT authentication:
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

### Get User Profile
```http
GET /api/v1/users/profile/
Authorization: Bearer <your_jwt_token>
```

---

## 2. Chat API (with Integrated RAG)

### Create Chat Session
```http
POST /api/v1/sessions/
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "title": "My Chat Session"
}
```

### List Chat Sessions
```http
GET /api/v1/sessions/
Authorization: Bearer <your_jwt_token>
```

### Send Message (Auto-Generates RAG Response!)
```http
POST /api/v1/sessions/{session_id}/messages/
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "content": "What is machine learning?",
  "document_category": "technology"
}
```

**Response includes both your message AND the RAG-generated response:**
```json
{
  "data": {
    "id": "message-uuid",
    "session": "session-uuid", 
    "sender": "assistant",
    "content": "Based on the available information, machine learning is...",
    "document_category": "technology",
    "rag_context": ["context from documents..."],
    "rag_sources": [{"source": "doc1", "score": 0.9}],
    "created_at": "2025-08-19T02:05:00Z"
  },
  "message": "Message sent and response generated successfully",
  "status": 201
}
```

### Get Session Messages
```http
GET /api/v1/sessions/{session_id}/messages/
Authorization: Bearer <your_jwt_token>
```

---

## 3. Documents API (Optional)

### Create Document
```http
POST /api/v1/documents/
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "title": "Machine Learning Basics",
  "content": "Machine learning is a subset of artificial intelligence...",
  "category": "technology"
}
```

### List Documents
```http
GET /api/v1/documents/
Authorization: Bearer <your_jwt_token>
```

---

## 🎯 Key Simplifications

1. **No Separate RAG API** - RAG is built into chat messages
2. **Automatic Response Generation** - Send a message, get RAG response instantly
3. **No Knowledge Base Complexity** - Just document categories
4. **Minimal Endpoints** - Only 8 total endpoints!

## 📊 API Count Comparison

| Feature | Before | After |
|---------|--------|-------|
| **Total Endpoints** | 15+ | **8** |
| **RAG APIs** | 3 separate | **0 (integrated)** |
| **Chat APIs** | 8 separate | **4 (simplified)** |
| **Knowledge Bases** | 6 APIs | **0 (removed)** |

## 🔄 Workflow

1. **Register/Login** → Get JWT token
2. **Create Chat Session** → Start conversation
3. **Send Message** → Automatically get RAG response
4. **Optional: Add Documents** → Improve RAG responses

## 💡 Example Usage

```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass","password_confirm":"pass","email":"user@example.com"}'

# 2. Login
curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'

# 3. Create session
curl -X POST http://localhost:8000/api/v1/sessions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Chat"}'

# 4. Send message (auto-gets RAG response!)
curl -X POST http://localhost:8000/api/v1/sessions/SESSION_ID/messages/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"What is AI?","document_category":"technology"}'
```

## 🎉 Benefits

- **Super Simple** - Only 2 main APIs to understand
- **Automatic RAG** - No separate API calls needed
- **Clean Responses** - Get both message and RAG response in one call
- **Easy Integration** - Perfect for React frontend
- **Minimal Complexity** - Focus on core functionality

This is the **ultimate simplified RAG backend**! 🚀
