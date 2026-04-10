# Configuration GitHub Actions — Stack Next.js + Django/Wagtail

## Prérequis

- Un VPS avec Docker installé et le container `claude-worker` en cours d'exécution
- Une session Claude Code MAX active dans `claude-worker`
- Une clé SSH permettant l'accès au VPS
- Un compte GitHub avec les permissions sur le repo et sur GHCR (`packages: write`)
- **Un Traefik déjà déployé sur le VPS**, exposant les entrypoints `web` (80)
  et `websecure` (443), avec un cert resolver Let's Encrypt configuré, et
  attaché à un network Docker externe partagé (par défaut `traefik_default`).
  Les services `django`, `nextjs` et `minio` s'enregistrent auprès de Traefik
  via des labels — pas de nginx ni de certbot dans le compose de prod.
- **DNS** : `culturall-website.nickorp.com` et `media.culturall-website.nickorp.com` doivent pointer vers l'IP du VPS
  (records A ou AAAA) avant le premier déploiement, pour que Let's Encrypt
  puisse émettre les certificats.
- **Clone du repo sur le VPS** : le dépôt doit être cloné à `~/n8n-traefik/repos/culturall-website`
  (ce chemin est utilisé par les workflows de déploiement, de tests browser et de TNR) :
  ```bash
  ssh ubuntu@<VPS_HOST>
  mkdir -p ~/n8n-traefik/repos
  cd ~/n8n-traefik/repos
  git clone git@github.com:nicolasdeclerck/culturall-website.git
  ```

## Secrets à configurer

Aller dans **Settings → Secrets and variables → Actions → New repository secret** :

| Secret | Description | Exemple |
|---|---|---|
| `VPS_HOST` | IP ou nom de domaine du VPS | `vps.example.com` |
| `VPS_SSH_KEY` | Contenu complet de la clé privée SSH | Contenu de `~/.ssh/id_ed25519` |
| `GHCR_USERNAME` | Compte GitHub avec accès au registry GHCR | `myorg-deploy` |
| `GHCR_TOKEN` | PAT classic avec scope `read:packages` (utilisé par `docker login` côté VPS) | `ghp_…` |

> **Note :** `GITHUB_TOKEN` est injecté automatiquement par GitHub Actions
> et possède déjà `packages: write` pour pousser sur GHCR. Le `GHCR_TOKEN`
> est uniquement nécessaire pour que le **VPS** puisse `docker pull` les
> images privées via SSH.

## Labels GitHub à créer sur le repo

```bash
gh label create "analyze"                  --description "Déclenche le ticket-workflow" --color "0e8a16"
gh label create "in progress"              --description "Ticket en cours de traitement" --color "fbca04"
gh label create "approved"                 --description "Code review approuvé"          --color "0e8a16"
gh label create "pending-browser-tests"    --description "Tests browser à exécuter"      --color "f9d0c4"
gh label create "help wanted"              --description "Intervention humaine requise"  --color "d93f0b"
gh label create "standby"                  --description "Workflow en pause"             --color "c5def5"
gh label create "non-regression tests"     --description "Issue liée aux TNR"            --color "5319e7"
```

## Workflows fournis

| Workflow | Déclencheur | Rôle |
|----------|-------------|------|
| `ticket-workflow.yml` | Label `analyze` posé sur une issue | Lance les Phases 1–5 du skill `ticket-workflow` |
| `build-images.yml` | Push sur `main` (+ manuel) | Build les images Django + Next.js, push sur GHCR, déclenche `deploy-prod.yml` avec le tag de commit |
| `deploy-prod.yml` | Manuel ou depuis `build-images.yml` | SSH sur le VPS, met à jour `.env.prod` avec `IMAGE_TAG`, pull les images, redémarre, migrate, collectstatic, update_index |
| `browser-tests.yml` | Manuel (`workflow_dispatch`) | Démarre l'env Docker éphémère, lance le skill `browser-tests-on-demand`, détruit l'env |
| `regression-tests.yml` | Cron (2h UTC) + manuel | Lance la TNR complète sur l'env éphémère si des PR ont été mergées dans les 24h |

## Pipeline CI/CD complet

```
git push main
    ↓
build-images.yml
  ├─ build django (target=production)
  ├─ build nextjs (target=production)
  ├─ push ghcr.io/.../django:<sha>
  ├─ push ghcr.io/.../nextjs:<sha>
  └─ trigger deploy-prod.yml --image_tag=<sha>
       ↓
deploy-prod.yml (SSH au VPS)
  ├─ git pull (compose files)
  ├─ sed IMAGE_TAG=<sha> dans .env.prod
  ├─ docker login ghcr.io
  ├─ docker compose pull django nextjs
  ├─ docker compose up -d --force-recreate
  ├─ python manage.py migrate
  ├─ python manage.py collectstatic
  └─ python manage.py update_index (Wagtail search)
```

## Vérification du container claude-worker

Sur le VPS :

```bash
docker ps | grep claude-worker
docker exec claude-worker claude --version
```

Si la session est expirée :

```bash
ssh ubuntu@<VPS_HOST>
docker exec -it claude-worker claude
# Suivre la procédure de login interactif
```
