# Phase 3 — Développement

## 3.1 Récupération du plan et de la progression

Récupère la liste des tâches depuis le fichier d'état (clé `tasks`) et
`CURRENT_TASK` pour reprendre à la bonne tâche :

```bash
cat "$STATE_FILE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for t in d.get('tasks', []):
    status = '✅' if t['status'] == 'completed' else '⬜'
    print(f\"{status} [{t['index']}] {t['description']}\")
"
```

Si un commentaire `## 🔄 Corrections demandées` ou
`## 🔄 Corrections demandées (tests browser)` existe, récupère-le pour
connaître les corrections spécifiques à apporter — elles priment sur le
plan initial pour les fichiers concernés :

```bash
gh issue view {ISSUE_NUMBER} --json comments \
  --jq '[.comments[] | select(.body | startswith("## 🔄 Corrections demandées"))] | last | .body'
```

## 3.2 Exécution des tâches

Pour chaque tâche depuis `CURRENT_TASK` :

1. Implémente en suivant le plan et les corrections éventuelles
2. Respecte les conventions du `CLAUDE.md`
3. Met à jour la progression dans le fichier d'état :

```bash
CURRENT_TASK=$((CURRENT_TASK + 1))
write_state "3"
```

## 3.3 Tests

Stack : **Django/Wagtail (pytest)** + **Next.js (vitest/jest)**.
L'env de dev empile `base.yml` + `dev.yml` avec `--env-file .env.dev`.

```bash
COMPOSE="docker compose -p culturall-website \
  -f docker-compose.base.yml \
  -f docker-compose.dev.yml \
  --env-file .env.dev"

$COMPOSE up -d

# Tests backend (Django + Wagtail)
$COMPOSE exec -T django pytest

# Tests frontend (Next.js) — passe sans erreur si aucun script test
$COMPOSE exec -T nextjs npm test --if-present

$COMPOSE stop
```

En cas d'échec : corriger le code, relancer. Maximum **3 tentatives**.

Si toujours en échec après 3 tentatives :
```bash
gh issue comment {ISSUE_NUMBER} --body "## ❌ Échec des tests après 3 tentatives
[logs d'erreur]
Intervention humaine requise."
gh issue edit {ISSUE_NUMBER} --add-label 'help wanted'
```
→ **STOP** (l'humain reposera `analyze` après avoir corrigé)

## 3.4 Commit et push

```bash
git config --global user.email "claude-worker@example.com"
git config --global user.name "Claude Worker"

BRANCH_NAME="feat/issue-{ISSUE_NUMBER}-{slug-du-titre}"

if git -C /workspace/culturall-website ls-remote --exit-code --heads origin "$BRANCH_NAME" > /dev/null 2>&1; then
  echo "Branche existante, commit sur $BRANCH_NAME"
else
  git checkout -b "$BRANCH_NAME"
fi

git add -A
git diff --cached --quiet || git commit -m "feat: close #{ISSUE_NUMBER} - {titre}"
git push origin "$BRANCH_NAME"
```

## 3.5 Vérification de la documentation

Après chaque implémentation, vérifie si les fichiers de documentation du projet
nécessitent des mises à jour en fonction des changements réalisés :

- **`CLAUDE.md`** : stack technique, modèles Django/Wagtail, endpoints API DRF,
  composants Next.js, conventions, architecture
- **`README.md`** : fonctionnalités, stack, structure du projet
- **`INSTALL.md`** : nouvelles dépendances Python ou npm, variables d'environnement,
  étapes d'installation

Pour chaque fichier, compare le contenu actuel avec les changements apportés.
Si une mise à jour est nécessaire, applique-la directement (pas de commentaire GitHub).

Exemples de changements déclencheurs :
- Nouveau modèle Wagtail (`Page`, `Snippet`) → mettre à jour la section modèles de `CLAUDE.md`
- Nouvel endpoint DRF → mettre à jour la section API de `CLAUDE.md`
- Nouvelle dépendance Python → mettre à jour `backend/requirements.txt` et `INSTALL.md`
- Nouvelle dépendance npm → mettre à jour `frontend/package.json` et `INSTALL.md`
- Nouvelle variable d'environnement → mettre à jour `.env.example` et `INSTALL.md`
- Nouveau composant Next.js majeur → mettre à jour `README.md`

## 3.6 Commentaire de documentation

```bash
gh issue comment {ISSUE_NUMBER} --body "## 📝 Documentation

### Ce qui a été implémenté
[Résumé des fichiers créés/modifiés côté backend ET frontend]

### Choix techniques
[Décisions importantes et pourquoi]

### Comment utiliser
[Guide pratique : URLs, paramètres, comportement attendu]

### Points d'attention
[Limitations, prérequis, impacts sur la migration / le seed]"
```

## 3.7 Pull Request

```bash
EXISTING_PR=$(gh pr list --head "$BRANCH_NAME" --json number --jq '.[0].number' 2>/dev/null)

if [ -n "$EXISTING_PR" ]; then
  PR_NUMBER="$EXISTING_PR"
  gh pr edit "$PR_NUMBER" \
    --body "## Description

Closes #{ISSUE_NUMBER}

---

## Documentation

[contenu du commentaire de doc]"
  echo "PR #$PR_NUMBER mise à jour."
else
  PR_NUMBER=$(gh pr create \
    --title "feat: {titre du ticket}" \
    --body "## Description

Closes #{ISSUE_NUMBER}

---

## Documentation

[contenu du commentaire de doc]" \
    --base main \
    --head "$BRANCH_NAME" 2>&1 | grep -oP '/pull/\K[0-9]+')
  echo "PR #$PR_NUMBER créée."
fi
```

**Important :** `PR_NUMBER` doit être capturé ici pour être persisté par
`write_state()` à l'étape 3.8.

## 3.8 Transition vers Phase 4

```bash
N_DEV=$((N_DEV + 1))
write_state "4"
# → Exécuter Phase 4 directement
```
