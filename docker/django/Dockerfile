# Backend — Django + Wagtail (multi-stage)
#
# Targets :
#   - development  : hot reload, outils dev
#   - production   : Gunicorn + WhiteNoise, utilisateur non-root
#
# Le code applicatif vit dans ../backend (contexte de build = ./backend
# dans les compose files).
#
# IMPORTANT — WhiteNoise est requis en production
# ───────────────────────────────────────────────
# Le reverse proxy en prod est Traefik, qui ne sert pas les fichiers statiques.
# Il faut donc que Django serve lui-même /static/ via WhiteNoise.
#
# Ajouter dans backend/requirements.txt :
#   whitenoise[brotli]
#
# Ajouter dans backend/config/settings/production.py :
#   MIDDLEWARE = [
#       'django.middleware.security.SecurityMiddleware',
#       'whitenoise.middleware.WhiteNoiseMiddleware',  # ← juste après SecurityMiddleware
#       ...
#   ]
#   STORAGES = {
#       "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
#       # default storage = django-storages S3 → MinIO
#   }
#
# /media/ est servi par MinIO directement via le sous-domaine media.culturall-website.nickorp.com.

# ─── Stage : base ──────────────────────────────────────────────
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        wget \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ─── Stage : deps (layer cacheable) ────────────────────────────
FROM base AS deps

COPY requirements.txt .
RUN pip install -r requirements.txt

# ─── Stage : development ───────────────────────────────────────
FROM deps AS development

# Outils dev (à compléter selon les besoins)
RUN pip install ipython pytest pytest-django pytest-cov

COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ─── Stage : production ────────────────────────────────────────
FROM deps AS production

COPY . .

# Utilisateur non-root
RUN groupadd -r app && useradd -r -g app app \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R app:app /app

USER app

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
