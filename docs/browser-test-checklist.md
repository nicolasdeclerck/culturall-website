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
6. Vérifier que le menu s'ouvre en plein écran avec les 3 entrées : « Nos Projets », « À propos », « Contact »
7. Cliquer sur « À propos »
8. Vérifier que le menu se ferme et que la navigation vers `${BASE_URL}/a-propos` fonctionne
9. Revenir sur `${BASE_URL}/` et rouvrir le menu hamburger
10. Cliquer sur « Contact »
11. Vérifier que le menu se ferme et que la navigation vers `${BASE_URL}/contact` fonctionne

**Résultat attendu** : sur mobile, le menu est masqué derrière un bouton hamburger, il s'ouvre en plein écran et se referme après navigation.

### NAV-06 [PUBLIC] — Fermeture du menu hamburger par le bouton croix
1. Ouvrir `${BASE_URL}/` en viewport mobile (375px de large)
2. Cliquer sur le bouton hamburger
3. Vérifier que le menu plein écran s'affiche
4. Cliquer sur le bouton de fermeture (✕)
5. Vérifier que le menu se referme
6. Vérifier que la page d'accueil est toujours visible normalement

**Résultat attendu** : le menu hamburger peut être fermé sans naviguer, retour à la page précédente.

### NAV-07 [PUBLIC] — Ouverture de l'overlay Nos Projets depuis le menu hamburger mobile
1. Ouvrir `${BASE_URL}/` en viewport mobile (375px de large)
2. Cliquer sur le bouton hamburger
3. Cliquer sur « Nos Projets »
4. Vérifier que le menu hamburger se ferme
5. Vérifier que l'overlay des projets s'ouvre par-dessus la page d'accueil (comme avant)
6. Fermer l'overlay des projets
7. Vérifier que la page d'accueil est visible normalement

**Résultat attendu** : depuis le menu hamburger, « Nos Projets » ferme le menu et ouvre l'overlay projets normalement.

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
5. Ouvrir l'overlay « Nos Projets »
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

### PROJ-01 [PUBLIC] — Ouverture de l'overlay Nos Projets
1. Ouvrir `${BASE_URL}/`
2. Cliquer sur le lien « Nos Projets » dans le header
3. Vérifier que l'overlay de projets apparaît avec une transition progressive
4. Vérifier que la page d'accueil en arrière-plan devient plus sombre
5. Vérifier que les projets s'affichent sous forme de cartes à bords carrés sans bordure

**Résultat attendu** : l'overlay s'ouvre avec une animation fluide, les cartes de projets sont visibles avec des bords carrés.

### PROJ-02 [PUBLIC] — Affichage des cartes de projets avec miniature
1. Ouvrir l'overlay Nos Projets (cliquer sur « Nos Projets » dans le header)
2. Vérifier que chaque carte affiche une image miniature en fond
3. Vérifier que le titre et le type (tag) sont masqués par défaut sur desktop (non visibles sur la carte au repos)
4. Vérifier que les cartes ont des bords carrés, pas de bordure visible

**Résultat attendu** : les cartes de projets affichent la miniature en fond, le titre et le tag sont masqués au repos sur desktop, les cartes ont des bords carrés.

### PROJ-03 [PUBLIC] — Ouverture d'un projet en vue détail
1. Ouvrir l'overlay Nos Projets
2. Cliquer sur une carte de projet
3. Vérifier que la carte s'agrandit en plein écran avec une transition progressive
4. Vérifier qu'à gauche s'affichent les informations textuelles (titre, description en texte riche, tags)
5. Vérifier qu'à droite s'affiche la vidéo YouTube intégrée
6. Vérifier la présence du lien « Retour aux projets » en haut

**Résultat attendu** : la vue détail s'ouvre en plein écran avec les informations (description en texte riche formaté) et la vidéo.

### PROJ-11 [PUBLIC] — Rendu du texte riche dans la description d'un projet
1. Ouvrir l'overlay Nos Projets
2. Cliquer sur un projet dont la description contient du texte riche (gras, italique, liste à puces, lien)
3. Vérifier que le texte en gras s'affiche en **gras** (balise `<b>` ou `<strong>`)
4. Vérifier que le texte en italique s'affiche en *italique* (balise `<i>` ou `<em>`)
5. Vérifier que les listes à puces sont rendues sous forme de liste HTML (`<ul><li>`)
6. Vérifier que les liens sont cliquables et s'ouvrent dans un nouvel onglet

**Résultat attendu** : la description du projet affiche correctement le formatage riche (gras, italique, listes, liens).

### PROJ-04 [PUBLIC] — Retour depuis la vue détail vers la liste
1. Ouvrir un projet en vue détail
2. Cliquer sur « Retour aux projets »
3. Vérifier le retour à la liste des projets avec une transition progressive

**Résultat attendu** : retour fluide à la liste des projets.

### PROJ-05 [PUBLIC] — Fermeture de l'overlay projets
1. Ouvrir l'overlay Nos Projets
2. Fermer l'overlay (bouton fermer ou clic en dehors)
3. Vérifier que l'overlay se ferme avec une transition progressive
4. Vérifier que la page d'accueil retrouve sa luminosité normale

**Résultat attendu** : l'overlay se ferme proprement et la landing page revient à l'état normal.

### PROJ-06 [AUTH] — Ajout d'un projet avec miniature et description riche via l'admin Wagtail
1. Se connecter à `${BASE_URL}/admin/`
2. Naviguer vers la section Snippets > Projets
3. Cliquer sur « Ajouter »
4. Remplir titre, tags (ex: « Clip »), lien YouTube
5. Dans le champ description, vérifier la présence d'un éditeur de texte riche (barre d'outils avec gras, italique, listes, liens…)
6. Saisir du texte avec mise en forme : un mot en **gras**, un mot en *italique*, une liste à puces
7. Ajouter une miniature via le sélecteur d'images Wagtail
8. Sauvegarder
9. Vérifier que le projet apparaît dans la liste admin
10. Ouvrir l'overlay Nos Projets côté public
11. Vérifier que le nouveau projet apparaît avec sa miniature en fond de carte

**Résultat attendu** : le projet est créé via l'admin avec miniature, la description est saisie via un éditeur riche, et le projet est visible côté public avec l'image en fond de carte.

### PROJ-07 [PUBLIC] — Effet hover sur les cartes de projets
1. Ouvrir l'overlay Nos Projets (cliquer sur « Nos Projets » dans le header)
2. Passer la souris sur une carte de projet
3. Vérifier que l'image de fond se floute (effet blur)
4. Vérifier que l'image de fond s'assombrit
5. Vérifier que le titre et le type (tag) du projet apparaissent au centre de la carte

**Résultat attendu** : au survol, l'image se floute et s'assombrit, le titre et le tag apparaissent avec une transition fluide.

## 5. Parcours principal

### PROJ-08 [PUBLIC] — Filtrage des projets par tags
1. Ouvrir l'overlay Nos Projets (cliquer sur « Nos Projets » dans le header)
2. Vérifier que des boutons de filtrage par tags apparaissent au-dessus de la grille de projets
3. Vérifier qu'un bouton « Tous » est présent et actif par défaut
4. Cliquer sur un tag spécifique (ex : « Clip »)
5. Vérifier que seuls les projets ayant ce tag sont affichés
6. Cliquer sur « Tous »
7. Vérifier que tous les projets sont de nouveau affichés

**Résultat attendu** : le filtrage par tags fonctionne dynamiquement, les projets sont filtrés instantanément.

### PROJ-09 [PUBLIC] — Affichage mobile des cartes de projets
1. Ouvrir `${BASE_URL}/` en viewport mobile (375px de large)
2. Cliquer sur « Nos Projets » dans le header
3. Vérifier que les cartes ont une hauteur réduite par rapport au desktop
4. Vérifier que le titre et le tag sont visibles sans hover, alignés sur la gauche
5. Vérifier que la miniature est bien assombrie pour rendre le texte lisible

**Résultat attendu** : en mobile, les cartes sont compactes avec titre/tag visibles alignés à gauche sur fond assombri.

### PROJ-10 [PUBLIC] — Scroll dans l'overlay projets
1. Ouvrir l'overlay Nos Projets (s'assurer qu'il y a suffisamment de projets pour dépasser l'écran)
2. Vérifier que l'overlay est scrollable verticalement
3. Scroller vers le bas et vérifier que les projets supplémentaires sont visibles

**Résultat attendu** : l'overlay permet le défilement vertical quand le contenu dépasse la hauteur de l'écran.

### E2E-01 [AUTH] — Parcours end-to-end principal
1. Se connecter à l'admin Wagtail
2. Créer un nouveau projet via Snippets > Projets
3. Ouvrir l'overlay Nos Projets côté public
4. Vérifier la présence du projet créé
5. Cliquer sur le projet pour voir la vue détail
6. Vérifier les informations et la vidéo

**Résultat attendu** : parcours complet de création et consultation d'un projet sans erreur.

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
