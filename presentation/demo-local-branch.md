# Travailler sur sa propre branche

Faire ses `dbt build` sur une branche Nessie à soi, sans toucher à `main`. Prérequis : la stack tourne
(`mise run stack-up`).

## 1. Créer la branche

```bash
mise run cli
```

Puis dans le REPL :

```sql
CREATE BRANCH ma-branche FROM main;
```

## 2. Pointer dbt sur la branche

Dans `mise.local.toml` (à la racine, ignoré par git) :

```toml
[env]
NESSIE_BRANCH = "ma-branche"
```

dbt lit et écrit maintenant sur `ma-branche` (depuis la racine ou depuis `dbt/`) :

```bash
mise exec -- uv run dbt build
```

Vérifier la branche active : `mise env | grep NESSIE_BRANCH`.

## 3. Supprimer la branche

Remettre `NESSIE_BRANCH = "main"` dans `mise.local.toml`, puis dans le REPL (`mise run cli`) :

```sql
DROP BRANCH ma-branche;
```
