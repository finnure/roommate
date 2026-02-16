# Django Best Practices for this Project

## Tech Stack & Constraints
- Django 5.x (or latest stable) on Python 3.14 venv.
- Ubuntu WSL, VS Code with Python extension + venv selected (`./.venv/bin/python`).
- Use async views/DRF where possible; class-based views (CBVs) preferred.
- PostgreSQL for prod, SQLite for dev.
- Tailwind/CSS for frontend (no heavy JS unless specified).
- Git flow: feature branches, descriptive commits.

## Code Style
- PEP 8 + Black formatter (`pip install black`).
- Type hints everywhere: `from typing import ...`.
- Docstrings: Google style.
- Settings: Split to `base.py`, `dev.py`, `prod.py`; use `python-decouple` for secrets.
- Models: Use `models.JSONField` for flexible data; custom managers.
- URLs: App-specific routers, no hardcoding.
- Tests: Pytest + coverage >90%; fixtures for DB.

## Security & Patterns
- CSRF/Django defaults always.
- Permissions: `permissions.IsAuthenticated` or custom.
- Serializers for all API.
- Logging: Structured with `structlog`.
- Errors: Custom 404/500 handlers.

## Project Structure

roommate/
├── manage.py
├── requirements.txt # pip freeze
├── .env # secrets
├── .vscode/settings.json # venv path
├── roommate/ # project
│ ├── settings/
│ ├── urls.py
│ └── wsgi.py
├── core/ # main app
│ ├── models.py
│ ├── views.py
│ ├── urls.py
│ └── tests/
└── staticfiles/


## Commands
- Run dev: `python manage.py runserver`
- Migrations: `makemigrations && migrate`
- Superuser: `createsuperuser`

Generate code following this exactly. Ask for clarification on unclear requirements.
