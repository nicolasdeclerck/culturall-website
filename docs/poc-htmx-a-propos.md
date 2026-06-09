# POC : page À propos rendue côté serveur (Django + HTMX-ready)

Preuve de concept attachée à l'étude comparative
[`stack-comparison-django-react-vs-htmx.md`](./stack-comparison-django-react-vs-htmx.md).
Objectif : valider concrètement l'étape 3 du checklist de migration (« migrer
les pages statiques vers un template Django/Wagtail ») en l'appliquant à
`/a-propos/` sans casser le reste de l'application Next.js.

---

## TL;DR

| Métrique | Avant (Next.js) | Après (Django POC) |
|---|---|---|
| Code spécifique à la page | `app/a-propos/page.tsx` (22 lignes TS) + `components/StaticPageContent.tsx` (62 lignes TS) | `pages/templates/pages/static_content_page.html` (12 lignes) |
| Couche réseau | `fetch GET /api/pages/a-propos/` → JSON → `dangerouslySetInnerHTML` | Direct ORM → template, 0 hop réseau |
| Build / runtime | Next.js + Node.js | Django seul |
| Preview Wagtail | `wagtail-headless-preview` + endpoint `/api/preview/page/` + route `/preview` Next | Native Wagtail (gratuite, déjà installée) |
| Tests | 0 (aucun test frontend) | 6 tests pytest, 100 % passants |

Coût d'écriture du POC : ~30 minutes sur un site dont la stack n'avait
encore aucune ligne de template Django.

---

## Comment tester

### Lancer le backend en local

```bash
docker compose -p culturall-website \
  -f docker-compose.base.yml \
  -f docker-compose.dev.yml \
  --env-file .env.dev up django postgres minio
```

Puis ouvrir :

- **POC server-rendered :** http://localhost:8000/a-propos/
- **Version Next.js actuelle (pour comparer) :** http://localhost:3000/a-propos

Les deux doivent afficher le même contenu (titre + body Wagtail) avec la
même apparence visuelle (le CSS est partagé : copié depuis
`frontend/app/globals.css`).

### Lancer les tests

```bash
cd backend && pytest pages/tests/test_html_view.py -v
```

Six tests couvrent : rendu 200, body en HTML, présence du header/footer,
404 si dépubliée, méthode POST refusée, chargement des assets statiques.

---

## Ce qui a été ajouté

### Nouveaux fichiers

| Fichier | Rôle | LOC |
|---|---|---|
| `backend/templates/base.html` | Layout HTML5 (`<head>`, header, footer) | 19 |
| `backend/templates/_header.html` | Partial header avec logo Wagtail + nav + bouton menu | 31 |
| `backend/templates/_footer.html` | Partial footer (mentions légales + copyright) | 9 |
| `backend/pages/templates/pages/static_content_page.html` | Template Wagtail pour `StaticContentPage` | 12 |
| `backend/static/css/main.css` | CSS recopié 1:1 depuis `frontend/app/globals.css` | 1 176 |
| `backend/static/js/site.js` | Scroll-aware header + toggle menu mobile | 51 |
| `backend/pages/tests/test_html_view.py` | Tests pytest du POC | 56 |

**Total nouveau code applicatif (hors CSS recopié) : ~120 lignes** —
contre ~190 lignes TS supprimables côté frontend (`page.tsx` + `StaticPageContent.tsx`),
plus la simplification de `Header.tsx` (passage de 110 à ~0 lignes :
les responsabilités auth + logo + scroll deviennent du SSR + 30 lignes de JS).

### Fichiers modifiés

- `backend/config/settings/base.py` :
  - `TEMPLATES["DIRS"] = [BASE_DIR / "templates"]`
  - `STATICFILES_DIRS = [BASE_DIR / "static"]`
  - Ajout du context processor `wagtail.contrib.settings.context_processors.settings`
    pour exposer `SiteSettings.logo` au template.
- `backend/config/urls.py` : route `path("a-propos/", static_page_html, …)`.
- `backend/config/middleware.py` : ajout de `/a-propos/` aux préfixes exclus
  de `LoginRequiredMiddleware` (cohérent avec `/api/pages/` déjà exclu).
- `backend/pages/views.py` : ajout de la vue `static_page_html`
  (5 lignes : `get_object_or_404` + `render`).

---

## Ce qui disparaît si on bascule entièrement

À l'échelle du site complet (toutes pages migrées), on supprime :

- `frontend/app/a-propos/`, `frontend/app/mentions-legales/`, etc.
- `frontend/app/components/StaticPageContent.tsx`.
- `pages/views.py::static_page_detail` et `static_page_preview_draft`.
- Les routes `/api/pages/<slug>/` et `/api/preview/page/`.
- L'app `wagtail_headless_preview` (la preview Wagtail native suffit).
- La logique CORS spécifique à ces routes.

---

## Comparaison côte à côte du chemin de rendu

### Avant (Next.js headless)

```
Browser
  └─ GET /a-propos
     └─ Next.js Node server
        ├─ Render `app/a-propos/page.tsx`
        │   └─ <StaticPageContent slug="a-propos" />
        │       └─ async fetch GET http://django:8000/api/pages/a-propos/
        │           └─ Django view `static_page_detail`
        │              ├─ ORM: StaticContentPage.objects.live().get(slug=…)
        │              ├─ expand_db_html(page.body)
        │              └─ JsonResponse({slug, title, body})
        │       └─ dangerouslySetInnerHTML={{ __html: page.body }}
        └─ HTML rendu
```

5 sauts logiques, 2 process (Node + Python), 1 round-trip HTTP interne,
1 sérialisation JSON, 1 désérialisation TS.

### Après (POC Django)

```
Browser
  └─ GET /a-propos/
     └─ Django (Gunicorn)
        └─ View `static_page_html`
           ├─ ORM: StaticContentPage.objects.live().get(slug=…)
           └─ render("pages/static_content_page.html", {"page": page})
              └─ {{ page.body|richtext }}  (Wagtail expand_db_html appelé par le filter)
        └─ HTML rendu
```

2 sauts logiques, 1 process, 0 round-trip HTTP, 0 JSON.

---

## Limites connues du POC

1. **CSS dupliqué** : `backend/static/css/main.css` est une copie de
   `frontend/app/globals.css`. Lors d'une migration réelle, le CSS serait
   déplacé (pas dupliqué) et `frontend/` serait supprimé.
2. **`LoginRequiredMiddleware` renvoie toujours du JSON** sur les pages
   protégées : pour une migration complète, il faudrait le faire
   rediriger vers `/login` quand la requête attend du HTML
   (`request.accepts("text/html")`). Hors scope du POC.
3. **Logo Wagtail via storage MinIO** : le `{% image %}` tag de Wagtail
   fonctionne identiquement, mais l'URL générée pointe vers MinIO public
   comme actuellement. Pas de régression.
4. **Pas encore de HTMX** : la page À propos n'a aucune interactivité.
   `django-htmx` sera ajouté quand on migrera le formulaire de contact
   (étape 4 du checklist), où il apporte une vraie valeur (`hx-post`,
   swap d'un partial succès/erreurs).
5. **Pas d'image optimization automatique** : Next.js `<Image>` faisait
   du lazy + responsive. Wagtail fournit `{% image … fill-WxH %}` et
   `srcset` via `{% picture %}` ; à câbler sur les pages avec images
   (blog, projets), pas nécessaire ici.

---

## Suite logique

Si ce POC est validé, l'ordre de migration recommandé reste celui du
checklist de l'étude comparative :

1. **Mentions légales** (identique au POC, ~5 minutes).
2. **Page d'accueil** (`HomePage` + section featured projects).
3. **Liste blog + détail article** (introduction de `django-htmx` pour le
   filtre par tag : `hx-get="/blog/?tag=…"` swap sur `<article-list>`).
4. **Liste projets + détail projet**.
5. **Formulaire de contact** (`hx-post` + partial succès/erreurs).
6. **Auth flows** (login/logout en HTML standard, suppression du middleware
   Next).
7. **Suppression de `frontend/`, du service `nextjs`, de
   `wagtail-headless-preview` et des routes `/api/preview/*`.**

À l'arrivée : un seul service applicatif (Django), un seul langage côté
serveur, la preview Wagtail native, et l'intégralité du HTML servi par
Wagtail — ce pour quoi le CMS a été conçu.
