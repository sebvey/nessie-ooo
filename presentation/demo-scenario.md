# Notes de démo

> Notes à suivre en live pendant la présentation. Le cas métier : une pipeline qui ingère des
> commandes (`orders`) et calcule un mart `daily_orders`. Objectif : **ne jamais laisser une
> mauvaise donnée arriver en prod (`main`)**.

## Avant de démarrer (préparation)

```bash
mise run stack-reset   # ardoise vierge : efface Nessie + MinIO
mise run stack-up      # démarre la stack et prépare main
```

`stack-up` affiche 3 étapes (sans pause) :
1. **Démarrer la stack** : Postgres, MinIO + bucket `iceberg-warehouse`, Nessie.
2. **État initial de Nessie** : `main` est sur le « commit zéro » (`2e1cfa8`), l'équivalent d'un
   dépôt Git vide. Aucun namespace, aucune table.
3. **Créer les namespaces** `raw` (données brutes) et `marts` (données transformées et testées).
   Un namespace Iceberg regroupe des tables, comme un schéma SQL (`raw.orders`). Dans Nessie, il est
   versionné : chaque création est un commit, d'où « +2 commits ».

→ La stack tourne, `main` contient les deux namespaces et **aucune table**.

> **Si on te demande pourquoi créer les namespaces à part** : un `main` tout neuf n'a aucun commit,
> et Nessie refuse de merger vers une branche sans historique (« No common ancestor »). Les
> namespaces donnent à `main` ses premiers commits. `mise run pipeline` refuse d'ailleurs de
> démarrer si `stack-up` n'a pas été lancé.

Utile à garder ouvert : `mise run branches` (liste des refs) et éventuellement la console MinIO
(http://localhost:29090, `minioadmin` / `8qqR90Az`).

---

## Acte 1 — le run qui marche

```bash
mise run pipeline
```

La pipeline s'arrête après chaque étape : **Entrée** pour passer à la suivante (`uv run pipeline --no-pause` pour
enchaîner). Ce qu'il faut lire à l'écran :
0. **État de départ** : le hash de `main` et le nombre de lignes de `raw.orders`. C'est la référence.
1. **Ouverture de branche** `pipeline-HHMMSS` depuis `main` : même commit, aucune donnée copiée.
2. **Ingestion** de 5 commandes (le tableau), **sur la branche** : la branche a 5 lignes de plus,
   `main` n'a pas bougé.
3. **`dbt build`** : `stg_orders` → `daily_orders` (écrite en Iceberg sur la branche) **+ tests**,
   8/8 OK. (`uv run pipeline --verbose` pour la sortie brute de dbt.)
4. Tests **verts** → **merge** dans `main` (le hash de `main` change), **tag `release-HHMMSS`**,
   branche supprimée.

**À montrer** : `main` contient maintenant les données, et un **tag immuable** marque cette promotion
(`mise run branches`).

---

## Acte 2 — le run qui casse — *le moment fort*

```bash
mise run pipeline-bad
```

Même pipeline, mais on injecte une **mauvaise donnée** :
1. Branche `pipeline-HHMMSS-bad` depuis `main`.
2. Ingestion des 5 lignes : le montant négatif et le client `null` sont **en rouge** dans le tableau.
3. **`dbt build`** : `montant ≥ 0` et `customer_id non null` **en échec**, `daily_orders` **non
   construit** (dbt saute ce qui dépend de tests rouges).
4. **PAS de merge** : le hash de `main` est **inchangé**, l'**alerte** s'affiche, la **branche est
   conservée** pour l'enquête.

**Message clé** : ***`main` est resté propre — la mauvaise donnée ne l'a jamais touché.***

---

## Acte 3 — explorer & prouver

- **`mise run branches`** : on voit `main`, la branche `-bad` conservée, et les tags `release-HHMMSS`.
- **`mise run notebook`** : basculer le sélecteur entre `main` (données validées) et `pipeline-…-bad`
  (données rejetées, isolées) — la démonstration visuelle de l'isolation.
- **`mise run dbt-inspect pipeline-…-bad`** : rejouer/déboguer la pipeline sur la branche fautive,
  sans rien casser en prod.
- **`mise run cli`** : parcours du REPL Nessie (historique, merge à blanc, rollback) dans
  [`demo-cli.md`](demo-cli.md).

---

## Bonus — la vie dans le temps

Rejouer `mise run pipeline` plusieurs fois : `raw.orders` **s'enrichit** (append de 5 lignes/run) et chaque
promotion laisse un **tag `release-HHMMSS`** → historique auditable et **rollback** possible
(« reviens à l'état de `release-…` »).
