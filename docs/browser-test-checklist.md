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

### NAV-01 [PUBLIC] — Affichage de la page d'accueil
1. Ouvrir `${BASE_URL}/`
2. Vérifier la présence du header
3. Vérifier la présence du footer

**Résultat attendu** : la page s'affiche sans erreur, header et footer visibles.

### NAV-03 [PUBLIC] — Affichage de la date du jour
1. Ouvrir `${BASE_URL}/`
2. Vérifier la présence d'un élément affichant la date du jour
3. Vérifier que la date correspond au jour courant (format français, ex : « mercredi 9 avril 2025 »)

**Résultat attendu** : la date du jour est affichée sur la page d'accueil au format français.

### NAV-02 [PUBLIC] — Navigation responsive
1. Ouvrir `${BASE_URL}/` en viewport mobile
2. Cliquer sur le menu burger
3. Vérifier que le menu s'ouvre

**Résultat attendu** : menu mobile fonctionnel.

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

## 3. Parcours principal

### E2E-01 [AUTH] — Parcours end-to-end principal
1. Se connecter
2. Réaliser l'action principale du produit
3. Vérifier la création/modification effective

**Résultat attendu** : parcours complet sans erreur.

---

> Remplace ces sections par les scénarios spécifiques à ton produit.
> Garde la structure (`## section`, `### ID [TYPE] — titre`, étapes numérotées,
> ligne `**Résultat attendu**`) pour que les skills puissent parser le fichier.
