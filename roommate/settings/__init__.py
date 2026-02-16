"""Settings package initialization."""

import os

# Default to development settings
DJANGO_ENV = os.environ.get("DJANGO_ENV", "dev")

if DJANGO_ENV == "prod":
    from .prod import *
else:
    from .dev import *
