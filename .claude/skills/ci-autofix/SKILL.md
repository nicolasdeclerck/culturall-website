---
name: ci-autofix
description: Analyse automatique d'un echec CI backend-tests, creation d'une issue GitHub et d'une PR avec le fix.
allowed-tools: Bash(gh:*), Bash(git:*), Bash(cat:*), Bash(pytest:*), Bash(python3:*), Bash(pip:*), Read, Write, Glob, Edit
---

# Skill : ci-autofix

Analyse un echec CI (backend-tests), cree une issue GitHub, et ouvre une PR avec le fix.

## Inputs (fournis dans le prompt)

- `RUN_ID` : ID du workflow run echoue (variable d'env)
- `HEAD_SHA` : SHA du commit qui a echoue (variable d'env)
- `REPO` : owner/repo (variable d'env)
- Logs de l'echec CI (colles dans le prompt)

---

## Etape 1 — Analyser l'erreur

1. Lis les logs CI fournis dans le prompt
2. Lis aussi `/tmp/ci-failed-logs.txt` pour le detail complet
3. Identifie :
   - Quel(s) test(s) echoue(nt)
   - Le message d'erreur exact
   - Le(s) fichier(s) et ligne(s) concernes
   - La cause probable (regression, import manquant, dependance cassee, erreur de logique, etc.)

**IMPORTANT :** Si l'erreur concerne un probleme d'infrastructure (Docker, GHCR, runner) et non du code, arrete-toi ici et cree uniquement une issue (etape 2) sans tenter de fix.

---

## Etape 2 — Creer une issue GitHub

Cree une issue structuree avec `gh issue create`. Utilise le `REPO` passe en variable d'env.

```bash
ISSUE_URL=$(gh issue create \
  --repo "$REPO" \
  --title "[ci-autofix] Fix: <description courte du probleme>" \
  --label "ci-autofix,bug" \
  --body "## Echec CI detecte automatiquement

**Run :** https://github.com/$REPO/actions/runs/$RUN_ID
**Commit :** $HEAD_SHA

### Erreur
<message d'erreur exact>

### Analyse
<analyse de la cause racine>

### Plan de fix
<description du fix prevu>

---
_Issue creee automatiquement par ci-autofix_")

ISSUE_NUM=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')
```

---

## Etape 3 — Creer une branche et appliquer le fix

```bash
git checkout -b "fix/ci-autofix-${ISSUE_NUM}" origin/main
```

1. Applique le fix identifie en etape 1
2. Verifie que le fix est correct en lisant les tests concernes
3. Si l'environnement le permet, lance les tests localement :
   ```bash
   cd /workspace/culturall-website/backend
   python -m pytest -x -v <fichier_test_concerne> 2>&1 | tail -50
   ```
4. Commit et push :
   ```bash
   git add <fichiers modifies>
   git commit -m "[ci-autofix] Fix: <description courte>

   Resolves #${ISSUE_NUM}"
   git push origin "fix/ci-autofix-${ISSUE_NUM}"
   ```

**Si le test echoue apres le fix :** tente un deuxieme fix (max 2 tentatives).
Si toujours en echec apres 2 tentatives, passe a l'etape abandon (voir plus bas).

---

## Etape 4 — Ouvrir une PR

```bash
gh pr create \
  --repo "$REPO" \
  --base main \
  --head "fix/ci-autofix-${ISSUE_NUM}" \
  --title "[ci-autofix] Fix: <description courte>" \
  --body "## Fix automatique CI

Closes #${ISSUE_NUM}

### Probleme
<description de l'erreur>

### Fix applique
<description du fix>

### Verification
- [ ] Tests backend passes en CI
- [ ] Review manuelle recommandee

---
_PR creee automatiquement par ci-autofix_"
```

---

## Etape 5 — Commenter l'issue

```bash
gh issue comment "$ISSUE_NUM" --repo "$REPO" \
  --body "PR creee avec le fix. Review manuelle recommandee avant merge."
```

---

## Abandon (si 2 tentatives de fix echouent)

Si le fix ne fonctionne pas apres 2 tentatives :

```bash
gh issue comment "$ISSUE_NUM" --repo "$REPO" \
  --body "## Fix automatique echoue

Le ci-autofix n'a pas reussi a corriger l'erreur apres 2 tentatives.

### Derniere tentative
<description de ce qui a ete tente>

### Erreur persistante
<message d'erreur>

**Intervention manuelle requise.**"

gh issue edit "$ISSUE_NUM" --repo "$REPO" --add-label "help wanted"
```

Supprime la branche si aucun commit utile n'a ete pousse.

---

## Garde-fous

- **Ne JAMAIS push sur main directement** — toujours via une branche `fix/ci-autofix-*` + PR
- **Maximum 2 tentatives de fix** — au-dela, abandonner et signaler
- **Ne PAS modifier les fichiers de migration Django** (`*/migrations/*.py`) — si l'erreur concerne les migrations, signaler dans l'issue et ne pas tenter de fix automatique
- **Ne PAS modifier les fichiers de workflow GitHub Actions** (`.github/workflows/*.yml`) — risque de boucle infinie
- **Ne PAS modifier les fichiers de configuration sensibles** (`.env*`, `secrets`, credentials)
- **Prefixer tous les commits avec `[ci-autofix]`** — necessaire pour le garde anti-boucle du workflow
