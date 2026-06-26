---
name: demo-video-wagtail
description: Enregistrer une démo vidéo du site Cultur'all (front public ou administration Wagtail) avec Playwright — curseur animé, encarts de consignes et carte d'introduction. À utiliser dès que l'utilisateur demande de « faire une démo vidéo », « enregistrer une vidéo », « filmer un parcours », « montrer comment faire X dans l'admin », etc. Couvre l'installation de Playwright, la navigation dans l'arbre Wagtail, les pièges connus, et impose une étape d'amélioration continue du skill après chaque séance.
---

# Démos vidéo Cultur'all (Playwright)

Ce skill produit des **vidéos pédagogiques** d'un parcours sur le site Cultur'all en local
(`localhost:8000`) : front public **ou** administration **Wagtail**. Le rendu inclut un
**curseur animé** (Playwright ne filme pas le vrai curseur), des **encarts de consignes**
à chaque écran, et une **carte d'introduction** qui annonce le plan.

La sortie native de Playwright est un fichier **`.webm`**. Proposer une conversion MP4/GIF si demandé.

## Quand l'utiliser

Dès que l'utilisateur demande une démonstration filmée d'un parcours du site, p. ex. :
« fais-moi une vidéo qui montre comment… », « enregistre une démo de… », « filme la création
d'une page… ». Pas pour de simples captures d'écran statiques (utiliser un screenshot).

## Pré-requis (vérifier dans l'ordre)

1. **Serveur local en marche** : `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/`
   doit renvoyer `200`/`302`. Le projet tourne sous Docker (`docker compose`), conteneur
   Django = `culturall-website-django-1`.
2. **Node + Playwright** : Node ≥ 20 disponible. Installer le navigateur si besoin :
   `npx playwright install chromium`. Si le module `playwright` n'est pas résolvable depuis
   le dossier de travail, faire un `npm install playwright` local (p. ex. dans le scratchpad).
3. **Identifiants admin de dev** : `admin` / `admin` (identifiants **locaux jetables** — ne
   jamais traiter comme un secret ; ne pas les utiliser hors localhost).

## Construire une démo

1. **Écrire le script** dans le scratchpad de session (pas dans le repo), en important les
   helpers : `scripts/demo-helpers.mjs`. S'inspirer de l'exemple complet
   `scripts/example-creer-publier-projet.mjs` (connexion → arbre → création → publication).
2. **Récupérer les IDs de pages** nécessaires AVANT d'écrire la navigation, via le shell Django :
   ```
   docker exec culturall-website-django-1 python manage.py shell -c "
   from wagtail.models import Page
   for p in Page.objects.all().order_by('path'):
       print(p.id, '  '*p.depth, repr(p.title), p.slug)"
   ```
   (Arbre actuel : Root `1` → **Cultur'all** `3` → **Nos réalisations** `7` → projets.)
3. **Structurer le scénario** : carte d'intro (`d.intro(...)`) → une `d.caption(...)` formulée
   comme une **consigne d'action** à *chaque* écran → actions via `d.clickEl` / `d.typeInto`
   / `d.smoothScroll`.
4. **Lancer** : `node mon-script.mjs <dossier-sortie>`. Le script imprime `VIDEO_PATH=…`.
5. **Vérifier l'effet** (si l'action modifie des données) via le shell Django, puis **copier
   la vidéo** vers un emplacement visible (`~/Desktop/…webm`) avec un nom parlant.

## Consignes de réalisation (rendu)

- **Viewport 1366×850**, `recordVideo.size` identique.
- `await context.addInitScript(initScript)` **avant** `newContext().newPage()` — sinon les
  overlays n'apparaissent pas. Les overlays sont ré-injectés à chaque navigation : ré-appeler
  `caption` après chaque `goto`/`waitForLoadState`.
- **Curseur** : toujours déplacer le curseur via `d.clickEl`/`d.glide` (mouvement fluide,
  easing) ; ne jamais cliquer « en téléportant ». Après un `goto`, resynchroniser avec
  `d.syncCursor()`.
- **Encarts** : une carte d'intro de ~6 s au démarrage listant les étapes ; puis à chaque
  écran une consigne impérative (« Cliquez sur… », « Renseignez… », « Faites défiler… »).
  Badge d'étape (« Étape 1 », « Étape 2 »…).
- **Scroll** : utiliser `d.smoothScroll(px)` pour rendre le défilement **visible** quand un
  formulaire est long (ne pas sauter directement en bas).
- Laisser des **pauses** (`d.sleep(800–2000)`) pour la lisibilité ; saisir le texte avec un
  `delay` (~70–110 ms) pour un effet de frappe naturel.

## Navigation Wagtail — pièges connus (À RESPECTER)

> ⚠️ Ces points ont été identifiés en séance. Les ignorer fait échouer la vidéo.

- **`waitUntil: 'networkidle'` ne se stabilise jamais** (websockets/polling) → utiliser
  `waitUntil: 'load'` et des `waitForTimeout` explicites.
- **Module `playwright` non résolvable** depuis le repo → `npm install playwright` local dans
  le dossier d'exécution (scratchpad) avant de lancer.
- **Bouton « ajouter une page enfant » = icône sans texte** → le cibler par son `href` :
  `a[href="/admin/pages/<PARENT_ID>/add_subpage/"]` (et non par rôle/nom).
- **Entrer dans une page de l'explorateur** : le lien d'entrée (chevron) est
  `a[href="/admin/pages/<ID>/"]` (aria-label « Explorer les sous-pages de … »). Le titre de la
  page pointe lui vers `…/edit/` (édition), à ne pas confondre.
- **Bouton « Publier » caché dans le menu « Plus d'actions »** : `button[name="action-publish"]`
  n'est pas visible par défaut. D'abord cliquer le toggle
  `getByRole('button', { name: /Plus d'actions|More actions/i })`, attendre ~700 ms, puis
  cliquer `button[name="action-publish"]`. Le glissement du curseur ne ferme PAS le menu.
- **Collision de slug = échec silencieux de publication** : si une page (même brouillon) avec
  le même slug existe déjà sous le parent, la publication échoue en validation et **reste sur
  le formulaire d'ajout** sans message évident. ⇒ **Nettoyer les pages de test AVANT chaque
  relance** (voir Nettoyage) ou utiliser un titre unique.
- **Champs requis non remplis = échec silencieux** : un `ProjectPage` exige `title` **et**
  `youtube_url` (non `blank`). Toujours remplir tous les champs obligatoires avant de publier.
- **Vérifier le résultat en base**, ne pas se fier à l'URL seule : après publication réussie,
  l'URL repasse à `/admin/pages/<PARENT_ID>/`. Confirmer avec un `manage.py shell` :
  `live=True`, bon `get_parent()`.
- **Langue de l'admin = français** : les libellés visibles sont en FR (« Enregistrer le
  brouillon », « Publier », « Plus d'actions »). Préférer des sélecteurs robustes (`name=`,
  `href=`) aux textes quand c'est possible ; sinon prévoir une regex FR/EN.

## Nettoyage & ré-exécution

Avant **chaque** relance d'un script qui crée une page, supprimer la page de test précédente
pour éviter la collision de slug :
```
docker exec culturall-website-django-1 python manage.py shell -c "
from projects.models import ProjectPage
qs = ProjectPage.objects.filter(slug='<slug-de-demo>')
print('deleting', list(qs.values_list('id', flat=True))); qs.delete()"
```
Adapter le modèle/le slug selon la démo. Après une démo, **demander à l'utilisateur** s'il faut
conserver, dépublier ou supprimer la page créée.

## Amélioration continue (OBLIGATOIRE en fin de séance)

Ce skill doit s'enrichir à chaque utilisation. **À la fin de chaque réalisation de vidéo** :

1. Repenser aux frictions rencontrées (sélecteur introuvable, étape qui échoue, attente mal
   calibrée, piège Wagtail, comportement inattendu…).
2. Pour **chaque** difficulté réelle, **ajouter une consigne préventive** dans la section
   « Navigation Wagtail — pièges connus » ci-dessus (formulée comme une règle actionnable :
   symptôme → cause → quoi faire), et/ou corriger `scripts/demo-helpers.mjs`.
3. Consigner la date et un résumé d'une ligne dans le **journal** ci-dessous.
4. Si un nouveau parcours réutilisable a été créé, l'ajouter comme exemple dans `scripts/`.

Ne pas sauter cette étape même si la séance s'est bien passée (noter « RAS » le cas échéant).

### Journal des séances

- **2026-06-26** — Première version. Démo « créer + publier une page Projet sous Nos
  réalisations ». Pièges découverts et documentés : `networkidle` qui ne stabilise pas,
  bouton add-subpage en icône (cibler par `href`), bouton Publier dans « Plus d'actions »,
  collision de slug → échec silencieux de publication (nettoyer avant relance), champs requis
  (`youtube_url`) obligatoires, module `playwright` à installer en local.
