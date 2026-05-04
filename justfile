# Default target - show available commands
default:
    @echo "Available commands:"
    @echo "  build          - Build Docker images"
    @echo "  up             - Start all containers"
    @echo "  ps             - Show container status"
    @echo "  down           - Stop and remove all containers"
    @echo "  stop           - Stop containers"
    @echo "  shell          - Open Django shell in container"
    @echo "  logs           - Show container logs"
    @echo "  clean          - Remove all containers, images, and volumes"
    @echo "  seed           - Run database seeding"
    @echo "  migrate        - Run database migrations"
    @echo "  su             - Create Django superuser"
    @echo "  collectstatic  - Collect static files"
    @echo "  dev            - Development server (run Django directly without Docker)"
    @echo "  install        - Install dependencies"
    @echo "  freeze         - Create requirements.txt"

# Build Docker images
build:
    docker compose build

# Start all containers
up:
    docker compose up -d

# Show container status
ps:
    docker compose ps

# Stop and remove containers
down:
    docker compose down

# Stop containers
stop:
    docker compose stop

# Open Django shell
shell:
    docker compose exec django python manage.py shell

# Show logs
logs:
    docker compose logs -f

# Clean everything
clean:
    docker compose down -v --rmi all --remove-orphans

# Run database migrations
migrate:
    docker compose exec django python manage.py migrate

# Create superuser
su:
    docker compose exec django python manage.py createsuperuser

# Seed database
seed: migrate su
    docker compose exec django python manage.py loaddata fixtures/initial_data.json || echo "No fixtures found"

# Collect static files
collectstatic:
    docker compose exec django python manage.py collectstatic --noinput

# Development server (run Django directly without Docker)
dev:
    python manage.py runserver

# Install dependencies
install:
    pip install -r requirements.txt

# Create requirements.txt
freeze:
    pip freeze > requirements.txt
