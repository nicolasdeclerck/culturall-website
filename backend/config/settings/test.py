"""Settings TNR — iso-prod mais sans contraintes HTTPS (HTTP only)."""

from .production import *  # noqa: F401,F403

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
