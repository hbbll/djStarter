# DRF Merged Project

A unified Django REST Framework project that combines authentication, file upload, and API gateway functionality.

## Features

- **Authentication System**: User registration, login, JWT tokens, profile management
- **File Upload/Download**: MinIO-based file storage with user permissions
- **API Gateway**: Nginx reverse proxy with load balancing
- **Role-Based Access Control**: Comprehensive permission system
- **Multi-language Support**: Uzbek, Russian, English
- **Docker Support**: Complete containerized deployment

## Architecture

This project merges three Django applications:
- `drf-auth`: Authentication and user management
- `drf-file`: File upload/download with MinIO
- `drf-gateway`: API gateway and nginx configuration

## Prerequisites

- Docker & Docker Compose
- Python 3.9+ (for local development)
- PostgreSQL (handled by Docker)
- Redis (handled by Docker)
- MinIO (handled by Docker)

## Quick Start

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd merged-project
   cp .env.example .env
   ```

2. **Configure environment variables:**
   Edit `.env` file with your settings

3. **Build and run:**
   ```bash
   make build
   make up
   ```

4. **Setup database:**
   ```bash
   make migrate
   make superuser
   ```

## API Endpoints

### Authentication (`/auth/`)
- `POST /auth/login/` - User login
- `POST /auth/register/` - User registration
- `POST /auth/token/` - Obtain JWT token
- `POST /auth/token/refresh/` - Refresh JWT token
- `POST /auth/logout/` - User logout
- `GET /auth/me/` - Get current user profile
- `PUT /auth/me/update/` - Update user profile

### File Management (`/api/`)
- `POST /api/upload/` - Upload file (requires authentication)
- `GET /api/<path:file_path>/` - Download file

### Admin
- `/admin/` - Django admin interface

## Development Commands

```bash
# Start development server
make dev

# Docker commands
make up          # Start all containers
make down        # Stop containers
make shell       # Django shell
make logs        # View logs
make clean       # Clean everything

# Database
make migrate     # Run migrations
make superuser   # Create superuser
make seed        # Seed database
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | True | Django debug mode |
| `SECRET_KEY` | - | Django secret key |
| `DB_NAME` | drf_merged | Database name |
| `DB_USER` | postgres | Database user |
| `DB_PASSWORD` | root | Database password |
| `REDIS_HOST` | redis | Redis server |
| `MINIO_ENDPOINT` | minio:9000 | MinIO server |

## File Storage

Files are stored using MinIO object storage:
- Each file is tagged with the uploading user's ID
- Files are organized by buckets and paths
- Presigned URLs are generated for secure access

## Authentication

- JWT-based authentication
- Token caching with Redis
- User session management
- Role-based permissions

## Deployment

The project is fully containerized and can be deployed with:

```bash
docker-compose up -d
```

Nginx acts as a reverse proxy, routing requests to the Django application and serving static/media files.

## Monitoring

- Application logs: `make logs`
- Nginx logs: `./docker/log/`
- Health checks configured for all services

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `make dev`
5. Submit a pull request
