# Docker Compose Quick Reference

## Initial Setup

```bash
# 1. Configure environment
cp .env.prod.example .env.prod
cp certbot/cloudflare.ini.example certbot/cloudflare.ini
# Edit both files with your credentials

# 2. Make scripts executable
chmod +x deploy.sh init-letsencrypt.sh

# 3. Deploy
./deploy.sh
```

## Common Commands

### Service Management

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart web

# View service status
docker-compose ps

# View resource usage
docker stats
```

### Logs

```bash
# View all logs
docker-compose logs

# Follow all logs
docker-compose logs -f

# Logs for specific service
docker-compose logs web
docker-compose logs nginx
docker-compose logs celery

# Follow specific service
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail=100
```

### Django Management

```bash
# Django shell
docker-compose exec web python manage.py shell

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run migrations
docker-compose exec web python manage.py migrate

# Create migrations
docker-compose exec web python manage.py makemigrations

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Custom management command
docker-compose exec web python manage.py <command>
```

### Database Operations

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U roommate_user -d roommate

# Backup database
docker-compose exec db pg_dump -U roommate_user roommate > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
docker-compose exec -T db psql -U roommate_user roommate < backup_20260216_120000.sql

# View database size
docker-compose exec db psql -U roommate_user -d roommate -c "SELECT pg_size_pretty(pg_database_size('roommate'));"
```

### Redis Operations

```bash
# Access Redis CLI (replace with your password)
docker-compose exec redis redis-cli -a $REDIS_PASSWORD

# Ping Redis
docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping

# Monitor Redis commands
docker-compose exec redis redis-cli -a $REDIS_PASSWORD monitor

# Clear cache
docker-compose exec redis redis-cli -a $REDIS_PASSWORD FLUSHALL
```

### Celery Operations

```bash
# View Celery workers
docker-compose exec celery celery -A roommate inspect active

# View registered tasks
docker-compose exec celery celery -A roommate inspect registered

# View scheduled tasks
docker-compose exec celery celery -A roommate inspect scheduled

# Restart Celery worker
docker-compose restart celery

# Restart Celery beat
docker-compose restart celery-beat
```

### SSL/Certificates

```bash
# View certificate status
docker-compose exec certbot certbot certificates

# Manually renew certificates
docker-compose exec certbot certbot renew

# Force renewal
docker-compose exec certbot certbot renew --force-renewal

# Reload nginx after certificate renewal
docker-compose restart nginx
```

### Application Updates

```bash
# Update application (full process)
git pull
docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput

# Or use a one-liner
git pull && docker-compose up -d --build && docker-compose exec web python manage.py migrate && docker-compose exec web python manage.py collectstatic --noinput
```

### Troubleshooting

```bash
# Rebuild specific service
docker-compose build web
docker-compose up -d web

# Rebuild all without cache
docker-compose build --no-cache

# Remove all containers and volumes (DESTRUCTIVE!)
docker-compose down -v

# View container details
docker-compose exec web env
docker-compose exec web ps aux

# Check environment variables
docker-compose config

# Execute bash in container
docker-compose exec web bash
docker-compose exec db bash

# View nginx configuration
docker-compose exec nginx cat /etc/nginx/nginx.conf
docker-compose exec nginx nginx -t  # Test configuration
```

### Maintenance

```bash
# Clean up Docker system
docker system prune -a

# Remove unused volumes
docker volume prune

# Remove unused images
docker image prune -a

# View disk usage
docker system df
```

### Backup Everything

```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Backup database
docker-compose exec db pg_dump -U roommate_user roommate > backups/$(date +%Y%m%d)/database.sql

# Backup media files
docker-compose exec web tar -czf - media/ > backups/$(date +%Y%m%d)/media.tar.gz

# Backup environment and configs
cp .env.prod backups/$(date +%Y%m%d)/
cp certbot/cloudflare.ini backups/$(date +%Y%m%d)/
```

### Development

```bash
# Use development settings locally
export DJANGO_ENV=dev
python manage.py runserver

# Use production settings locally (for testing)
export DJANGO_ENV=prod
# Set required environment variables
python manage.py runserver
```

## Service URLs

- **Application**: https://roommate.klauvi.is
- **Admin Panel**: https://roommate.klauvi.is/admin/
- **Static Files**: https://roommate.klauvi.is/static/
- **Media Files**: https://roommate.klauvi.is/media/

## Quick Diagnostics

```bash
# Check if all services are healthy
docker-compose ps

# Check web service health
curl http://localhost:8000/

# Check nginx health
curl http://localhost/health

# View recent errors in web logs
docker-compose logs web | grep ERROR

# Check database connectivity
docker-compose exec web python manage.py dbshell

# Test Redis connection
docker-compose exec web python -c "from django.core.cache import cache; cache.set('test', 'value'); print(cache.get('test'))"
```

## Environment Variables Quick Reference

```bash
# View all environment variables in web container
docker-compose exec web env | grep -E '(DJANGO|POSTGRES|REDIS)'

# Check specific variable
docker-compose exec web printenv SECRET_KEY
```

## Permissions

```bash
# Fix file permissions if needed
sudo chown -R $USER:$USER .
chmod 600 certbot/cloudflare.ini
chmod +x *.sh
```
