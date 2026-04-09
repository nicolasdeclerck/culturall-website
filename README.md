# Infra template — Next.js + Django/Wagtail + MinIO

Variante du template d'infra pour la stack site vitrine **Next.js 14 + Django 5/Wagtail 6**,
avec MinIO comme stockage médias S3-compatible et déploiement via images
pré-buildées poussées sur GHCR.

> Si tu cherches la version Django classique sans Next.js, voir
> `../infra-template/`.

## Différences vs le template de base

| Aspect | Template de base | Cette variante |
|---|---|---|
| Stack | Django + frontend buildé en one-shot | Next.js standalone (long-running) + Django/Wagtail headless |
| Composes | 3 fichiers indépendants (`docker-compose.yml`, `.test.yml`, `.prod.yml`) | 1 base + 4 overrides (`base`, `dev`, `preprod`, `prod`, `test`) avec `--env-file` |
| Stockage médias | Volume Docker local | MinIO (init bucket auto via `minio-init`), prêt pour migration vers Cloudflare R2 |
| Reverse proxy prod | Traefik externe avec labels sur nginx | Traefik externe avec labels directement sur `django` + `nextjs` + `minio` |
| Reverse proxy preprod / TNR | Nginx en compose | Nginx en compose (inchangé, local uniquement) |
| Static files Django | Servis par nginx | Servis par **WhiteNoise** (Django middleware), Traefik proxie `/static/` vers django |
| Déploiement | `git pull` + `docker compose build` côté VPS | Build dans CI (GHCR) + `docker pull` côté VPS |
| Tests Phase 3 | `pytest` uniquement | `pytest` (Django/Wagtail) + `npm test --if-present` (Next.js) |
| Env files | `.env`, `.env.test`, `.env.prod` | `.env.dev`, `.env.test`, `.env.preprod`, `.env.prod` |

## Arborescence

```
infra-template-nextjs-wagtail/
├── .claude/
│   ├── settings.local.json
│   └── skills/
│       ├── agent-browser/                   ← générique, copié verbatim
│       ├── ticket-workflow/                 ← orchestration + 7 references
│       ├── browser-tests-on-demand/
│       └── regression-tests/
├── .github/workflows/
│   ├── ticket-workflow.yml                  ← inchangé
│   ├── build-images.yml                     ← NEW : build & push GHCR
│   ├── deploy-prod.yml                      ← REWRITTEN : pull au lieu de build
│   ├── browser-tests.yml
│   └── regression-tests.yml
├── docker-compose.base.yml                  ← services communs (5 + minio-init)
├── docker-compose.dev.yml                   ← hot reload, ports exposés
├── docker-compose.preprod.yml               ← build local + nginx HTTP
├── docker-compose.prod.yml                  ← image: ${REGISTRY}/...:${IMAGE_TAG} + labels Traefik
├── docker-compose.test.yml                  ← TNR éphémère, postgres+minio en tmpfs
├── docker/
│   ├── django/Dockerfile                    ← multi-stage Python 3.12 + WhiteNoise (note)
│   ├── nextjs/Dockerfile                    ← multi-stage Node 20, mode standalone
│   └── nginx/
│       └── preprod.conf                     ← upstream django + nextjs, HTTP (preprod + TNR)
├── scripts/tnr-docker.sh                    ← multi-compose, 2 services, MinIO bucket init
├── docs/
│   ├── github-actions-setup.md              ← secrets GHCR + labels + pipeline
│   └── browser-test-checklist.md            ← squelette à remplir
├── .env.example
├── .gitignore
└── README.md  ← tu es ici
```

## Glossaire des placeholders

| Placeholder | Description | Exemple |
|---|---|---|
| `{{REPO_OWNER}}` | Owner GitHub (user ou org) | `myorg` |
| `{{REPO_NAME}}` | Nom court du repo | `studio-site` |
| `{{WORKSPACE_PATH}}` | Chemin du clone interne au container `claude-worker` | `/workspace/studio-site` |
| `{{COMPOSE_PROJECT}}` | Nom du projet docker compose **sans suffixe** | `studio-site` (devient `studio-site-tnr` pour la TNR) |
| `{{DOMAIN}}` | Domaine principal de production | `studio.example.com` |
| `{{MEDIA_DOMAIN}}` | Sous-domaine pour les médias MinIO/R2 | `media.studio.example.com` |
| `{{TRAEFIK_NETWORK}}` | Network Docker externe sur lequel Traefik écoute | `traefik_default` |
| `{{CERT_RESOLVER}}` | Nom du cert resolver Let's Encrypt côté Traefik | `myresolver` |
| `{{REGISTRY}}` | Registry des images CI | `ghcr.io/myorg/studio-site` |
| `{{TEST_USER_EMAIL}}` | Email du user de test #1 | `testuser@example.com` |
| `{{TEST_USER_PASSWORD}}` | Mot de passe du user de test | `Testpass123!` |
| `{{LOGIN_URL_PATH}}` | Chemin de la page de connexion (Wagtail admin par défaut) | `/admin/login/` |
| `{{PROD_BASE_URL}}` | URL de production | `https://studio.example.com` |
| `{{POSTGRES_DB}}` | Base Postgres pour le healthcheck TNR | `app_test_db` |
| `{{WORKER_GIT_EMAIL}}` | Email Git utilisé par les commits du worker | `claude-worker@example.com` |
| `{{WORKER_GIT_NAME}}` | Nom Git utilisé par les commits du worker | `Claude Worker` |

> Les placeholders `{{HEALTHCHECK_CMD}}`, `{{MIGRATE_CMD}}`, `{{SEED_BLOCK}}`,
> `{{POST_DEPLOY_COMMAND}}`, `{{TEST_COMMAND}}` du template de base **n'existent
> plus** ici — ces commandes sont déjà inlinées dans `tnr-docker.sh`,
> `deploy-prod.yml` et `phase-3-develop.md` (Django/Wagtail + Next.js sont
> figés dans cette variante).

## Bootstrap d'un nouveau projet

### 1. Cloner ou copier le template

```bash
cp -r infra-template-nextjs-wagtail my-studio-site
cd my-studio-site
git init
```

### 2. Remplacer les placeholders simples

```bash
export REPO_OWNER=myorg
export REPO_NAME=studio-site
export WORKSPACE_PATH=/workspace/studio-site
export COMPOSE_PROJECT=studio-site
export DOMAIN=studio.example.com
export MEDIA_DOMAIN=media.studio.example.com
export TRAEFIK_NETWORK=traefik_default
export CERT_RESOLVER=myresolver
export TEST_USER_EMAIL=testuser@example.com
export TEST_USER_PASSWORD='Testpass123!'
export LOGIN_URL_PATH=/admin/login/
export PROD_BASE_URL=https://studio.example.com
export POSTGRES_DB=app_test_db
export WORKER_GIT_EMAIL=claude-worker@example.com
export WORKER_GIT_NAME='Claude Worker'

# IMPORTANT : on exclut README.md du sed — son glossaire mentionne les
# placeholders avec leur syntaxe `{{...}}` et serait détruit par la substitution.
#
# NOTE portabilité : `sed -i ''` est la syntaxe BSD sed (macOS). Sur Linux
# (GNU sed), retire les guillemets vides : `sed -i \` tout court.
find . -type f -not -path './.git/*' -not -name 'README.md' -print0 | xargs -0 sed -i '' \
  -e "s|{{REPO_OWNER}}|$REPO_OWNER|g" \
  -e "s|{{REPO_NAME}}|$REPO_NAME|g" \
  -e "s|{{WORKSPACE_PATH}}|$WORKSPACE_PATH|g" \
  -e "s|{{COMPOSE_PROJECT}}|$COMPOSE_PROJECT|g" \
  -e "s|{{DOMAIN}}|$DOMAIN|g" \
  -e "s|{{MEDIA_DOMAIN}}|$MEDIA_DOMAIN|g" \
  -e "s|{{TRAEFIK_NETWORK}}|$TRAEFIK_NETWORK|g" \
  -e "s|{{CERT_RESOLVER}}|$CERT_RESOLVER|g" \
  -e "s|{{TEST_USER_EMAIL}}|$TEST_USER_EMAIL|g" \
  -e "s|{{TEST_USER_PASSWORD}}|$TEST_USER_PASSWORD|g" \
  -e "s|{{LOGIN_URL_PATH}}|$LOGIN_URL_PATH|g" \
  -e "s|{{PROD_BASE_URL}}|$PROD_BASE_URL|g" \
  -e "s|{{POSTGRES_DB}}|$POSTGRES_DB|g" \
  -e "s|{{WORKER_GIT_EMAIL}}|$WORKER_GIT_EMAIL|g" \
  -e "s|{{WORKER_GIT_NAME}}|$WORKER_GIT_NAME|g"
```

### 3. Configurer les `.env.*`

```bash
cp .env.example .env.dev
cp .env.example .env.test
cp .env.example .env.preprod
cp .env.example .env.prod
```

Adapte chaque fichier (en particulier `DEBUG`, `ALLOWED_HOSTS`,
`NEXT_PUBLIC_API_URL`, secrets MinIO, `IMAGE_TAG` pour `.env.prod`).

### 4. Ajouter le code applicatif

```
backend/        ← projet Django/Wagtail (manage.py, config/, requirements.txt)
frontend/       ← projet Next.js 14 (package.json, app/, next.config.js)
```

> **Important** : `next.config.js` doit contenir `output: 'standalone'`
> pour que le Dockerfile prod fonctionne.

### 5. Configurer GitHub

Voir `docs/github-actions-setup.md`. En résumé :

1. Créer les secrets `VPS_HOST`, `VPS_SSH_KEY`, `GHCR_USERNAME`, `GHCR_TOKEN`
2. Créer les labels (`analyze`, `in progress`, `approved`, `pending-browser-tests`, `help wanted`, `standby`, `non-regression tests`)
3. Activer GitHub Actions et donner `packages: write` au token

### 6. Préparer le VPS

1. **Traefik déjà en place** : un container Traefik doit déjà tourner sur le VPS,
   exposer les entrypoints `web` (80) et `websecure` (443), et avoir un cert
   resolver Let's Encrypt nommé `{{CERT_RESOLVER}}`. Le network Docker
   `{{TRAEFIK_NETWORK}}` doit exister (`docker network create traefik_default`
   si ce n'est pas déjà fait, puis l'attacher au container Traefik).
2. **DNS** : `{{DOMAIN}}` et `{{MEDIA_DOMAIN}}` doivent pointer vers l'IP du VPS.
3. Cloner le repo dans `~/{{REPO_NAME}}`
4. Installer Docker, Docker Compose, agent-browser
5. Lancer un container `claude-worker` avec un clone du repo dans `{{WORKSPACE_PATH}}`
6. Faire un login Claude MAX dans le container : `docker exec -it claude-worker claude`
7. Renseigner `.env.prod` avec les vraies valeurs (en particulier `MINIO_ROOT_PASSWORD`, `DJANGO_SECRET_KEY`, `REGISTRY`, `MINIO_PUBLIC_URL=https://{{MEDIA_DOMAIN}}`)
8. Ajouter `whitenoise[brotli]` à `backend/requirements.txt` et configurer le middleware (cf. note dans `docker/django/Dockerfile`)
9. Premier déploiement manuel via : Actions → Deploy to Production → Run workflow → `image_tag=latest`

### 7. Écrire le cahier de tests

`docs/browser-test-checklist.md` contient un squelette. Adapte-le aux
parcours de ton site (admin Wagtail, navigation Next.js, formulaires de
contact, etc.).

## Comment ça marche en 4 lignes

1. **Push sur `main`** → `build-images.yml` build les 2 images, les push sur GHCR avec le tag `<sha>`, déclenche `deploy-prod.yml`.
2. **`deploy-prod.yml`** → SSH au VPS, met à jour `IMAGE_TAG` dans `.env.prod`, `docker pull`, restart, `migrate` + `collectstatic` + `update_index`.
3. **Label `analyze` sur une issue** → `ticket-workflow.yml` lance Claude qui exécute Phases 1-5 du skill `ticket-workflow` (analyse → PR → auto-review).
4. **TNR (cron 2h UTC)** → `regression-tests.yml` démarre l'env éphémère via `tnr-docker.sh up`, lance la TNR complète sur `http://{{COMPOSE_PROJECT}}-tnr-nginx-1:80`, détruit l'env.

## Évolutions prévues (cf. ton document de stack)

| Sujet | Action future |
|---|---|
| Stockage médias | Migration MinIO → Cloudflare R2 : changer `MINIO_ENDPOINT_URL`, `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD` dans `.env.prod`, retirer le service `minio` (et ses labels Traefik) du compose, faire pointer le CNAME `{{MEDIA_DOMAIN}}` vers R2 au lieu du VPS |
| Frontend tests | Ajouter Vitest/Playwright et étoffer le step `npm test` de Phase 3 |
| Wagtail multilangue | Si activé, adapter `LOGIN_URL_PATH` et le seed Wagtail dans `tnr-docker.sh` |
# infra-template-nextjs-wagtail
# culturall-website
# culturall-website
