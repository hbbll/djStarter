# Django Starter Project

A modern Django REST Framework project with authentication, file upload, and containerized deployment.

## Features

- **Authentication System**: User registration, login, JWT tokens, profile management
- **File Upload/Download**: File storage with user permissions
- **Role-Based Access Control**: Comprehensive permission system
- **Docker Support**: Complete containerized deployment
- **Just Task Runner**: Efficient task management with justfile

## Architecture

This project includes Django applications:
- `account`: Authentication and user management
- `upload`: File upload/download functionality

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
   cd djStarter
   cp .env.example .env
   ```

2. **Configure environment variables:**
   Edit `.env` file with your settings

3. **Build and run:**
   ```bash
   just build
   just up
   ```

4. **Setup database:**
   ```bash
   just migrate
   just su
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
just dev

# Docker commands
just up          # Start all containers
just down        # Stop containers
just shell       # Django shell
just logs        # View logs
just clean       # Clean everything

# Database
just migrate     # Run migrations
just su          # Create superuser
just seed        # Seed database
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | True | Django debug mode |
| `SECRET_KEY` | - | Django secret key |
| `DB_NAME` | djstarter | Database name |
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

- Application logs: `just logs`
- Nginx logs: `./docker/log/`
- Health checks configured for all services

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `just dev`
5. Submit a pull request
