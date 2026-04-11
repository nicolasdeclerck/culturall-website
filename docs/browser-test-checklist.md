# Cahier de tests de non-régression — culturall-website

> Ce fichier est lu par les skills `browser-tests-on-demand` et
> `regression-tests`. Il contient les scénarios de tests browser à exécuter.
>
> **À écrire entièrement pour ton projet.** Le squelette ci-dessous montre
> les conventions attendues par les skills.

## Prérequis

- **URL de base** : `${BASE_URL}` (env var fournie au runtime par le workflow ou l'utilisateur)
- **Utilisateur de test 1** : `testuser@example.com` / `Testpass123!` — créé par `scripts/tnr-docker.sh`
- **Utilisateur de test 2** : `testuser2@example.com` / `Testpass123!` — créé par `scripts/tnr-docker.sh`

## Conventions

Chaque scénario porte un **identifiant stable** (ex : `NAV-01`, `1.1`, `E2E-02`),
un **type d'accès** entre crochets, un **titre**, une liste d'**étapes** et un
**résultat attendu**.

Types d'accès :
- `[PUBLIC]` : aucune authentification (session `public`)
- `[AUTH]`   : utilisateur 1 connecté (session `user1`)
- `[OWNER]`  : nécessite un second utilisateur ou des données dont l'utilisateur 1 est propriétaire (sessions `user1` + `user2`)

## 1. Navigation et layout

### NAV-01 [PUBLIC] — Affichage de la landing page avec vidéo plein écran
1. Ouvrir `${BASE_URL}/`
2. Vérifier la présence d'une vidéo en arrière-plan occupant tout l'écran
3. Vérifier que la vidéo est en lecture automatique et sans son (muted)
4. Vérifier la présence du header avec le titre « Cultur'all » à gauche
5. Vérifier la présence du menu de navigation à droite avec les liens « À propos » et « Contact »

**Résultat attendu** : la landing page s'affiche avec la vidéo plein écran en fond, le header est visible par-dessus la vidéo.

### NAV-02 [PUBLIC] — Navigation vers la page À propos
1. Ouvrir `${BASE_URL}/`
2. Cliquer sur le lien « À propos » dans le header
3. Vérifier que l'URL est `${BASE_URL}/a-propos`
4. Vérifier que la page À propos s'affiche avec un titre

**Résultat attendu** : navigation fonctionnelle vers la page À propos.

### NAV-03 [PUBLIC] — Navigation vers la page Contact
1. Ouvrir `${BASE_URL}/`
2. Cliquer sur le lien « Contact » dans le header
3. Vérifier que l'URL est `${BASE_URL}/contact`
4. Vérifier que la page Contact s'affiche avec un titre et un formulaire de contact

**Résultat attendu** : navigation fonctionnelle vers la page Contact avec formulaire visible.

### NAV-04 [PUBLIC] — Header visible sur toutes les pages
1. Ouvrir `${BASE_URL}/a-propos`
2. Vérifier la présence du header avec « Cultur'all » et les liens de navigation
3. Ouvrir `${BASE_URL}/contact`
4. Vérifier la présence du header avec « Cultur'all » et les liens de navigation

**Résultat attendu** : le header est présent et fonctionnel sur toutes les pages.

### NAV-05 [PUBLIC] — Menu hamburger sur mobile
1. Ouvrir `${BASE_URL}/` en viewport mobile (375px de large)
2. Vérifier que le titre « Cultur'all » est positionné en haut à gauche de l'écran
3. Vérifier que les liens de navigation ne sont **pas** visibles (masqués par défaut)
4. Vérifier la présence d'un bouton hamburger (☰) en haut à droite
5. Cliquer sur le bouton hamburger
6. Vérifier que le menu s'ouvre en plein écran avec les entrées : « Nos Projets », « Blog », « À propos », « Contact »
7. Cliquer sur « Nos Projets »
8. Vérifier que le menu se ferme et que la navigation vers `${BASE_URL}/projets` fonctionne
9. Revenir sur `${BASE_URL}/` et rouvrir le menu hamburger
10. Cliquer sur « À propos »
11. Vérifier que le menu se ferme et que la navigation vers `${BASE_URL}/a-propos` fonctionne
12. Revenir sur `${BASE_URL}/` et rouvrir le menu hamburger
13. Cliquer sur « Contact »
14. Vérifier que le menu se ferme et que la navigation vers `${BASE_URL}/contact` fonctionne

**Résultat attendu** : sur mobile, le menu est masqué derrière un bouton hamburger, il s'ouvre en plein écran et se referme après navigation vers les pages correspondantes.

### NAV-06 [PUBLIC] — Fermeture du menu hamburger par le bouton croix
1. Ouvrir `${BASE_URL}/` en viewport mobile (375px de large)
2. Cliquer sur le bouton hamburger
3. Vérifier que le menu plein écran s'affiche
4. Cliquer sur le bouton de fermeture (✕)
5. Vérifier que le menu se referme
6. Vérifier que la page d'accueil est toujours visible normalement

**Résultat attendu** : le menu hamburger peut être fermé sans naviguer, retour à la page précédente.

### NAV-07 [PUBLIC] — Navigation vers la page Projets depuis le header
1. Ouvrir `${BASE_URL}/`
2. Cliquer sur le lien « Nos Projets » dans le header
3. Vérifier que l'URL est `${BASE_URL}/projets`
4. Vérifier que la page Projets s'affiche avec un titre et une grille de projets

**Résultat attendu** : navigation fonctionnelle vers la page Projets (pas d'overlay).

### NAV-08 [PUBLIC] — Navbar évolutive au scroll (fond progressif)
1. Ouvrir `${BASE_URL}/`
2. Vérifier que le header est visible avec un fond transparent (pas de background noir)
3. Scroller progressivement vers le bas (au-delà de 50px)
4. Vérifier que le header a maintenant un fond noir semi-opaque (rgba(0,0,0,0.85) ou similaire)
5. Vérifier que la transition est progressive (pas de changement brusque)
6. Scroller vers le haut jusqu'en position 0
7. Vérifier que le header redevient transparent

**Résultat attendu** : le header passe progressivement de transparent à noir semi-opaque au scroll, et redevient transparent en haut de page. Le contenu du menu reste lisible sur la zone réseau (fond blanc).

## 2. Formulaire de contact

### CONTACT-01 [PUBLIC] — Affichage du formulaire de contact
1. Ouvrir `${BASE_URL}/contact`
2. Vérifier la présence d'un formulaire avec les champs : Nom, Email, Sujet, Message
3. Vérifier la présence d'un bouton d'envoi
4. Vérifier que les champs sont vides par défaut

**Résultat attendu** : le formulaire de contact s'affiche avec tous les champs attendus.

### CONTACT-02 [PUBLIC] — Soumission du formulaire avec succès
1. Ouvrir `${BASE_URL}/contact`
2. Remplir le champ Nom avec « Test Utilisateur »
3. Remplir le champ Email avec « test@example.com »
4. Remplir le champ Sujet avec « Demande de test »
5. Remplir le champ Message avec « Ceci est un message de test. »
6. Cliquer sur le bouton d'envoi
7. Vérifier qu'un message de confirmation s'affiche (ex : « Votre message a bien été envoyé »)

**Résultat attendu** : le formulaire est soumis, un message de succès s'affiche, les champs sont réinitialisés.

### CONTACT-03 [PUBLIC] — Validation des champs obligatoires
1. Ouvrir `${BASE_URL}/contact`
2. Cliquer sur le bouton d'envoi sans remplir les champs
3. Vérifier qu'un message d'erreur s'affiche pour les champs requis

**Résultat attendu** : le formulaire n'est pas soumis, des messages d'erreur de validation sont visibles.

### CONTACT-04 [AUTH] — Visibilité des soumissions dans l'admin Django
1. Soumettre un formulaire de contact via `${BASE_URL}/contact` (cf. CONTACT-02)
2. Ouvrir `${BASE_URL}/django-admin/`
3. Se connecter avec les identifiants admin
4. Naviguer vers la section « Demandes de contact » (ou « Contact submissions »)
5. Vérifier que la soumission apparaît dans la liste avec les bonnes données

**Résultat attendu** : la soumission de contact est visible dans l'admin Django avec toutes les informations saisies.

## 3. Authentification et protection par mot de passe

### AUTH-01 [PUBLIC] — Redirection vers la page de login quand la protection est activée
1. S'assurer que le paramètre « Authentification requise » est activé dans l'admin Wagtail (Paramètres > Paramètres du site)
2. Ouvrir `${BASE_URL}/` dans un navigateur sans session
3. Vérifier la redirection automatique vers `${BASE_URL}/login`
4. Vérifier que la page de login s'affiche avec un formulaire (champs Nom d'utilisateur et Mot de passe)

**Résultat attendu** : l'utilisateur non connecté est redirigé vers `/login` avec un formulaire de connexion.

### AUTH-02 [PUBLIC] — Connexion avec identifiants valides
1. Ouvrir `${BASE_URL}/login`
2. Remplir le champ « Nom d'utilisateur » avec `testuser`
3. Remplir le champ « Mot de passe » avec `Testpass123!`
4. Cliquer sur le bouton « Se connecter »
5. Vérifier la redirection vers la page d'accueil `${BASE_URL}/`
6. Vérifier que la page d'accueil s'affiche normalement (vidéo, header)

**Résultat attendu** : connexion réussie, redirection vers l'accueil, contenu accessible.

### AUTH-03 [PUBLIC] — Connexion avec identifiants invalides
1. Ouvrir `${BASE_URL}/login`
2. Remplir le champ « Nom d'utilisateur » avec `wronguser`
3. Remplir le champ « Mot de passe » avec `wrongpass`
4. Cliquer sur le bouton « Se connecter »
5. Vérifier qu'un message d'erreur s'affiche (ex : « Identifiants invalides »)
6. Vérifier que l'utilisateur reste sur la page de login

**Résultat attendu** : message d'erreur affiché, pas de redirection.

### AUTH-04 [AUTH] — Déconnexion
1. Se connecter avec `testuser` / `Testpass123!`
2. Vérifier la présence d'un lien « Déconnexion » dans le header
3. Cliquer sur « Déconnexion »
4. Vérifier la redirection vers la page de login
5. Tenter d'ouvrir `${BASE_URL}/` directement
6. Vérifier la redirection vers `/login`

**Résultat attendu** : session terminée, l'utilisateur est redirigé vers le login.

### AUTH-05 [AUTH] — Navigation complète après connexion
1. Se connecter avec `testuser` / `Testpass123!`
2. Vérifier l'accès à `${BASE_URL}/`
3. Naviguer vers `${BASE_URL}/a-propos`
4. Naviguer vers `${BASE_URL}/contact`
5. Naviguer vers `${BASE_URL}/projets`
6. Vérifier que toutes les pages sont accessibles sans redirection vers le login

**Résultat attendu** : toutes les pages du site sont accessibles après connexion.

### AUTH-06 [AUTH] — Toggle de protection dans l'admin Wagtail
1. Se connecter à `${BASE_URL}/admin/` avec les identifiants admin
2. Naviguer vers Paramètres > Paramètres du site
3. Décocher « Authentification requise »
4. Sauvegarder
5. Ouvrir `${BASE_URL}/` dans un navigateur sans session (navigation privée)
6. Vérifier que la page d'accueil s'affiche sans redirection vers le login

**Résultat attendu** : quand la protection est désactivée, le site est accessible sans connexion.

## 4. Projets

### PROJ-01 [PUBLIC] — Section Projets à la une sur la homepage
1. Ouvrir `${BASE_URL}/`
2. Scroller vers le bas après le carousel d'articles
3. Vérifier que la section « Projets » apparaît avec un titre
4. Vérifier que 3 cartes de projets sont affichées horizontalement
5. Vérifier que les 3 cartes occupent toute la largeur disponible sans écart entre elles
6. Vérifier que chaque carte affiche la miniature du projet en fond
7. Vérifier que le titre du projet est affiché en surimpression sur la carte
8. Vérifier que le tag du projet est affiché sur la carte
9. Vérifier la présence d'un lien « Voir tous les projets » pointant vers `/projets`

**Résultat attendu** : la section Projets affiche 3 cartes pleine largeur sans écart, avec miniature, titre en surimpression et tag.

### PROJ-02 [PUBLIC] — Page Projets avec grille 3 colonnes
1. Ouvrir `${BASE_URL}/projets`
2. Vérifier que la page affiche un titre « Nos Projets »
3. Vérifier que les projets sont affichés en grille avec 3 projets par ligne en desktop
4. Vérifier que chaque carte affiche la miniature en fond, le titre en surimpression et le tag
5. Vérifier la présence de boutons de filtrage par tags au-dessus de la grille
6. Cliquer sur un tag spécifique
7. Vérifier que seuls les projets ayant ce tag sont affichés
8. Cliquer sur « Tous »
9. Vérifier que tous les projets sont de nouveau affichés

**Résultat attendu** : la page Projets affiche une grille 3 colonnes avec filtrage par tags fonctionnel.

### PROJ-03 [PUBLIC] — Clic sur un projet ouvre la vue détail
1. Ouvrir `${BASE_URL}/projets`
2. Cliquer sur une carte de projet
3. Vérifier que la vue détail s'ouvre avec les informations textuelles (titre, description en texte riche, tags)
4. Vérifier que la vidéo YouTube intégrée est affichée
5. Vérifier la présence du lien « Retour aux projets »
6. Cliquer sur « Retour aux projets »
7. Vérifier le retour à la grille de projets

**Résultat attendu** : la vue détail s'ouvre avec les informations et la vidéo, retour fonctionnel à la grille.

### PROJ-04 [AUTH] — Champ « À la une » dans l'admin Wagtail
1. Se connecter à `${BASE_URL}/admin/`
2. Naviguer vers la section Snippets > Projets
3. Éditer un projet existant
4. Vérifier la présence d'une case à cocher « À la une »
5. Cocher « À la une » et sauvegarder
6. Vérifier que le projet est marqué comme « À la une »

**Résultat attendu** : le champ « À la une » est disponible et fonctionnel dans l'admin.

### PROJ-05 [AUTH] — Validation max 3 projets « À la une »
1. Se connecter à `${BASE_URL}/admin/`
2. Naviguer vers la section Snippets > Projets
3. S'assurer que 3 projets sont déjà cochés « À la une »
4. Éditer un 4ème projet et cocher « À la une »
5. Tenter de sauvegarder
6. Vérifier qu'un message d'erreur clair s'affiche indiquant qu'il ne peut y avoir plus de 3 projets à la une

**Résultat attendu** : la sauvegarde est refusée avec un message d'erreur clair sur la limite de 3 projets à la une.

### PROJ-06 [PUBLIC] — Responsive de la section Projets homepage sur mobile
1. Ouvrir `${BASE_URL}/` en viewport mobile (375px de large)
2. Scroller jusqu'à la section Projets
3. Vérifier que les cartes s'adaptent au viewport mobile (pas de changement de disposition demandé)

**Résultat attendu** : la section Projets est visible et utilisable sur mobile.

### PROJ-07 [PUBLIC] — Responsive de la page Projets sur mobile
1. Ouvrir `${BASE_URL}/projets` en viewport mobile (375px de large)
2. Vérifier que la grille s'adapte au mobile (pas de changement de disposition demandé)
3. Vérifier que les boutons de filtrage par tags sont utilisables

**Résultat attendu** : la page Projets est utilisable et lisible sur mobile.

## 5. Parcours principal

### E2E-01 [AUTH] — Parcours end-to-end projets
1. Se connecter à l'admin Wagtail
2. Créer un nouveau projet via Snippets > Projets avec « À la une » coché
3. Ouvrir `${BASE_URL}/` côté public
4. Scroller jusqu'à la section Projets et vérifier la présence du projet créé parmi les 3 à la une
5. Cliquer sur « Voir tous les projets »
6. Vérifier la navigation vers `${BASE_URL}/projets`
7. Vérifier la présence du projet créé dans la grille
8. Cliquer sur le projet pour voir la vue détail
9. Vérifier les informations et la vidéo

**Résultat attendu** : parcours complet de création et consultation d'un projet via la homepage et la page projets sans erreur.

## 6. Section Réseau

### NET-01 [PUBLIC] — Affichage de la section Réseau sur la landing page
1. Ouvrir `${BASE_URL}/`
2. Scroller vers le bas depuis la vidéo de fond
3. Vérifier que la section Réseau apparaît en scrollant par-dessus la vidéo
4. Vérifier que la vidéo reste fixe en arrière-plan pendant le scroll
5. Vérifier que la section Réseau a un fond blanc
6. Vérifier que les logos des membres du réseau s'affichent en entier (pas de troncature, même pour les logos non carrés)

**Résultat attendu** : la section Réseau s'affiche au scroll sur fond blanc, la vidéo reste fixe derrière, les logos des membres sont visibles en entier sans troncature.

### NET-02 [PUBLIC] — Filtrage des membres du réseau par type
1. Ouvrir `${BASE_URL}/`
2. Scroller jusqu'à la section Réseau
3. Vérifier la présence de boutons de filtrage par type au-dessus de la grille de logos
4. Vérifier qu'un bouton « Tous » est actif par défaut
5. Cliquer sur un type spécifique
6. Vérifier que seuls les logos des membres de ce type sont affichés
7. Cliquer sur « Tous »
8. Vérifier que tous les logos sont de nouveau affichés

**Résultat attendu** : le filtrage par type fonctionne dynamiquement, seuls les logos correspondants sont affichés.

### NET-03 [AUTH] — Ajout d'un membre du réseau via l'admin Wagtail
1. Se connecter à `${BASE_URL}/admin/`
2. Naviguer vers la section Snippets > Membres du réseau
3. Cliquer sur « Ajouter »
4. Remplir le nom, sélectionner un type, ajouter un logo via le sélecteur d'images Wagtail
5. Sauvegarder
6. Vérifier que le membre apparaît dans la liste admin
7. Ouvrir `${BASE_URL}/` côté public et scroller jusqu'à la section Réseau
8. Vérifier que le logo du nouveau membre est visible

**Résultat attendu** : le membre est créé via l'admin avec son logo, et il est visible dans la section Réseau côté public.

### NET-04 [PUBLIC] — Responsive de la section Réseau sur mobile
1. Ouvrir `${BASE_URL}/` en viewport mobile (375px de large)
2. Scroller jusqu'à la section Réseau
3. Vérifier que les logos s'affichent en grille adaptée au mobile
4. Vérifier que les boutons de filtrage par type sont utilisables

**Résultat attendu** : la section Réseau est utilisable et lisible sur mobile.

### E2E-02 [AUTH] — Parcours end-to-end création et consultation d'un membre du réseau
1. Se connecter à l'admin Wagtail
2. Créer un nouveau membre du réseau via Snippets > Membres du réseau (nom, logo, type)
3. Ouvrir `${BASE_URL}/` côté public
4. Scroller jusqu'à la section Réseau
5. Vérifier la présence du logo du membre créé
6. Filtrer par le type du membre créé
7. Vérifier que le logo est toujours visible après filtrage

**Résultat attendu** : parcours complet de création et consultation d'un membre du réseau sans erreur.

## 7. Blog — Carousel et articles

### BLOG-01 [PUBLIC] — Affichage du carousel d'articles sur la homepage
1. Ouvrir `${BASE_URL}/`
2. Scroller vers le bas après la vidéo de fond
3. Vérifier que le carousel d'articles apparaît entre la section vidéo et la section réseau
4. Vérifier que chaque slide affiche l'illustration de l'article et le titre en dessous
5. Vérifier la présence de flèches de navigation gauche/droite
6. Cliquer sur la flèche droite et vérifier que le carousel défile horizontalement
7. Vérifier la présence du lien « Voir tous les articles » sous le carousel

**Résultat attendu** : le carousel affiche les derniers articles avec illustrations et titres, navigation par flèches fonctionnelle.

### BLOG-02 [PUBLIC] — Ouverture de l'overlay article depuis le carousel
1. Ouvrir `${BASE_URL}/`
2. Scroller jusqu'au carousel d'articles
3. Cliquer sur un article du carousel
4. Vérifier que l'overlay s'ouvre en plein écran avec une transition progressive
5. Vérifier que l'overlay affiche l'illustration, le titre, le résumé et le contenu complet de l'article
6. Vérifier que le contenu riche est correctement rendu (gras, italique, listes, liens)
7. Fermer l'overlay (bouton fermer ou touche Escape)
8. Vérifier que la page d'accueil est de nouveau visible

**Résultat attendu** : l'overlay affiche le contenu complet de l'article et se ferme proprement.

### BLOG-03 [PUBLIC] — Navigation vers la page Blog
1. Ouvrir `${BASE_URL}/`
2. Vérifier la présence du lien « Blog » dans le header de navigation
3. Cliquer sur « Blog »
4. Vérifier que l'URL est `${BASE_URL}/blog`
5. Vérifier que la page Blog s'affiche avec un titre et une grille d'articles

**Résultat attendu** : navigation fonctionnelle vers la page Blog.

### BLOG-04 [PUBLIC] — Affichage de la grille masonry sur la page Blog
1. Ouvrir `${BASE_URL}/blog`
2. Vérifier que les articles sont affichés en grille de type masonry (colonnes CSS)
3. Vérifier que chaque carte affiche l'illustration de l'article
4. Vérifier que chaque carte affiche les 500 premiers caractères du contenu sous l'illustration
5. Vérifier que les cartes ont des hauteurs variables (layout masonry)

**Résultat attendu** : la grille masonry affiche les articles avec illustrations et extraits de contenu.

### BLOG-05 [PUBLIC] — Filtrage par tags sur la page Blog
1. Ouvrir `${BASE_URL}/blog`
2. Vérifier la présence de boutons de filtrage par tags au-dessus de la grille
3. Vérifier qu'un bouton « Tous » est actif par défaut
4. Cliquer sur un tag spécifique
5. Vérifier que seuls les articles ayant ce tag sont affichés
6. Cliquer sur « Tous »
7. Vérifier que tous les articles sont de nouveau affichés

**Résultat attendu** : le filtrage par tags fonctionne dynamiquement sur la page Blog.

### BLOG-06 [PUBLIC] — Ouverture de l'overlay article depuis la page Blog
1. Ouvrir `${BASE_URL}/blog`
2. Cliquer sur une carte d'article
3. Vérifier que l'overlay s'ouvre en plein écran avec le contenu complet
4. Vérifier que l'illustration, le titre, le résumé et le contenu sont affichés
5. Fermer l'overlay
6. Vérifier le retour à la page Blog avec la grille visible

**Résultat attendu** : l'overlay article fonctionne depuis la page Blog comme depuis le carousel.

### BLOG-07 [PUBLIC] — Responsive du carousel sur mobile
1. Ouvrir `${BASE_URL}/` en viewport mobile (375px de large)
2. Scroller jusqu'au carousel d'articles
3. Vérifier que le carousel est utilisable en swipe horizontal
4. Vérifier que les articles sont lisibles sur mobile

**Résultat attendu** : le carousel d'articles est fonctionnel et lisible sur mobile.

### BLOG-08 [PUBLIC] — Responsive de la page Blog sur mobile
1. Ouvrir `${BASE_URL}/blog` en viewport mobile (375px de large)
2. Vérifier que la grille s'adapte en une seule colonne
3. Vérifier que les boutons de filtrage par tags sont utilisables
4. Cliquer sur une carte et vérifier l'ouverture de l'overlay

**Résultat attendu** : la page Blog est utilisable et lisible sur mobile.

### E2E-03 [AUTH] — Parcours end-to-end création et consultation d'un article
1. Se connecter à `${BASE_URL}/admin/`
2. Naviguer vers la section Snippets > Articles
3. Créer un nouvel article avec titre, résumé, contenu riche, illustration et tags
4. Publier l'article (statut Live)
5. Ouvrir `${BASE_URL}/` côté public
6. Scroller jusqu'au carousel et vérifier la présence de l'article créé
7. Cliquer sur l'article dans le carousel et vérifier l'overlay
8. Naviguer vers `${BASE_URL}/blog`
9. Vérifier que l'article apparaît dans la grille
10. Filtrer par le tag de l'article créé et vérifier qu'il reste visible

**Résultat attendu** : parcours complet de création et consultation d'un article sans erreur.
