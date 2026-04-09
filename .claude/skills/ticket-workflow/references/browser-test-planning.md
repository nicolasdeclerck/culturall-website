# Planification des tests browser (TDD)

Ce fichier est appelé par la Phase 2 (plan technique) pour gérer la mise à jour
du cahier de tests et la définition des scénarios spécifiques au ticket.

---

## Mise à jour du cahier de tests browser

Avant de démarrer le développement, mets à jour le cahier de tests de non-régression
`docs/browser-test-checklist.md` pour refléter les fonctionnalités à implémenter.

**Principe TDD :** les tests attendus sont écrits **avant** le code, ce qui garantit
que le cahier est toujours synchronisé avec les fonctionnalités de l'application.

**Démarche :**

1. Lis le fichier `docs/browser-test-checklist.md` existant
2. Analyse les tâches du plan pour identifier les impacts sur les tests browser :
   - Nouvelle fonctionnalité utilisateur → **ajouter** de nouveaux scénarios de test
   - Modification d'un flux existant → **mettre à jour** les scénarios concernés
   - Suppression d'une fonctionnalité → **retirer** les scénarios obsolètes
   - Nouvel endpoint API consommé par le front → **ajouter** les vérifications associées
   - Changement de comportement UI (formulaire, navigation, permissions) → **adapter** les vérifications
3. Applique les modifications en respectant les conventions du cahier :
   - Tags `[PUBLIC]`, `[AUTH]`, `[OWNER]` selon le niveau d'accès requis
   - Format : action à réaliser + résultat attendu
   - Placement dans la section thématique appropriée (ou création d'une nouvelle section si nécessaire)
   - Si la fonctionnalité implique un parcours complet, ajouter un scénario end-to-end
4. Commite la mise à jour du cahier **séparément** du code d'implémentation :

```bash
git add docs/browser-test-checklist.md
git diff --cached --quiet || git commit -m "test: update browser test checklist for #{ISSUE_NUMBER}"
```

**Si aucun changement front-end n'est identifié** (ex : refactoring backend pur,
modification de tâche asynchrone sans impact UI), cette étape est sautée.

---

## Définition de la liste de tests browser du ticket

Après la mise à jour du cahier de tests, définis la liste des scénarios de test
browser **spécifiques à ce ticket** qui seront exécutés à la demande via le
workflow `browser-tests.yml`.

**Démarche :**

1. Identifie tous les scénarios de `docs/browser-test-checklist.md` impactés par ce ticket :
   - Les scénarios **ajoutés** ci-dessus
   - Les scénarios **modifiés** ci-dessus
   - Les scénarios existants qui testent des fonctionnalités **touchées** par les changements
     (tests de non-régression directe)
2. Collecte pour chaque scénario : son identifiant (ex : `NAV-01`), son titre, son type
   (`[PUBLIC]`, `[AUTH]`, `[OWNER]`), et les étapes détaillées telles que décrites dans le cahier
3. Enregistre cette liste dans le fichier d'état `.claude-state.json` sous la clé `browser_tests` :

```json
{
  "browser_tests": [
    {
      "id": "NAV-01",
      "title": "Affichage du header",
      "type": "PUBLIC",
      "steps": "1. Ouvrir la page d'accueil\n2. Vérifier la présence du header..."
    },
    {
      "id": "E2E-02",
      "title": "Parcours end-to-end principal",
      "type": "AUTH",
      "steps": "1. Se connecter...\n2. Réaliser l'action principale..."
    }
  ]
}
```

4. Le nombre de scénarios est mentionné dans le commentaire court de Phase 2.

**Si aucun changement front-end n'est identifié**, la liste `browser_tests` est vide (`[]`)
et la Phase 4 marquera le ticket `approved` directement (sans `pending-browser-tests`).
