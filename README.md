# Cultur'all

Site vitrine de l'association Cultur'all, permettant de présenter ses projets culturels et de recevoir des demandes de contact. Le back-office Wagtail permet aux administrateurs de gérer les contenus (projets, pages, paramètres du site).

## Stack technique

| Couche | Technologie |
|---|---|
| Frontend | Next.js 14, React 18, TypeScript |
| Backend / CMS | Django 5.1, Wagtail 6.3 (headless) |
| Base de données | PostgreSQL 16 |
| Stockage médias | MinIO (S3-compatible, self-hosted) |
| Reverse proxy | Nginx (dev) · Traefik (preprod/prod) |
| CI/CD | GitHub Actions → GHCR → VPS |

## Environnements

| Env | URL | VPS | Traefik | Déploiement |
|---|---|---|---|---|
| Dev | http://localhost | local | nginx | manuel |
| Preprod | https://culturall-website.nickorp.com | partagé (n8n-traefik) | externe | auto sur push `main` |
| Prod | https://cultur-all.org | dédié | embarqué dans le compose | manuel via Actions |

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

## Pipeline CI/CD

```
push main
   │
   ▼
build-images.yml  ──► tests backend + build Django/Next.js + push GHCR
   │
   ▼
deploy-preprod.yml  (auto)  ──► VPS preprod (n8n-traefik)
                                   https://culturall-website.nickorp.com

[manuel] deploy-prod.yml      ──► VPS prod (Traefik dédié)
                                   https://cultur-all.org
```

- **Push sur `main`** → build + déploiement automatique sur **preprod** uniquement
- **Prod** → déploiement **manuel** : Actions → **Deploy to Production** → Run workflow → `image_tag: latest` (ou un SHA précis)

## Installation — Pré-production

La preprod tourne sur un VPS partagé avec un stack Traefik externe (`n8n-traefik`, réseau `n8n-traefik_default`).

### Prérequis sur le VPS

- Docker et Docker Compose installés
- Stack **Traefik** (`n8n-traefik`) déjà déployé, exposant les entrypoints `web` (80) et `websecure` (443) avec un cert resolver Let's Encrypt nommé `myresolver`
- Le réseau Docker externe `n8n-traefik_default` existant
- Enregistrements DNS pointant vers le VPS :
  - `culturall-website.nickorp.com`
  - `media.culturall-website.nickorp.com`

### 1. Cloner le dépôt sur le VPS

```bash
git clone git@github.com:nicolasdeclerck/culturall-website.git ~/n8n-traefik/repos/culturall-website
cd ~/n8n-traefik/repos/culturall-website
```

### 2. Configurer l'environnement

```bash
cp .env.example .env.preprod
```

À renseigner :

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

### 3. Premier lancement manuel

```bash
docker compose -p culturall-website \
  -f docker-compose.base.yml \
  -f docker-compose.preprod.yml \
  --env-file .env.preprod \
  up -d
```

Puis : `migrate` + `collectstatic` + `createsuperuser` comme en dev. Les déploiements suivants sont automatiques via `deploy-preprod.yml`.

## Installation — Production

La prod tourne sur un VPS dédié au site `cultur-all.org`. Traefik est embarqué dans `docker-compose.prod.yml` (pas de stack Traefik partagé). TLS automatique via Let's Encrypt (challenge TLS-ALPN sur :443).

### Prérequis sur le VPS

- Docker et Docker Compose installés
- Ports 80 et 443 libres (Traefik les utilise)
- Enregistrements DNS pointant vers le VPS :
  - `cultur-all.org`
  - `www.cultur-all.org` (redirige vers `cultur-all.org` via Traefik)
  - `media.cultur-all.org`

### 1. Cloner le dépôt sur le VPS

```bash
git clone git@github.com:nicolasdeclerck/culturall-website.git ~/culturall-website
cd ~/culturall-website
```

### 2. Configurer l'environnement

```bash
cp .env.example .env.prod
```

À renseigner :

```
DJANGO_SECRET_KEY=<clé secrète forte>
DEBUG=False
ALLOWED_HOSTS=cultur-all.org,www.cultur-all.org
CSRF_TRUSTED_ORIGINS=https://cultur-all.org,https://www.cultur-all.org
MINIO_ROOT_PASSWORD=<mot de passe fort>
MINIO_PUBLIC_URL=https://media.cultur-all.org
NEXT_PUBLIC_API_URL=https://cultur-all.org
NODE_ENV=production
ACME_EMAIL=<email pour Let's Encrypt>
REGISTRY=ghcr.io/nicolasdeclerck/culturall-website
IMAGE_TAG=latest
```

### 3. Configurer les secrets GitHub Actions

Dans les paramètres du dépôt GitHub, ajouter les secrets suivants :

| Secret | Description |
|---|---|
| `VPS_HOST` | IP/hostname du VPS de **prod** |
| `VPS_SSH_KEY` | Clé SSH privée pour le VPS de **prod** |
| `PREPROD_VPS_HOST` | IP/hostname du VPS de **preprod** |
| `PREPROD_VPS_SSH_KEY` | Clé SSH privée pour le VPS de **preprod** |
| `GHCR_USERNAME` | Nom d'utilisateur GitHub (push GHCR) |
| `GHCR_TOKEN` | Token GitHub avec scope `packages:write` |

### 4. Premier lancement

```bash
docker compose -p culturall-website \
  -f docker-compose.base.yml \
  -f docker-compose.prod.yml \
  --env-file .env.prod \
  up -d
```

Traefik négocie automatiquement les certificats Let's Encrypt au premier accès HTTPS. Les déploiements suivants se font manuellement via : Actions → **Deploy to Production** → Run workflow.

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
├── backend/                    # Django 5.1 / Wagtail 6.3
│   ├── config/                 #   Settings (base, dev, test, prod)
│   ├── home/                   #   HomePage + ContactSubmission
│   ├── projects/               #   Projets culturels (snippets Wagtail)
│   └── site_settings/          #   Paramètres globaux du site
├── frontend/                   # Next.js 14
│   └── app/                    #   Pages : accueil, à propos, contact, login
├── docker/                     # Dockerfiles (django, nextjs) + config nginx (TNR)
├── docker-compose.base.yml     # Services communs (django, nextjs, postgres, minio, nginx)
├── docker-compose.dev.yml      # Override dev (hot-reload, ports exposés)
├── docker-compose.test.yml     # Override TNR (éphémère, tmpfs)
├── docker-compose.preprod.yml  # Override preprod (GHCR + Traefik externe)
├── docker-compose.prod.yml     # Override prod (GHCR + Traefik embarqué)
├── scripts/                    # tnr-docker.sh
├── docs/                       # Documentation complémentaire
└── .github/workflows/          # build-images / deploy-preprod / deploy-prod
```
