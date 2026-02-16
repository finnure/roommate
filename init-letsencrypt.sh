#!/bin/bash

# Script to initialize SSL certificates for the first time
# This script should be run once before starting the full docker-compose stack

set -e

DOMAIN="roommate.klauvi.is"
EMAIL="klauvi@gmail.com"

echo "=== Initial SSL Certificate Setup ==="
echo "This script will obtain the first SSL certificate from Let's Encrypt"
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Check if cloudflare.ini exists
if [ ! -f "certbot/cloudflare.ini" ]; then
    echo "ERROR: certbot/cloudflare.ini not found!"
    echo "Please copy certbot/cloudflare.ini.example to certbot/cloudflare.ini"
    echo "and fill in your Cloudflare API credentials."
    exit 1
fi

# Check if .env.prod exists
if [ ! -f ".env.prod" ]; then
    echo "ERROR: .env.prod not found!"
    echo "Please copy .env.prod.example to .env.prod"
    echo "and fill in your production configuration."
    exit 1
fi

# Create necessary directories
mkdir -p certbot/conf certbot/www

# Set proper permissions for cloudflare.ini
chmod 600 certbot/cloudflare.ini

echo "Starting initial certificate request..."
echo ""

# Run certbot in a temporary container to obtain the certificate
docker run --rm \
    -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
    -v "$(pwd)/certbot/www:/var/www/certbot" \
    -v "$(pwd)/certbot/cloudflare.ini:/etc/letsencrypt/cloudflare.ini:ro" \
    certbot/dns-cloudflare:latest \
    certonly \
    --dns-cloudflare \
    --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN"

echo ""
echo "=== Certificate obtained successfully! ==="
echo "You can now start the full application with: docker-compose up -d"
