# Démo CLI Nessie, pas à pas

Parcours guidé du REPL Nessie pour l'acte 3. Prérequis : la stack tourne (`mise run stack-up`), au moins un `mise run pipeline-ok` puis un `mise run pipeline-ko` ont été lancés.

```bash
mise run cli
```

Toutes les commandes se terminent par `;`.

## 1. Où suis-je ?

```sql
SHOW REFERENCE;
```

**À voir** : `main`.
**À dire** : comme dans Git, on est toujours positionné sur une référence (branche ou tag).

## 2. Les branches et tags existants

```sql
LIST REFERENCES;
```

**À voir** : `main`, `pipeline-HHMMSS-bad`, `release-HHMMSS`.
**À dire** :
- la branche `-bad` est toujours là : c'est la mauvaise donnée, isolée ;
- le tag `release-…` a **le même hash que `main`** : c'est la dernière promotion validée.

## 3. Ce que contient `main`

```sql
LIST CONTENTS;
```

**À voir** : `raw.orders` et `marts.daily_orders` (type `ICEBERG_TABLE`).
**À dire** : Nessie ne stocke pas de données, seulement des pointeurs vers des tables Iceberg.

## 4. L'historique de `main`

```sql
SHOW LOG;
```

**À voir** : le plus récent en haut. Un commit `Merged pipeline-… into main` avec **deux parents** (un vrai merge, comme dans Git), puis plus bas les commits `update namespace raw/marts` qui ont initialisé `main`.

## 5. Passer sur la branche fautive

```sql
USE BRANCH pipeline-HHMMSS-bad;
SHOW LOG;
```

Remplacer `HHMMSS` par le nom affiché à l'étape 2.

**À voir** : en plus de l'historique de `main`, le commit d'ingestion fait sur la branche.
**À dire** : ce commit n'existe pas dans `main`.

Revenir sur `main` :

```sql
USE BRANCH main;
```

## 6. Simuler un merge, sans rien modifier

```sql
MERGE DRY BRANCH pipeline-HHMMSS-bad INTO main;
```

**À voir** : Nessie dit si le merge serait possible, sans l'appliquer.
**À dire** : la pipeline a refusé de merger parce que les tests dbt étaient rouges ; Nessie, lui, l'aurait accepté. C'est la pipeline qui décide de la qualité, Nessie apporte l'isolation.

## 7. Créer une branche à la main

```sql
CREATE BRANCH demo FROM main;
LIST REFERENCES;
```

**À dire** : la branche est créée instantanément. Aucune donnée n'est copiée, on a juste un nouveau pointeur.

## 8. Rollback (le point fort)

Il faut au moins deux tags `release-…`. Sinon, lancer `mise run pipeline-ok` dans un autre terminal.

```sql
LIST REFERENCES;
ASSIGN BRANCH main TO release-<le-plus-ancien>;
SHOW LOG;
```

**À voir** : `main` revient à l'état de ce tag.
**À dire** : rollback en une seule opération. Comme pour un `git reset`, les commits plus récents restent accessibles par leur tag.

## 9. Nettoyer et quitter

```sql
DROP BRANCH demo;
EXIT;
```
