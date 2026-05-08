# Étude comparative : Django + React vs Django + HTMX

Document d'analyse rédigé pour évaluer si le stack actuel (Django/Wagtail headless + Next.js/React) est le plus pertinent pour `culturall-website`, ou si un retour à du rendu serveur Django + HTMX serait plus simple à maintenir.

> **TL;DR** — Le site est aujourd'hui un usage typique pour lequel HTMX a été pensé : un CMS Wagtail qui sert principalement du contenu éditorial, sans interactivité client riche, sans temps réel, sans état partagé complexe. La couche Next.js fait essentiellement de la traduction JSON → HTML, ce qui est précisément le rôle natif des templates Django/Wagtail. Une migration vers Django + HTMX réduirait significativement la surface de maintenance, **à condition** d'accepter un coût de réécriture initial et de figer un certain nombre d'options d'évolution (app mobile partageant l'API, équipe spécialisée frontend, écosystème React).

---

## 1. Photographie du stack actuel

| Dimension | État |
|---|---|
| Backend | Django 5.2 + Wagtail 7.4 (headless), PostgreSQL 16, MinIO (S3) |
| API | ~13 endpoints JSON, vues Django pures (pas de DRF, pas de GraphQL) |
| Auth | Sessions Django, pas de 2FA / OAuth / reset password |
| Frontend | Next.js 14 (App Router, SSR), React 18, TypeScript |
| State management | Aucun (`useState` local uniquement) |
| UI / styles | CSS vanilla (1 176 lignes dans `globals.css`) |
| Form library | Aucune (validation HTML native + `useState`) |
| Data fetching | `fetch()` brut |
| i18n | Aucune (français uniquement) |
| Temps réel | Aucun (pas de WS, pas de SSE, pas de polling) |
| Tâches asynchrones | Aucune (ni Celery, ni Channels) |
| Tests frontend | **Aucun** (ni Jest, ni Vitest, ni Playwright) |
| Tests backend | pytest, ~18 modules de tests |
| LOC backend Python | ~3 900 |
| LOC frontend TS/TSX | ~1 280 (dont ~600 de composants réels) |
| LOC CSS | 1 176 |
| Conteneurs prod | django + nextjs + postgres + minio |

Sources : `backend/`, `frontend/app/`, `docker-compose.prod.yml`, `.github/workflows/`.

## 2. Ce que la couche React fait réellement

En parcourant `frontend/app/`, les seuls comportements qui ne sont pas de la simple mise en page de contenu Wagtail sont :

- **Filtrage par tag** côté client sur la liste blog (`app/blog/page.tsx`) — recalcul d'un `Array.from(new Set(...))` à chaque sélection.
- **Soumission du formulaire de contact** avec gestion d'état d'erreur et de soumission (`app/contact/ContactForm.tsx`, 140 lignes).
- **Header sticky** dont le style change au scroll, plus un menu mobile avec verrouillage du scroll body et fermeture sur Escape (`app/components/Header.tsx`, 110 lignes).
- **Middleware d'authentification** qui appelle `/api/auth/check/` à chaque requête pour rediriger vers `/login` si `require_authentication=true` (`middleware.ts`, 49 lignes).
- **Preview Wagtail headless** via tokens signés (`app/preview/route.ts`).

Tout le reste est de la consommation d'API JSON pour afficher des champs Wagtail (titre, image, rich text). Côté Wagtail ce sont des `Page` standards déjà conçues pour être rendues via templates.

## 3. Coût de la complexité actuelle

Le stack headless impose plusieurs coûts qui ne sont pas justifiés par les bénéfices habituels du headless (réutilisation par une app mobile, équipe frontend dédiée, interactivité riche) :

1. **Deux runtimes en production** : un service Node.js standalone Next.js + Gunicorn Django. Deux process à monitorer, deux pipelines de build d'image, deux cycles de mise à jour (Next 14 → 15, Node LTS, etc.).
2. **Une couche de sérialisation manuelle** : chaque vue Django convertit un objet Wagtail en `dict` JSON. Tout nouveau champ exige une modification synchrone backend + types TS frontend, sans aucun typage end-to-end (pas d'OpenAPI, pas de tRPC).
3. **Un système de preview ré-implémenté** : Wagtail offre la preview en natif. La version headless oblige à passer par `wagtail-headless-preview`, des tokens signés et un endpoint `/preview` côté Next, pour reproduire ce qui marche par défaut en mode templates.
4. **CORS, double routage, double 404** : nginx/Traefik route `/api`, `/admin`, `/static` vers Django et le reste vers Next.js. Cela complique la config locale comme prod.
5. **Aucun test frontend** : 1 280 lignes de TS sans filet de sécurité automatisé. C'est un risque de régression à chaque montée de version.
6. **Image optimization Next** : utile, mais Wagtail fournit déjà des renditions (`fill-600x400`, `max-200x200`) — la fonctionnalité est dupliquée.
7. **Polyglottisme** : Python côté serveur, TypeScript côté client, deux écosystèmes de dépendances (pip + npm), deux Dockerfiles, deux logiques de migration de version.

## 4. Ce qu'apporterait Django + HTMX

### 4.1 Mapping concret des fonctionnalités existantes

| Fonctionnalité actuelle (Next.js) | Équivalent Django + HTMX |
|---|---|
| Pages SSR (`/`, `/blog`, `/projets`, …) | Templates Django/Wagtail rendus par les `Page` correspondantes — déjà supporté nativement |
| Filtrage par tag blog | `<a hx-get="/blog/?tag=foo" hx-target="#article-list" hx-push-url="true">` |
| Formulaire de contact | `<form hx-post="/contact/" hx-target="#form-container">` qui swap avec un partial `_success.html` ou `_errors.html` |
| Header scroll-aware + menu mobile | Alpine.js (~10 KB) ou JS vanilla < 30 lignes |
| Auth middleware | `LoginRequiredMiddleware` Django + setting `require_authentication` déjà en place |
| Preview Wagtail | Preview Wagtail native (gratuite) |
| Image optimization | Renditions Wagtail + `loading="lazy"` natif HTML |
| `next/font` | `<link rel="preload">` ou `django-compressor` |
| Metadata API | Balises `<meta>` dans les templates de base, ou `django-meta` |

### 4.2 Ce qui disparaît du dépôt

- `frontend/` complet (~1 280 LOC TS + 1 176 LOC CSS, ou plutôt : le CSS reste, déplacé dans `static/`).
- `docker/nextjs/Dockerfile` et le service `nextjs` du compose.
- Le routage CORS et la duplication d'URL.
- `wagtail-headless-preview` et les routes `*/preview/`.
- Toutes les vues `views.py` qui font de la sérialisation JSON, remplacées par des templates ou supprimées si la `Page` Wagtail suffit.

### 4.3 Ce qu'il faut ajouter

- `django-htmx` (~5 KB) pour `request.htmx` et helpers.
- Optionnellement `alpinejs` pour les 2-3 interactions JS résiduelles (scroll header, menu mobile).
- Une suite de templates : `base.html`, `_header.html`, `_footer.html`, plus les templates spécifiques aux `Page` Wagtail (`blog/article_page.html`, `projects/project_page.html`, etc.).
- Tests d'intégration côté Django (Wagtail fournit `WagtailPageTests`).

## 5. Trade-offs honnêtes

### Arguments **pour** la migration HTMX

- **Surface de code drastiquement réduite** : on supprime un service entier, un langage, un écosystème de dépendances.
- **Une seule source de vérité** : le modèle Wagtail rend directement son template, plus de désynchronisation API ⇄ types.
- **Preview Wagtail native** : élimine une vraie source de bugs/complexité.
- **i18n future plus simple** : `gettext` Django + `django.utils.translation` est mature ; ré-implémenter ça côté Next.js demanderait `next-intl` ou équivalent.
- **Tests** : moins de surface non testée. Tester un template + une vue Wagtail est un pattern bien outillé.
- **Moins de CVE et de mises à jour** : pas de Node, pas de Next.js majeur tous les 9 mois, pas de churn TypeScript.

### Arguments **contre** la migration HTMX

- **Coût de réécriture** : ~1 semaine-développeur pour un site de cette taille. Pas gratuit.
- **Pas d'API JSON publique** : si demain une app mobile ou un partenaire doit consommer les contenus, il faudra reconstruire les endpoints (ou conserver une partie de l'API existante en parallèle).
- **Écosystème React abandonné** : pas de retour facile en arrière, et le marché des développeurs React reste plus large que celui des développeurs Django/HTMX.
- **Interactions très riches** : si la roadmap inclut un éditeur drag-and-drop, des graphiques interactifs, ou un dashboard temps réel, React reste mieux armé. *(D'après le README et `docs/`, ce n'est pas le cas aujourd'hui.)*
- **Image optimization perdue** : Next.js `<Image>` fait du lazy loading + responsive automatique. Reproduire ça avec Wagtail demande un peu de travail (mais reste faisable avec `picture` + `srcset`).
- **Préférence d'équipe** : si l'équipe est plus à l'aise en React qu'en templates Django, le bénéfice de maintenance n'est pas garanti.

## 6. Recommandation

Sur la base **de l'application actuelle uniquement** — pas d'une roadmap qui n'est pas documentée — le stack Django + React est **sur-dimensionné**. Les indicateurs concrets :

- Le frontend sert essentiellement à afficher du contenu Wagtail.
- Aucun test frontend n'a été écrit (ce qui suggère que l'investissement dans la couche React n'est pas pleinement rentabilisé).
- Aucune des fonctionnalités qui justifient habituellement React (state global, optimistic UI, real-time, offline, interactions riches) n'est présente.
- Le headless ajoute une complexité opérationnelle réelle (deux services, sérialisation manuelle, preview ré-implémentée).

**Trois trajectoires possibles, du moins au plus engageant :**

1. **Statu quo + tests frontend.** Garder l'architecture actuelle et ajouter une suite Vitest + Playwright. Bon choix si une app mobile ou des features interactives sont prévues à 6-12 mois.
2. **Migration progressive vers Wagtail templates + HTMX.** Démarrer par les pages les plus statiques (`/a-propos`, `/mentions-legales`, `/contact`), puis migrer blog et projets. Conserver Next.js le temps de la transition. Permet de valider le pattern avant de s'engager.
3. **Réécriture complète Django + HTMX + Alpine.js.** Faisable en ~1 semaine pour un site de cette taille. Maximum de gains à terme, mais demande un sprint dédié.

Pour cette codebase précise, la trajectoire **(2) puis (3)** semble la plus rationnelle si l'objectif explicite est *"plus facile à maintenir"*. Si l'objectif est *"évoluer vers une plateforme plus riche"*, alors **(1)** reste défendable et il faut investir dans des tests frontend plutôt que dans un changement de stack.

## 7. Si la migration est retenue : checklist de découpage

1. Activer `wagtail.contrib.routable_page` ou rendu standard et créer `templates/base.html` (header, footer, slot principal).
2. Ajouter `django-htmx` aux dépendances et le middleware associé.
3. Migrer les pages statiques (`StaticContentPage`) vers un template `pages/static_content_page.html` — supprimer la vue `pages/views.py`.
4. Réimplémenter le formulaire de contact en `FormView` Django + partial HTMX (`_contact_form.html`, `_contact_success.html`).
5. Migrer la liste blog avec filtre par tag : `BlogIndexPage.serve()` retourne soit la page complète, soit le partial `_article_list.html` selon `request.htmx`.
6. Migrer les projets de la même manière, plus la section "featured" sur la home.
7. Réintroduire le scroll-aware header + menu mobile via Alpine.js (~30 lignes).
8. Supprimer `wagtail-headless-preview`, les routes `*/preview/`, le middleware Next, les vues JSON.
9. Retirer `frontend/`, le service `nextjs`, le Dockerfile correspondant, les workflows CI associés.
10. Mettre à jour `docker-compose.*.yml`, Traefik/nginx (un seul upstream `django:8000`), le README et le guide admin.

---

*Document généré le 2026-05-08 sur la branche `claude/compare-django-stacks-YQVrB`.*
