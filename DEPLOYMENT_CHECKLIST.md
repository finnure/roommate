# Production Deployment Checklist

## Pre-Deployment

### Server Setup
- [ ] Linux server provisioned (Ubuntu 20.04+ recommended)
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] Firewall configured (ports 80, 443 open)
- [ ] Server has sufficient resources (2GB+ RAM recommended)

### DNS & Domain
- [ ] Domain registered (roommate.klauvi.is)
- [ ] Domain added to Cloudflare
- [ ] DNS A record pointing to server IP
- [ ] DNS propagation verified (`dig roommate.klauvi.is`)

### Cloudflare API
- [ ] Cloudflare account created
- [ ] API token created with Zone:DNS:Edit permissions
- [ ] Token tested and working

### Email (Optional)
- [ ] SMTP credentials obtained (if using email features)
- [ ] Test email sent to verify SMTP works

## Configuration Files

### Environment Variables
- [ ] Copied `.env.prod.example` to `.env.prod`
- [ ] Generated strong SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Set ALLOWED_HOSTS=roommate.klauvi.is
- [ ] Set strong POSTGRES_PASSWORD
- [ ] Set strong REDIS_PASSWORD
- [ ] Set CLOUDFLARE_API_TOKEN
- [ ] Set CERTBOT_EMAIL
- [ ] Configured email settings (if needed)

### Cloudflare Credentials
- [ ] Copied `certbot/cloudflare.ini.example` to `certbot/cloudflare.ini`
- [ ] Added Cloudflare API token
- [ ] Set file permissions: `chmod 600 certbot/cloudflare.ini`

### Scripts
- [ ] Made scripts executable: `chmod +x *.sh`

## Deployment

### Initial Certificate Setup
- [ ] Run `./init-letsencrypt.sh`
- [ ] Verify certificate obtained successfully
- [ ] Check certificate files in `certbot/conf/live/`

### Application Deployment
- [ ] Run `./deploy.sh`
- [ ] All Docker images built successfully
- [ ] All containers started
- [ ] Database migrations completed
- [ ] Static files collected
- [ ] Superuser created

### Verification
- [ ] All services healthy: `docker-compose ps`
- [ ] Web app accessible: `https://roommate.klauvi.is`
- [ ] Admin panel accessible: `https://roommate.klauvi.is/admin/`
- [ ] SSL certificate valid (green padlock in browser)
- [ ] Static files loading correctly
- [ ] Can login to admin panel
- [ ] Changed default admin password

### Service Health Checks
- [ ] Web service: `docker-compose logs web | tail -20`
- [ ] Database: `docker-compose exec db psql -U roommate_user -d roommate -c "SELECT 1;"`
- [ ] Redis: `docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping`
- [ ] Celery: `docker-compose logs celery | tail -20`
- [ ] Nginx: `docker-compose logs nginx | tail -20`
- [ ] Certbot: `docker-compose exec certbot certbot certificates`

## Post-Deployment

### Security
- [ ] Changed admin password from default
- [ ] Verified `.env.prod` not in git
- [ ] Verified `certbot/cloudflare.ini` not in git
- [ ] Reviewed security headers: `curl -I https://roommate.klauvi.is`
- [ ] Verified HTTPS redirect working: `curl -I http://roommate.klauvi.is`
- [ ] Checked for exposed credentials in logs

### Monitoring
- [ ] Set up log monitoring
- [ ] Configure alerting for errors
- [ ] Set up uptime monitoring (optional)
- [ ] Configure backup schedule

### Backup
- [ ] Test database backup: `docker-compose exec db pg_dump -U roommate_user roommate > test_backup.sql`
- [ ] Test backup restore
- [ ] Set up automated backups
- [ ] Verify backups stored off-site

### Documentation
- [ ] Document server details (IP, credentials location)
- [ ] Share admin credentials securely with team
- [ ] Update project documentation with production URLs

### Testing
- [ ] Create test player
- [ ] Generate selection link
- [ ] Test roommate selection flow
- [ ] Verify email/SMS (if configured)
- [ ] Test CSV export

## Maintenance Tasks

### Daily
- [ ] Check service health: `docker-compose ps`
- [ ] Review error logs: `docker-compose logs --tail=100 | grep ERROR`

### Weekly
- [ ] Check disk usage: `df -h` and `docker system df`
- [ ] Review application logs
- [ ] Verify backups working
- [ ] Check certificate expiry: `docker-compose exec certbot certbot certificates`

### Monthly
- [ ] Update Docker images: `docker-compose pull`
- [ ] Update Python packages: `pip list --outdated`
- [ ] Review security advisories
- [ ] Test disaster recovery procedure

## Troubleshooting

### Services Won't Start
1. Check logs: `docker-compose logs`
2. Verify environment variables: `docker-compose config`
3. Check disk space: `df -h`
4. Rebuild: `docker-compose build --no-cache`

### SSL Certificate Issues
1. Check Cloudflare API token is valid
2. Verify DNS records: `dig roommate.klauvi.is`
3. Check certbot logs: `docker-compose logs certbot`
4. Manually renew: `docker-compose exec certbot certbot renew --force-renewal`

### Database Connection Errors
1. Check database is running: `docker-compose ps db`
2. Check credentials in `.env.prod`
3. Test connection: `docker-compose exec db psql -U roommate_user -d roommate`
4. Check logs: `docker-compose logs db`

### Static Files Not Loading
1. Recollect: `docker-compose exec web python manage.py collectstatic --noinput`
2. Check nginx logs: `docker-compose logs nginx`
3. Verify volume mounts: `docker-compose exec nginx ls -la /app/staticfiles/`
4. Check permissions

### Application Errors
1. Check Django logs: `docker-compose logs web`
2. Access Django shell: `docker-compose exec web python manage.py shell`
3. Check environment: `docker-compose exec web env`
4. Restart service: `docker-compose restart web`

## Rollback Procedure

If deployment fails:
1. Stop services: `docker-compose down`
2. Restore database: `docker-compose exec -T db psql -U roommate_user roommate < backup.sql`
3. Checkout previous version: `git checkout <previous-commit>`
4. Rebuild and deploy: `docker-compose up -d --build`

## Emergency Contacts

- **Hosting Provider**: _______________
- **Domain Registrar**: Cloudflare
- **DevOps Lead**: _______________
- **Emergency Email**: klauvi@gmail.com

## Success Criteria

✅ All services running and healthy
✅ HTTPS working with valid certificate  
✅ Admin can login and manage players
✅ Players can submit roommate selections
✅ Data persists across container restarts
✅ Logs accessible and monitored
✅ Backups configured and tested
✅ Security headers properly set
✅ No exposed credentials or secrets
✅ Documentation up to date

---

**Deployment Date**: _______________  
**Deployed By**: _______________  
**Server IP**: _______________  
**Notes**: _______________
