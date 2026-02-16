# Production Deployment Guide

## Overview

This guide covers deploying the Roommate application to production using Docker Compose with:
- **Nginx** as reverse proxy
- **Let's Encrypt** SSL certificates via Certbot
- **Cloudflare DNS** authentication
- **PostgreSQL** database
- **Redis** for caching and Celery broker
- **Celery** for background tasks

## Prerequisites

1. **Server Requirements:**
   - Linux server (Ubuntu 20.04+ recommended)
   - Docker and Docker Compose installed
   - Domain name pointing to your server IP
   - Ports 80 and 443 open in firewall

2. **Cloudflare Setup:**
   - Domain managed by Cloudflare DNS
   - API token with `Zone:DNS:Edit` permissions
   - DNS A record for `roommate.klauvi.is` pointing to server IP

3. **Get Cloudflare API Token:**
   - Go to https://dash.cloudflare.com/profile/api-tokens
   - Click "Create Token"
   - Use "Edit zone DNS" template
   - Select your domain under "Zone Resources"
   - Create and copy the token

## Initial Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd roommate
```

### 2. Configure Environment Variables

Copy the example environment file and edit it:

```bash
cp .env.prod.example .env.prod
nano .env.prod
```

**Important variables to change:**

```bash
# Generate a secure secret key (Django)
SECRET_KEY=your-random-secret-key-here

# Database credentials
POSTGRES_PASSWORD=strong-database-password

# Redis password
REDIS_PASSWORD=strong-redis-password

# Email configuration (if using email features)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Cloudflare API token
CLOUDFLARE_API_TOKEN=your-cloudflare-token
```

**Generate a Django SECRET_KEY:**

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 3. Configure Cloudflare Credentials

Copy the example Cloudflare credentials file:

```bash
cp certbot/cloudflare.ini.example certbot/cloudflare.ini
nano certbot/cloudflare.ini
```

Edit and add your Cloudflare API token:

```ini
dns_cloudflare_api_token = YOUR_CLOUDFLARE_API_TOKEN_HERE
```

Set proper permissions:

```bash
chmod 600 certbot/cloudflare.ini
```

### 4. Obtain SSL Certificates

Run the initialization script to obtain your first SSL certificate:

```bash
chmod +x init-letsencrypt.sh
./init-letsencrypt.sh
```

This will:
- Create necessary directories
- Request SSL certificate from Let's Encrypt using Cloudflare DNS validation
- Store certificates in `certbot/conf/`

## Deployment

### Option 1: Automated Deployment

Use the deployment script:

```bash
chmod +x deploy.sh
./deploy.sh
```

This script will:
1. Check for required configuration files
2. Obtain SSL certificates (if needed)
3. Build Docker images
4. Start all services
5. Run database migrations
6. Collect static files
7. Create a superuser account

### Option 2: Manual Deployment

If you prefer manual steps:

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Wait for database
sleep 10

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## Post-Deployment

### 1. Access Your Application

- **Application:** https://roommate.klauvi.is
- **Admin Panel:** https://roommate.klauvi.is/admin/

### 2. Change Default Admin Password

If you used the automated deployment, change the default admin password:

1. Login to admin panel: https://roommate.klauvi.is/admin/
2. Username: `admin`
3. Default password: `changeme123`
4. **Change this immediately!**

### 3. Verify Services

Check that all services are running:

```bash
docker-compose ps
```

You should see:
- `roommate_web` (Django application)
- `roommate_db` (PostgreSQL)
- `roommate_redis` (Redis)
- `roommate_celery` (Celery worker)
- `roommate_celery_beat` (Celery beat scheduler)
- `roommate_nginx` (Nginx reverse proxy)
- `roommate_certbot` (Certificate renewal)

## Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f celery
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart web
```

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Database Backup

```bash
# Backup
docker-compose exec db pg_dump -U roommate_user roommate > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
docker-compose exec -T db psql -U roommate_user roommate < backup_20260216_120000.sql
```

### SSL Certificate Renewal

Certificates auto-renew via the certbot container. To manually renew:

```bash
docker-compose exec certbot certbot renew
docker-compose restart nginx
```

### Django Management Commands

```bash
# Access Django shell
docker-compose exec web python manage.py shell

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run custom management command
docker-compose exec web python manage.py <command>
```

## Monitoring

### Health Checks

All services have health checks configured. Check status:

```bash
docker-compose ps
```

Healthy services show `healthy` in the status column.

### Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

## Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose logs

# Check environment variables
docker-compose config
```

### Database connection errors

```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection
docker-compose exec db psql -U roommate_user -d roommate -c "SELECT 1;"
```

### SSL certificate issues

```bash
# Check certificate status
docker-compose exec certbot certbot certificates

# Renew manually
docker-compose exec certbot certbot renew --force-renewal

# Check Cloudflare API token
docker-compose logs certbot
```

### Static files not loading

```bash
# Recollect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check nginx logs
docker-compose logs nginx
```

### Celery not processing tasks

```bash
# Check Celery worker logs
docker-compose logs celery

# Check Redis connection
docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping
```

## Security Considerations

1. **Keep secrets secure:**
   - Never commit `.env.prod` or `certbot/cloudflare.ini` to git
   - Use strong, unique passwords
   - Rotate credentials regularly

2. **Firewall:**
   - Only expose ports 80 and 443
   - Consider using UFW or iptables

3. **Updates:**
   - Keep Docker images updated
   - Regularly update Python dependencies
   - Monitor security advisories

4. **Backups:**
   - Set up automated database backups
   - Store backups off-site
   - Test restore procedures

## Architecture

```
┌─────────────────────────────────────────────┐
│              Internet (HTTPS)                │
└─────────────────┬───────────────────────────┘
                  │
         ┌────────▼────────┐
         │  Nginx (Proxy)  │
         │  + SSL (443)    │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  Django App     │
         │  (Gunicorn)     │
         └────┬────┬───────┘
              │    │
    ┌─────────┘    └──────────┐
    │                          │
┌───▼────┐              ┌──────▼──────┐
│ PostgreSQL             │   Redis      │
│ (Database) │          │  (Cache)    │
└────────────┘          └──────┬──────┘
                               │
                        ┌──────▼──────┐
                        │   Celery    │
                        │  (Workers)  │
                        └─────────────┘
```

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `DJANGO_ENV` | Environment (prod/dev) | Yes |
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode (False for prod) | Yes |
| `ALLOWED_HOSTS` | Comma-separated hosts | Yes |
| `POSTGRES_DB` | Database name | Yes |
| `POSTGRES_USER` | Database user | Yes |
| `POSTGRES_PASSWORD` | Database password | Yes |
| `REDIS_PASSWORD` | Redis password | Yes |
| `CLOUDFLARE_API_TOKEN` | Cloudflare API token | Yes |
| `CERTBOT_EMAIL` | Let's Encrypt email | Yes |
| `CERTBOT_DOMAIN` | Your domain name | Yes |
| `EMAIL_HOST` | SMTP host | Optional |
| `EMAIL_HOST_USER` | SMTP username | Optional |
| `EMAIL_HOST_PASSWORD` | SMTP password | Optional |

## Support

For issues or questions:
1. Check the logs: `docker-compose logs`
2. Review this documentation
3. Check Django/Docker documentation
4. Contact the development team
