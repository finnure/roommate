# Project Context

This project is for a soccer team going to Portugal on a trip. The hotel has rooms for 3 people, and we need to assign players to rooms. Each player should be able to select exactly 3 other players they want to room with.

# Requirements
1. Create an admin site to manage players and send out links to the roommate selection form.
2. Create an unauthenticated page with a query parameter for generated selection id. The page should lookup the id to find the player and have a heading greeting the player by name, example: "Halló Ólafur!".
3. The page should start with a single dropdown with all the other players as options. When the player selects another player, a new dropdown should appear with the remaining players as options. This should continue until the player has selected 3 other players.
4. The form should not be valid until the player has selected 3 other players. Once the form is submitted, the selections should be saved as a draft. A verification code should be generated and sent to the player via sms or email (for the sake of this project, you can just print the code to the console). The player should then be able to enter the verification code on a separate page to confirm their selections. Once confirmed, the selections should be marked as final and no further changes should be allowed.
5. The admin site should have a page to view the final roommate assignments and a way to export the data as a CSV file.


# ⚠️ CRITICAL: CHANGELOG.md UPDATE RULES ⚠️

**MANDATORY: After EVERY code change, file creation, configuration update, or bugfix, you MUST update CHANGELOG.md. NO EXCEPTIONS.**

## When to Update CHANGELOG.md (ALL of these):
1. ✅ **New Features**: Any new functionality added to the project
2. ✅ **Bugfixes**: ANY bug that was fixed, no matter how small
3. ✅ **Configuration Changes**: New/modified config files (.prettierrc, .vscode/settings.json, etc.)
4. ✅ **Model Changes**: Database schema modifications
5. ✅ **Template Updates**: New or modified HTML templates
6. ✅ **View/URL Changes**: New views, modified business logic
7. ✅ **Deployment Changes**: Docker, nginx, deployment scripts
8. ✅ **Dependency Updates**: New packages or version changes

## CHANGELOG Entry Format:

### For Features/Changes:
```
## [Feature Title] - [Date]

### User Request
[Original user request verbatim]

### What Was Created/Modified
[Detailed list with file links]

### How to Use
[Usage instructions]

### Technical Details
[Implementation notes]
```

### For Bugfixes:
```
## Bugfix: [Brief Title] - [Date]

### Issue
[Clear description of the bug]

### Fix
[What was fixed with file paths and line numbers]

**Root Cause**: [Why it happened]

**Testing**: [How to verify the fix]
```

## Verification Checklist
Before completing ANY task, verify:
- [ ] Did I create or modify any files?
- [ ] Did I fix a bug?
- [ ] Did I add a feature?
- [ ] **If YES to any: Did I update CHANGELOG.md?**

**If you did NOT update CHANGELOG.md, STOP and do it NOW.**

---

# Copilot Instructions for Django Project

Follow these rules for all suggestions:

1. **Environment**: Python 3.14 venv in WSL Ubuntu. Interpreter: `./.venv/bin/python`.
2. **Django Patterns**:
   - Prefer CBVs: `ListView`, `CreateView` with `form_class`.
   - APIs: Django REST Framework (DRF) with `generics` or `viewsets`.
   - Models: Abstract base + `UUIDField` for PK.
3. **Best Practices**:
   - Atomic transactions for DB ops.
   - Celery for background tasks.
   - Redis for cache/sessions.
   - Dockerize for prod (docker-compose.yml).
4. **Lint/Format**: Black, isort, flake8. Pre-commit hooks.
5. **Testing**: `pytest -v --cov=core`.
6. **No Bloat**: Minimal deps; justify additions.
7. **Documentation**: Update README.md and relevant docs with new features or changes.

Example model:
```python
from django.db import models
from uuid import uuid4

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```
