# Mesure d'audience — Plausible Community Edition (auto-hébergé)

Ce document décrit le **suivi du nombre de visiteurs par page** du site
Cultur'all, via une instance **Plausible Community Edition** auto-hébergée.

## Pourquoi Plausible

- **Sans cookie** → conforme RGPD, **pas de bannière de consentement** à ajouter.
- Fournit nativement, **par page**, les **visiteurs uniques** et les **pages vues**.
- **Auto-hébergé** : les données restent sur l'infrastructure de l'association.

## Principe : exclusion des utilisateurs connectés

Le besoin est de compter les visiteurs **hors utilisateurs connectés**. Le
suivi étant fait côté navigateur (un petit script), l'exclusion est réalisée
**à la source** : le script de mesure n'est injecté dans la page **que pour les
visiteurs anonymes**.

Concrètement, dans `backend/templates/base.html` :

```django
{% if PLAUSIBLE_DOMAIN and PLAUSIBLE_SCRIPT_URL and not request.user.is_authenticated %}
<script defer data-domain="{{ PLAUSIBLE_DOMAIN }}" src="{{ PLAUSIBLE_SCRIPT_URL }}"></script>
{% endif %}
```

- Un utilisateur **connecté** (back-office Wagtail) ne reçoit jamais le script
  → ses visites ne sont **jamais** comptées.
- Tant que `PLAUSIBLE_DOMAIN` / `PLAUSIBLE_SCRIPT_URL` ne sont pas renseignés
  (dev, tests, CI), **aucun** script n'est chargé.

Les variables sont exposées aux templates par le context processor
`home.context_processors.analytics` et lues depuis l'environnement dans
`config/settings/base.py`.

## Architecture

```
                         ┌────────────────────────────────────────┐
  Navigateur visiteur ──▶│ stats-culturall.nickorp.com (Traefik)  │──▶ plausible
   (script.js + events)  └────────────────────────────────────────┘      │
                                                     ┌───────────────────┴─────┐
                                                     ▼                         ▼
                                              plausible_db            plausible_events_db
                                              (PostgreSQL)               (ClickHouse)
```

La stack vit dans `docker-compose.analytics.yml`, **indépendante** de
l'application (elle n'impose ni ClickHouse ni dépendance supplémentaire au
stack principal ou à la CI). Elle rejoint le **réseau Traefik externe** déjà en
place sur le VPS.

## Déploiement (production)

### 1. DNS

Créer un enregistrement pointant vers le VPS :

```
stats-culturall.nickorp.com  →  <IP du VPS>
```

### 2. Configurer les secrets de l'instance

```bash
cp .env.analytics.example .env.analytics
```

Renseigner dans `.env.analytics` :

```bash
BASE_URL=https://stats-culturall.nickorp.com
SECRET_KEY_BASE=$(openssl rand -base64 48)
TOTP_VAULT_KEY=$(openssl rand -base64 32)
PLAUSIBLE_DB_PASSWORD=<mot de passe fort>
DISABLE_REGISTRATION=true
```

> `.env.analytics` est ignoré par Git (cf. `.gitignore`) : ne jamais le committer.

### 3. Lancer la stack Plausible

```bash
docker compose -p culturall-analytics \
  -f docker-compose.analytics.yml \
  --env-file .env.analytics \
  up -d
```

Le service `plausible` crée et migre ses bases automatiquement au démarrage
(`db createdb && db migrate && run`). Traefik émet le certificat TLS
Let's Encrypt pour `stats-culturall.nickorp.com`.

### 4. Créer le compte admin et le site suivi

1. Ouvrir `https://stats-culturall.nickorp.com` → créer le **compte administrateur**.
2. **Add a website** → domaine **`cultur-all.org`** (sans `https://`).
   Plausible affiche alors un snippet ; on n'en a pas besoin (déjà intégré au
   site), mais on retient la valeur du `data-domain` = `cultur-all.org`.

### 5. Activer la mesure côté site

Dans le `.env.prod` du **site** (pas `.env.analytics`) :

```bash
PLAUSIBLE_DOMAIN=cultur-all.org
PLAUSIBLE_SCRIPT_URL=https://stats-culturall.nickorp.com/js/script.js
```

Puis redémarrer le conteneur Django pour recharger l'environnement :

```bash
docker compose -p culturall-website \
  -f docker-compose.base.yml -f docker-compose.prod.yml \
  --env-file .env.prod up -d django
```

### 6. Vérifier

- Ouvrir le site en **navigation privée** (donc anonyme), visiter quelques pages.
- Dans l'onglet **Réseau** du navigateur : une requête vers
  `stats-culturall.nickorp.com/api/event` (200) doit partir à chaque page.
- En étant **connecté** au back-office : **aucune** requête `script.js` /
  `api/event` ne doit partir (visites non comptées).
- Le tableau de bord Plausible affiche les visites sous **« Top Pages »**.

## Exploitation

- **Visiteurs par page** : tableau de bord → encadré **« Top Pages »**
  (visiteurs uniques + pages vues), bouton **Details** pour la liste complète
  et l'export CSV.
- **Sauvegardes** : les données vivent dans les volumes nommés
  `plausible_db_data` (PostgreSQL) et `plausible_event_data` (ClickHouse).
- **Mises à jour** : modifier le tag d'image dans `docker-compose.analytics.yml`
  (`ghcr.io/plausible/community-edition:vX.Y.Z`) puis `up -d`.

## Ressources

- Note pour petits VPS : la config ClickHouse `docker/plausible/clickhouse/`
  (issue de l'upstream) limite l'usage mémoire (`low-resources.xml`).
- Référence upstream : https://github.com/plausible/community-edition
