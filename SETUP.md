# RAG Backend Setup Guide

## Environment Configuration

### 1. Copy Environment File
```bash
cp env.working .env
```

### 2. Environment Variables Explained

#### Authentication
- **JWT Authentication**: The project uses JWT (JSON Web Tokens) for authentication
  - Access tokens expire after 1 hour
  - Refresh tokens expire after 7 days
  - Tokens are automatically rotated for security

- **NUBIOUS_API_KEY**: Used for external RAG service integration
  - This is for the Nubious API service used in `rag/services.py`
  - Replace with your actual Nubious API key

#### New Relic Configuration
- **NEW_RELIC_LICENSE_KEY**: `d98a0483339e24d42e6e225903b1c768FFFFNRAL`
  - This is your New Relic license key for APM monitoring
  - Already configured in `newrelic.ini`

- **NEW_RELIC_API_KEY**: `NRAK-5PI0H3A6QGA8HEFZYBWUYSNSNHQ`
  - This is your New Relic user key for deployments and API access
  - Already configured in `newrelic.ini`

#### Database Configuration
- **No pgvector extension required**: This project uses standard PostgreSQL
- Standard PostgreSQL configuration with psycopg2-binary

### 3. Required Services

#### PostgreSQL
```bash
# Install PostgreSQL and create database
createdb rag_chat_db
```

#### Redis
```bash
# Install Redis for Celery and caching
redis-server
```

### 4. Installation Steps

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

4. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

### 5. JWT Authentication Usage

#### Getting JWT Tokens
```bash
# Login to get access and refresh tokens
curl -X POST http://localhost:8000/api/v1/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "your_username", "password": "your_password"}'
```

#### Using JWT Tokens
```bash
# Use the access token in Authorization header
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://localhost:8000/api/v1/endpoint/

# Refresh token when access token expires
curl -X POST http://localhost:8000/api/v1/token/refresh/ \
     -H "Content-Type: application/json" \
     -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

#### JWT Endpoints
- `POST /api/v1/token/` - Get access and refresh tokens
- `POST /api/v1/token/refresh/` - Refresh access token
- `POST /api/v1/token/verify/` - Verify token validity

### 6. New Relic Monitoring

New Relic is automatically initialized when the license key is provided. The agent will:
- Monitor application performance
- Collect error data
- Provide distributed tracing
- Enable browser monitoring

### 7. Production Considerations

1. **Change SECRET_KEY**: Generate a secure random key
2. **Set DEBUG=False**: In production environment
3. **Configure proper email settings**: For user registration
4. **Set up proper database credentials**: For production database
5. **Configure Redis**: For production Redis instance
6. **JWT Security**: Consider using asymmetric keys for JWT signing in production

### 8. Security Notes

- Never commit `.env` files to version control
- Use strong, unique keys for SECRET_KEY
- Keep New Relic keys secure
- Use environment-specific configurations
- JWT tokens are automatically rotated for security
- Access tokens expire after 1 hour for security
