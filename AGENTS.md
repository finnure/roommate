# AGENTS.md

## Environment
Python 3.14 venv (WSL Ubuntu), Django 6.x, VS Code with `./.venv/bin/python`

## Architecture
- Monolith: core/ app handles models/views/URLs
- Settings split: base.py, dev.py, prod.py
- PostgreSQL prod, SQLite dev

## Code Style
- Black + isort formatting
- Type hints everywhere
- Google docstrings
- CBVs over FBVs

## Commands
- `source .venv/bin/activate && python manage.py runserver`
- `pytest -v --cov`
- `black . && isort .`

## Testing
100% coverage required. Use pytest fixtures.

## NEVER
- Global interpreters
- Raw SQL without params
- JS frameworks (Tailwind only)
