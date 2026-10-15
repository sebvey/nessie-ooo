# CLI Nessie — commandes utiles pour la démo

Aide-mémoire des commandes du **REPL Nessie** (la CLI SQL-like) pour piloter branches, tags,
merges et rollback à la main pendant la présentation.

> Toutes les commandes se terminent par `;`. `ReferenceType` = `BRANCH` ou `TAG`.
> La pipeline (`task run` / `task fail`) automatise déjà branche → merge → tag ; ces commandes
> servent à **explorer, montrer et faire un rollback en direct**.

## Se connecter

```bash
task nessie-cli          # ouvre le REPL déjà connecté à main
```

Ou manuellement, dans le REPL :

```sql
CONNECT TO http://localhost:19120/api/v2 ON main;
```

## Lister & inspecter

```sql
LIST REFERENCES;                 -- toutes les branches ET tags (nom, type, hash)
SHOW REFERENCE;                  -- la référence courante
USE BRANCH main;                 -- se positionner sur une branche (ou USE TAG <tag>)
LIST CONTENTS;                   -- namespaces / tables de la référence courante
SHOW LOG;                        -- historique des commits de la référence courante
SHOW LOG ON BRANCH main;         -- historique d'une référence précise (donne les hash)
```

## Créer une branche / un tag

```sql
CREATE BRANCH ma_branche;                       -- depuis la référence courante
CREATE BRANCH ma_branche FROM main;             -- depuis main
CREATE BRANCH IF NOT EXISTS ma_branche FROM main;

CREATE TAG release-manuel FROM main;            -- un tag = snapshot immuable

-- time-travel : créer depuis un point passé
CREATE BRANCH investigate FROM main AT TIMESTAMP 2026-07-08T10:00:00Z;
CREATE BRANCH investigate FROM main AT COMMIT <hash>;   -- hash via SHOW LOG
```

## Supprimer

```sql
DROP BRANCH ma_branche;
DROP TAG release-manuel;
DROP BRANCH IF EXISTS ma_branche;
```

## Merger

```sql
MERGE BRANCH pipeline-HHMMSS INTO main;         -- promotion
MERGE DRY BRANCH pipeline-HHMMSS INTO main;     -- simulation (ne modifie rien)
```

## Rollback / restaurer un état

`ASSIGN` **repointe** une branche (ou un tag) vers un autre état — c'est le rollback.

```sql
-- ramener main à l'état capturé par un tag précédent
ASSIGN BRANCH main TO release-170656;

-- ramener main à un commit précis (hash via SHOW LOG)
ASSIGN BRANCH main TO main AT COMMIT <hash>;

-- ou à un instant donné
ASSIGN BRANCH main TO main AT TIMESTAMP 2026-07-08T10:00:00Z;

-- déplacer / re-poser un tag sur l'état courant de main
ASSIGN TAG release-manuel TO main;
```

> Idée de démo : après un `task run`, faire un `task fail` (rejeté, main intact), puis montrer
> qu'on peut aussi **revenir en arrière** sur `main` avec `ASSIGN BRANCH main TO release-…` —
> la donnée « comme du code », rollback compris.

## Quitter

```sql
EXIT;
```
(ou `Ctrl-D`)
