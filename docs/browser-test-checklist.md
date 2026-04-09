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
4. Vérifier que la page Contact s'affiche avec un titre

**Résultat attendu** : navigation fonctionnelle vers la page Contact.

### NAV-04 [PUBLIC] — Header visible sur toutes les pages
1. Ouvrir `${BASE_URL}/a-propos`
2. Vérifier la présence du header avec « Cultur'all » et les liens de navigation
3. Ouvrir `${BASE_URL}/contact`
4. Vérifier la présence du header avec « Cultur'all » et les liens de navigation

**Résultat attendu** : le header est présent et fonctionnel sur toutes les pages.

### NAV-05 [PUBLIC] — Navigation responsive
1. Ouvrir `${BASE_URL}/` en viewport mobile (375px)
2. Vérifier que le header reste visible et lisible
3. Vérifier que les liens de navigation sont accessibles

**Résultat attendu** : la landing page et la navigation sont utilisables sur mobile.

## 2. Authentification

### AUTH-01 [PUBLIC] — Connexion utilisateur valide
1. Ouvrir `${BASE_URL}/admin/login/`
2. Remplir email + mot de passe valides
3. Soumettre le formulaire
4. Vérifier la redirection vers la page authentifiée

**Résultat attendu** : utilisateur connecté, redirection correcte.

### AUTH-02 [AUTH] — Déconnexion
1. Cliquer sur le bouton de déconnexion
2. Vérifier la redirection vers l'accueil public

**Résultat attendu** : session terminée, accès aux pages [AUTH] redirigé vers la connexion.

## 3. Projets

### PROJ-01 [PUBLIC] — Ouverture de l'overlay Nos Projets
1. Ouvrir `${BASE_URL}/`
2. Cliquer sur le lien « Nos Projets » dans le header
3. Vérifier que l'overlay de projets apparaît avec une transition progressive
4. Vérifier que la page d'accueil en arrière-plan devient plus sombre
5. Vérifier que les projets s'affichent sous forme de cartes à bords arrondis

**Résultat attendu** : l'overlay s'ouvre avec une animation fluide, les cartes de projets sont visibles.

### PROJ-02 [PUBLIC] — Affichage des cartes de projets avec miniature
1. Ouvrir l'overlay Nos Projets (cliquer sur « Nos Projets » dans le header)
2. Vérifier que chaque carte affiche une image miniature en fond
3. Vérifier que le titre et le type (tag) sont masqués par défaut (non visibles sur la carte au repos)
4. Vérifier que les cartes ont des bords arrondis et une taille augmentée

**Résultat attendu** : les cartes de projets affichent la miniature en fond, le titre et le tag sont masqués au repos.

### PROJ-03 [PUBLIC] — Ouverture d'un projet en vue détail
1. Ouvrir l'overlay Nos Projets
2. Cliquer sur une carte de projet
3. Vérifier que la carte s'agrandit en plein écran avec une transition progressive
4. Vérifier qu'à gauche s'affichent les informations textuelles (titre, description, tags)
5. Vérifier qu'à droite s'affiche la vidéo YouTube intégrée
6. Vérifier la présence du lien « Retour aux projets » en haut

**Résultat attendu** : la vue détail s'ouvre en plein écran avec les informations et la vidéo.

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

### PROJ-06 [AUTH] — Ajout d'un projet avec miniature via l'admin Wagtail
1. Se connecter à `${BASE_URL}/admin/`
2. Naviguer vers la section Snippets > Projets
3. Cliquer sur « Ajouter »
4. Remplir titre, description, tags (ex: « Clip »), lien YouTube
5. Ajouter une miniature via le sélecteur d'images Wagtail
6. Sauvegarder
7. Vérifier que le projet apparaît dans la liste admin
8. Ouvrir l'overlay Nos Projets côté public
9. Vérifier que le nouveau projet apparaît avec sa miniature en fond de carte

**Résultat attendu** : le projet est créé via l'admin avec miniature et visible côté public avec l'image en fond de carte.

### PROJ-07 [PUBLIC] — Effet hover sur les cartes de projets
1. Ouvrir l'overlay Nos Projets (cliquer sur « Nos Projets » dans le header)
2. Passer la souris sur une carte de projet
3. Vérifier que l'image de fond se floute (effet blur)
4. Vérifier que l'image de fond s'assombrit
5. Vérifier que le titre et le type (tag) du projet apparaissent au centre de la carte

**Résultat attendu** : au survol, l'image se floute et s'assombrit, le titre et le tag apparaissent avec une transition fluide.

## 4. Parcours principal

### E2E-01 [AUTH] — Parcours end-to-end principal
1. Se connecter à l'admin Wagtail
2. Créer un nouveau projet via Snippets > Projets
3. Ouvrir l'overlay Nos Projets côté public
4. Vérifier la présence du projet créé
5. Cliquer sur le projet pour voir la vue détail
6. Vérifier les informations et la vidéo

**Résultat attendu** : parcours complet de création et consultation d'un projet sans erreur.
