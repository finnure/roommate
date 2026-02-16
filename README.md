# Roommates

An Icelandic soccer team is going to Portugal this summer to participate in IberCup. In the hotel, there will be 3 players in each room. This project was created to help with room assignments. Each player needs to choose 3 other players they would like to stay with. They are guaranteed to be matched with at least one of their selected options. After all players have made their selections, there is an option to generate room assignments that uses the selections from all players.

## Quick Start

### Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit http://127.0.0.1:8000/admin/

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete production deployment instructions using Docker Compose.

**Quick production deploy:**
```bash
cp .env.prod.example .env.prod
cp certbot/cloudflare.ini.example certbot/cloudflare.ini
# Edit both files with your credentials
./deploy.sh
```

## Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete production deployment guide
- **[DOCKER_COMMANDS.md](DOCKER_COMMANDS.md)** - Docker and Docker Compose command reference
- **[CHANGELOG.md](CHANGELOG.md)** - Project change history
- **[AGENTS.md](AGENTS.md)** - Agent configuration

## Features

- **Admin Dashboard** - Manage players and generate selection links
- **Roommate Selection** - Players select their preferred roommates
- **Verification System** - Email/SMS verification of selections
- **Room Assignment** - Automated room assignment based on preferences
- **Export Data** - CSV export of assignments

## Tech Stack

- **Backend**: Django 6.0, Python 3.14
- **Database**: PostgreSQL (production), SQLite (development)
- **Cache**: Redis
- **Task Queue**: Celery
- **Web Server**: Nginx + Gunicorn
- **SSL**: Let's Encrypt via Certbot
- **Deployment**: Docker Compose

