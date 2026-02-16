#!/bin/bash

# Deployment script for roommate application
# This script handles the full deployment process

set -e

echo "=== Roommate Application Deployment ==="
echo ""

# Check if .env.prod exists
if [ ! -f ".env.prod" ]; then
    echo "ERROR: .env.prod not found!"
    echo "Please copy .env.prod.example to .env.prod and configure it."
    exit 1
fi

# Source environment variables
set -a
source .env.prod
set +a

# Check if SSL certificates exist
if [ ! -d "certbot/conf/live/$CERTBOT_DOMAIN" ]; then
    echo "SSL certificates not found. Running initial setup..."
    ./init-letsencrypt.sh
fi

echo "Building Docker images..."
docker-compose build

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for database to be ready..."
sleep 10

echo ""
echo "Running database migrations..."
docker-compose exec -T web python manage.py migrate --noinput

echo ""
echo "Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

echo ""
echo "Creating superuser (if not exists)..."
docker-compose exec -T web python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'changeme123')
    print('Superuser created: admin / changeme123')
    print('IMPORTANT: Change this password immediately!')
else:
    print('Superuser already exists')
EOF

echo ""
echo "=== Deployment Complete! ==="
echo ""
echo "Application is running at: https://$CERTBOT_DOMAIN"
echo "Admin panel: https://$CERTBOT_DOMAIN/admin/"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo ""
