# RAG Chat Storage Microservice

A production-ready Django REST Framework microservice for storing and managing RAG (Retrieval-Augmented Generation) based chat conversations. This microservice provides comprehensive chat session management, message storage, and RAG pipeline integration with Nubious API.

## Features

### Core Functionalities
- ✅ **Chat Session Management**: Create, rename, favorite, and delete chat sessions
- ✅ **Message Storage**: Store messages with sender, content, and RAG context
- ✅ **Session Operations**: Rename sessions, mark as favorite, soft delete
- ✅ **Message History**: Retrieve conversation history with pagination
- ✅ **RAG Integration**: Full RAG pipeline with Nubious API integration
- ✅ **Knowledge Base Management**: Create and manage knowledge bases for RAG

### Technical Features
- ✅ **Authentication**: JWT and API key authentication
- ✅ **Rate Limiting**: Configurable rate limiting to prevent abuse
- ✅ **Global Error Handling**: Centralized error handling and logging
- ✅ **API Logging**: Comprehensive logging of all API requests/responses
- ✅ **Soft Delete**: Soft delete functionality for data recovery
- ✅ **Pagination**: Built-in pagination for large datasets
- ✅ **CORS Support**: Configurable CORS for frontend integration
- ✅ **Health Checks**: Health check endpoints for monitoring
- ✅ **Swagger Documentation**: Auto-generated API documentation
- ✅ **Docker Support**: Complete Docker setup with PostgreSQL and Redis
- ✅ **Database Management**: pgAdmin included for database browsing

## Architecture

The project follows a microservice architecture with clear separation of concerns:

### Layer Architecture
- **Views Layer**: Handle HTTP requests/responses (def get, def post methods)
- **Controllers Layer**: Contain business logic and orchestrate operations
- **Services Layer**: Handle database connections and data operations
- **Models Layer**: Define data structures and relationships

### App Structure
```
RAG Chat Microservice
├── Core App (Base classes, utilities, authentication)
├── Chat App (Sessions, messages, conversation management)
├── RAG App (RAG pipeline, knowledge bases, document processing)
├── Logs App (API logging middleware)
└── Django Admin (Complete admin interface)
```

## Technology Stack

- **Backend**: Django 4.2.7 + Django REST Framework 3.14.0
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Authentication**: Django Allauth + JWT + API Keys
- **Documentation**: Swagger/OpenAPI (drf-yasg)
- **Containerization**: Docker + Docker Compose
- **Background Tasks**: Celery + Redis
- **Monitoring**: Health checks + comprehensive logging + New Relic APM

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd RAG-backend
```

### 2. Environment Setup
```bash
# Copy environment file
cp env.example .env

# Edit .env file with your configuration
# Update API keys, database credentials, etc.
# For New Relic APM, add your license key to NEW_RELIC_LICENSE_KEY
```

### 3. Start with Docker
```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser and setup project
docker-compose exec web python manage.py setup_project

# Create static files
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. Access the Services
- **API**: http://localhost:8000/api/v1/
- **Admin**: http://localhost:8000/admin/ (admin/admin123)
- **Swagger**: http://localhost:8000/swagger/
- **Health Check**: http://localhost:8000/api/v1/health/
- **pgAdmin**: http://localhost:5050/ (admin@admin.com/admin)

## API Documentation

### Authentication

The API supports multiple authentication methods:

1. **JWT Authentication** (for web clients)
2. **API Key Authentication** (for external services)
3. **Token Authentication** (for mobile apps)

#### API Key Authentication
```bash
# Add to request headers
X-API-Key: your-api-key-here
# or
Authorization: Bearer your-api-key-here
```

### Standard Response Format

All API responses follow a consistent format:

```json
{
  "data": {...},
  "message": "Success message",
  "status": "success",
  "meta": {
    "pagination": {...},
    "additional_info": "..."
  }
}
```

### Chat Session APIs

#### List/Create Chat Sessions
```http
GET /api/v1/sessions/
POST /api/v1/sessions/
```

**Create Session Request:**
```json
{
  "title": "New Chat Session"
}
```

#### Get/Update/Delete Session
```http
GET /api/v1/sessions/{session_id}/
PUT /api/v1/sessions/{session_id}/
DELETE /api/v1/sessions/{session_id}/
```

#### Rename Session
```http
PATCH /api/v1/sessions/{session_id}/rename/
```
```json
{
  "title": "New Title"
}
```

#### Toggle Favorite
```http
PATCH /api/v1/sessions/{session_id}/toggle-favorite/
```

### Chat Message APIs

#### List/Create Messages
```http
GET /api/v1/sessions/{session_id}/messages/
POST /api/v1/sessions/{session_id}/messages/
```

**Create Message Request:**
```json
{
  "sender": "user",
  "content": "Hello, how are you?",
  "context": {},
  "metadata": {}
}
```

#### Get/Update/Delete Message
```http
GET /api/v1/sessions/{session_id}/messages/{message_id}/
PUT /api/v1/sessions/{session_id}/messages/{message_id}/
DELETE /api/v1/sessions/{session_id}/messages/{message_id}/
```

#### Get Conversation History
```http
GET /api/v1/sessions/{session_id}/history/?limit=50
```

### RAG APIs

#### Process RAG Query
```http
POST /api/v1/rag/query/
```
```json
{
  "query": "What is machine learning?",
  "session_id": "optional-session-id",
  "knowledge_base_id": "optional-knowledge-base-id"
}
```

#### Knowledge Base Management
```http
GET /api/v1/rag/knowledge-bases/
POST /api/v1/rag/knowledge-bases/
GET /api/v1/rag/knowledge-bases/{id}/
PUT /api/v1/rag/knowledge-bases/{id}/
DELETE /api/v1/rag/knowledge-bases/{id}/
```

#### Document Management
```http
GET /api/v1/rag/knowledge-bases/{kb_id}/documents/
POST /api/v1/rag/knowledge-bases/{kb_id}/documents/
GET /api/v1/rag/knowledge-bases/{kb_id}/documents/{doc_id}/
PUT /api/v1/rag/knowledge-bases/{kb_id}/documents/{doc_id}/
DELETE /api/v1/rag/knowledge-bases/{kb_id}/documents/{doc_id}/
```

#### RAG Query History
```http
GET /api/v1/rag/queries/history/?limit=20
```

## Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=rag_chat_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# API Authentication
API_KEY=your-api-key-here
NUBIOUS_API_KEY=your-nubious-api-key-here

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# New Relic Configuration
NEW_RELIC_LICENSE_KEY=your-newrelic-license-key-here
NEW_RELIC_APP_NAME=RAG-Chat-Backend
NEW_RELIC_ENVIRONMENT=development
```

## Development Setup

### Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env file

# Run migrations
python manage.py migrate

# Create superuser
python manage.py setup_project

# Run development server
python manage.py runserver

# Run Celery worker (in another terminal)
celery -A rag_chat worker -l info
```

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test chat
python manage.py test rag
python manage.py test core
```

## Code Architecture

### Controller Pattern Implementation

The project implements a clear separation of concerns using the Controller pattern:

#### Views Layer (`views.py`)
- Handle HTTP requests and responses
- Use `def get()`, `def post()`, `def put()`, `def patch()`, `def delete()` methods
- Minimal logic - only request/response handling
- Example:
```python
class ChatSessionListCreateAPIView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        controller = ChatSessionController()
        result = controller.list_sessions(request.user, request)
        return Response(result['data'], status=result['status'])
```

#### Controllers Layer (`controllers.py`)
- Contain all business logic
- Orchestrate operations between services
- Handle validation, error handling, and response formatting
- Example:
```python
class ChatSessionController:
    def list_sessions(self, user, request):
        try:
            sessions = self.session_service.get_user_sessions(user)
            serializer = ChatSessionListSerializer(sessions, many=True)
            return {
                'data': serializer.data,
                'message': 'Chat sessions retrieved successfully',
                'status': status.HTTP_200_OK
            }
        except Exception as e:
            return {
                'data': None,
                'message': f'Failed to retrieve chat sessions: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
```

#### Services Layer (`services.py`)
- Handle database connections and operations
- Implement data access logic
- Provide reusable business operations
- Example:
```python
class ChatSessionService:
    def get_user_sessions(self, user):
        return ChatSession.objects.filter(
            user=user, 
            is_active=True
        ).order_by('-last_message_at')
```

## Database Schema

### Core Models
- **TimeStampedModel**: Base model with created_at, updated_at
- **SoftDeleteModel**: Base model with soft delete functionality
- **BaseModel**: Combines timestamp and soft delete

### Chat Models
- **ChatSession**: Chat sessions with title, favorite status, last message time
- **ChatMessage**: Individual messages with sender, content, context, metadata

### RAG Models
- **KnowledgeBase**: Knowledge bases for RAG processing
- **Document**: Documents within knowledge bases
- **DocumentChunk**: Document chunks for vector search
- **RAGQuery**: RAG queries and responses

### Logging Models
- **APILog**: Comprehensive API request/response logging

## Monitoring and Logging

### Health Checks
- **Health Check Endpoint**: `/api/v1/health/`
- **Database Connection**: Monitored
- **Cache Connection**: Monitored
- **Response Time**: Tracked

### API Logging
- **Request Logging**: All API requests logged with metadata
- **Response Logging**: Response status, time, and data logged
- **Error Logging**: Comprehensive error tracking
- **Performance Metrics**: Response time tracking

### Log Files
- **Application Logs**: `logs/app.log`
- **Django Logs**: Console and file logging
- **API Logs**: Database-stored API request logs

## Security Features

- **API Key Authentication**: Secure API key validation
- **JWT Authentication**: Token-based authentication
- **CORS Configuration**: Configurable cross-origin requests
- **Rate Limiting**: Request rate limiting
- **Input Validation**: Comprehensive input validation
- **SQL Injection Protection**: Django ORM protection
- **XSS Protection**: Built-in Django security

## Deployment

### Production Deployment
```bash
# Build production image
docker build -t rag-chat:latest .

# Run with production settings
docker run -d \
  -e DEBUG=False \
  -e SECRET_KEY=your-production-secret \
  -e DB_HOST=your-db-host \
  -e REDIS_URL=your-redis-url \
  -p 8000:8000 \
  rag-chat:latest
```

### Environment-Specific Configurations
- **Development**: Debug enabled, local database
- **Staging**: Debug disabled, staging database
- **Production**: Debug disabled, production database, SSL

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation at `/swagger/`

## Changelog

### v1.0.0
- Initial release
- Complete chat session management
- RAG pipeline integration
- Comprehensive API logging
- Docker support
- Swagger documentation
