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

### NAV-05 [PUBLIC] — Navigation responsive
1. Ouvrir `${BASE_URL}/` en viewport mobile (375px)
2. Vérifier que le header reste visible et lisible
3. Vérifier que les liens de navigation sont accessibles

**Résultat attendu** : la landing page et la navigation sont utilisables sur mobile.

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

## 3. Authentification

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

## 4. Parcours principal

### E2E-01 [AUTH] — Parcours end-to-end principal
1. Se connecter
2. Réaliser l'action principale du produit
3. Vérifier la création/modification effective

**Résultat attendu** : parcours complet sans erreur.

---

> Remplace ces sections par les scénarios spécifiques à ton produit.
> Garde la structure (`## section`, `### ID [TYPE] — titre`, étapes numérotées,
> ligne `**Résultat attendu**`) pour que les skills puissent parser le fichier.
