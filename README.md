# Cultur'all

Site vitrine de l'association Cultur'all, permettant de présenter ses projets culturels et de recevoir des demandes de contact. Le back-office Wagtail permet aux administrateurs de gérer les contenus (projets, pages, paramètres du site).

## Stack technique

| Couche | Technologie |
|---|---|
| Frontend | Next.js 14, React 18, TypeScript |
| Backend / CMS | Django 5.1, Wagtail 6.3 (headless) |
| Base de données | PostgreSQL 16 |
| Stockage médias | MinIO (S3-compatible, self-hosted) |
| Reverse proxy | Nginx (dev/preprod) · Traefik (production) |
| CI/CD | GitHub Actions → GHCR → VPS |

## Prérequis

- Docker et Docker Compose
- Git

## Installation — Environnement de développement

### 1. Cloner le dépôt

```bash
git clone git@github.com:nicolasdeclerck/culturall-website.git
cd culturall-website
```

### 2. Créer le fichier d'environnement

```bash
cp .env.example .env.dev
```

Les valeurs par défaut de `.env.example` sont prêtes pour le développement local. Aucune modification n'est nécessaire pour un premier lancement.

### 3. Lancer les services

```bash
docker compose -p culturall-website \
  -f docker-compose.base.yml \
  -f docker-compose.dev.yml \
  --env-file .env.dev \
  up
```

Cela démarre 5 services : Django, Next.js, PostgreSQL, MinIO et Nginx. Le hot-reload est actif pour le frontend et le backend.

### 4. Accéder à l'application

| Service | URL |
|---|---|
| Site (via Nginx) | http://localhost |
| Next.js (direct) | http://localhost:3000 |
| Django API | http://localhost:8000 |
| Admin Wagtail | http://localhost:8000/admin/ |
| Console MinIO | http://localhost:9001 |

### 5. Initialiser la base de données (premier lancement)

```bash
# Appliquer les migrations
docker compose -p culturall-website \
  -f docker-compose.base.yml \
  -f docker-compose.dev.yml \
  --env-file .env.dev \
  exec -T django python manage.py migrate

# Créer un super-utilisateur
docker compose -p culturall-website \
  -f docker-compose.base.yml \
  -f docker-compose.dev.yml \
  --env-file .env.dev \
  exec django python manage.py createsuperuser
```

## Installation — Production

La production utilise des images Docker pré-buildées, poussées sur GHCR par la CI, et servies derrière Traefik avec TLS automatique (Let's Encrypt).

### Prérequis sur le VPS

- Docker et Docker Compose installés
- Un container **Traefik** déjà en place, exposant les entrypoints `web` (80) et `websecure` (443) avec un cert resolver Let's Encrypt
- Le réseau Docker externe `traefik_default` créé (`docker network create traefik_default`)
- Les enregistrements DNS pointant vers le VPS :
  - `culturall-website.nickorp.com` (site)
  - `media.culturall-website.nickorp.com` (médias MinIO)

### 1. Cloner le dépôt sur le VPS

```bash
git clone git@github.com:nicolasdeclerck/culturall-website.git ~/culturall-website
cd ~/culturall-website
```

### 2. Configurer l'environnement de production

```bash
cp .env.example .env.prod
```

Modifier `.env.prod` avec les valeurs de production :

```
DJANGO_SECRET_KEY=<clé secrète forte>
DEBUG=False
ALLOWED_HOSTS=culturall-website.nickorp.com
CSRF_TRUSTED_ORIGINS=https://culturall-website.nickorp.com
MINIO_ROOT_PASSWORD=<mot de passe fort>
MINIO_PUBLIC_URL=https://media.culturall-website.nickorp.com
NEXT_PUBLIC_API_URL=https://culturall-website.nickorp.com
NODE_ENV=production
REGISTRY=ghcr.io/nicolasdeclerck/culturall-website
IMAGE_TAG=latest
```

### 3. Configurer les secrets GitHub Actions

Dans les paramètres du dépôt GitHub, ajouter les secrets suivants :

| Secret | Description |
|---|---|
| `VPS_HOST` | Adresse IP ou hostname du VPS |
| `VPS_SSH_KEY` | Clé SSH privée pour se connecter au VPS |
| `GHCR_USERNAME` | Nom d'utilisateur GitHub (pour push sur GHCR) |
| `GHCR_TOKEN` | Token GitHub avec le scope `packages:write` |

### 4. Pipeline de déploiement

Le déploiement est entièrement automatisé :

1. **Push sur `main`** → GitHub Actions build les images Django et Next.js, les pousse sur GHCR
2. **Deploy automatique** → SSH au VPS, pull des images, redémarrage des containers, migrations et collectstatic

Pour un premier déploiement manuel : Actions → **Deploy to Production** → Run workflow → `image_tag: latest`.

### 5. Lancer les services en production

```bash
docker compose -p culturall-website \
  -f docker-compose.base.yml \
  -f docker-compose.prod.yml \
  --env-file .env.prod \
  up -d
```

## Tests de non-régression (TNR)

Un environnement éphémère peut être lancé pour exécuter les tests browser :

```bash
./scripts/tnr-docker.sh up       # Démarrer l'environnement de test
./scripts/tnr-docker.sh status   # Vérifier l'état des services
./scripts/tnr-docker.sh down     # Détruire l'environnement
```

Les TNR tournent aussi automatiquement chaque nuit à 2h UTC via GitHub Actions.

## Structure du projet

```
culturall-website/
├── backend/                 # Django 5.1 / Wagtail 6.3
│   ├── config/              #   Settings (base, dev, test, prod)
│   ├── home/                #   HomePage + ContactSubmission
│   ├── projects/            #   Projets culturels (snippets Wagtail)
│   └── site_settings/       #   Paramètres globaux du site
├── frontend/                # Next.js 14
│   └── app/                 #   Pages : accueil, à propos, contact, login
├── docker/                  # Dockerfiles (django, nextjs) + config nginx
├── docker-compose.*.yml     # base + overrides (dev, test, preprod, prod)
├── scripts/                 # tnr-docker.sh
├── docs/                    # Documentation complémentaire
└── .github/workflows/       # CI/CD GitHub Actions
```
