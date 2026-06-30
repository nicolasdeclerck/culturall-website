# Cultur'all

Site vitrine de l'association Cultur'all, permettant de présenter ses projets culturels et de recevoir des demandes de contact. Le back-office Wagtail permet aux administrateurs de gérer les contenus (projets, pages, paramètres du site).

## Stack technique

| Couche | Technologie |
|---|---|
| Application / CMS | Django 5.2, Wagtail 7.4 — rendu serveur (templates Django/Wagtail + HTMX + Alpine.js) |
| Base de données | PostgreSQL 16 |
| Stockage médias | MinIO (S3-compatible, self-hosted) |
| Reverse proxy | Nginx (preprod/TNR) · Traefik (production) |
| CI/CD | GitHub Actions → GHCR → VPS |

## Dépendances front-end (JS / CSS)

Le site est rendu côté serveur (templates Django/Wagtail) : **pas de build front, pas de npm**. Les quelques librairies front sont des fichiers statiques autonomes, versionnés dans le dépôt sous `backend/static/` et inclus dans [`backend/templates/base.html`](backend/templates/base.html).

| Librairie | Rôle sur le site | Documentation |
|---|---|---|
| **HTMX** | Permet de déclencher des requêtes serveur (et de remplacer des fragments de page) directement depuis des attributs HTML, sans écrire de JavaScript — pour les interactions dynamiques tout en restant en rendu serveur. | [htmx.org/docs](https://htmx.org/docs/) |
| **Alpine.js** | Micro-framework de réactivité « dans le HTML » (attributs `x-data`, `x-show`…). Gère les comportements d'interface légers, par ex. le header (état « scrolled », menu mobile) défini dans `site.js`. | [alpinejs.dev](https://alpinejs.dev/) |
| **AOS** (Animate On Scroll) | Anime l'apparition des éléments à leur entrée dans le viewport, pilotée par de simples attributs `data-aos` (ex. `data-aos="fade-right"`). Utilisé notamment par le bloc « Texte illustré » (slide du texte et de l'image). Initialisé dans `site.js`, désactivé automatiquement si l'utilisateur a activé « réduire les animations ». | [github.com/michalsnik/aos](https://github.com/michalsnik/aos) |
| **site.js** | Code maison du site : enregistre les composants Alpine (header) et initialise AOS. | — |

> Mise à jour d'une librairie : remplacer le fichier correspondant dans `backend/static/js/` (ou `css/`) par la nouvelle version, puis relancer `collectstatic` en production.

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

Cela démarre Django (Wagtail), PostgreSQL et MinIO. Le hot-reload est actif (sources montées). Nginx n'est pas lancé en dev : on accède à Django directement.

### 4. Accéder à l'application

| Service | URL |
|---|---|
| Site (Django/Wagtail) | http://localhost:8000 |
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
  - `media.cultur-all.org` (médias MinIO)
  - `stats-culturall.nickorp.com` (tableau de bord Plausible — optionnel, mesure d'audience)

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
MINIO_PUBLIC_URL=https://media.cultur-all.org
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

1. **Push sur `main`** → GitHub Actions build l'image Django, la pousse sur GHCR
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

## Mesure d'audience (Plausible)

Le nombre de **visiteurs par page** est mesuré via une instance **Plausible
Community Edition** auto-hébergée (sans cookie, RGPD-friendly). Le script de
mesure n'est injecté que pour les **visiteurs anonymes** : les utilisateurs
connectés sont exclus des statistiques.

- Activation côté site : variables `PLAUSIBLE_DOMAIN` / `PLAUSIBLE_SCRIPT_URL`
  (cf. `.env.example`). Laissées vides, la mesure est désactivée.
- Stack dédiée : `docker-compose.analytics.yml` (+ `.env.analytics.example`).
- Déploiement et exploitation : voir [`docs/analytics-plausible.md`](docs/analytics-plausible.md).

## Structure du projet

```
culturall-website/
├── backend/                 # Django 5.2 / Wagtail 7.4 (rendu serveur)
│   ├── config/              #   Settings (base, dev, test, prod)
│   ├── home/                #   HomePage + contact + ContactSubmission
│   ├── blog/                #   Articles (ArticlePage, BlogIndexPage)
│   ├── projects/            #   Projets (ProjectPage, ProjectsIndexPage)
│   ├── pages/               #   Pages statiques (StaticContentPage)
│   ├── network/             #   Membres du réseau (snippets)
│   ├── templates/           #   base.html, header, footer
│   ├── static/              #   CSS + JS (htmx, Alpine, AOS, site.js)
│   └── site_settings/       #   Paramètres globaux du site
├── docker/                  # Dockerfile django + config nginx (preprod/TNR)
├── docker-compose.*.yml     # base + overrides (dev, test, preprod, prod)
├── scripts/                 # tnr-docker.sh
├── docs/                    # Documentation complémentaire
└── .github/workflows/       # CI/CD GitHub Actions
```
