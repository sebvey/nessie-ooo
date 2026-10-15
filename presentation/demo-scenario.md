# Notes de démo

> Notes à suivre en live pendant la présentation. Le cas métier : une pipeline qui ingère des
> commandes (`orders`) et calcule un mart `daily_orders`. Objectif : **ne jamais laisser une
> mauvaise donnée arriver en prod (`main`)**.

## Avant de démarrer (préparation)

```bash
mise run reset   # ardoise vierge : efface Nessie + MinIO
mise run up       # démarre la stack (Nessie + Postgres + MinIO) + crée le bucket
```
→ La stack tourne, `main` est **vide**.

Utile à garder ouvert : `mise run branches` (liste des refs) et éventuellement la console MinIO
(http://localhost:29090, `minioadmin`/`minioadmin`).

---

## Acte 1 — le run qui marche

```bash
mise run pipeline
```

Commenter les 4 étapes qui s'affichent :
1. **Ouverture de branche** `pipeline-HHMMSS` depuis `main` (Nessie).
2. **Ingestion** de 5 commandes fraîches dans `raw.orders`, **sur la branche** (invisible de `main`).
3. **`dbt build`** = transformations (`stg_orders` → `daily_orders`) **+ tests** de qualité.
4. Tests **verts** → **merge** dans `main`, **tag `release-HHMMSS`** posé, branche supprimée.

**À montrer** : `main` contient maintenant les données, et un **tag immuable** marque cette promotion
(`mise run branches`).

---

## Acte 2 — le run qui casse — *le moment fort*

```bash
mise run pipeline-bad
```

Même pipeline, mais on injecte une **mauvaise donnée** (montant négatif, client `null`) :
1. Branche `pipeline-HHMMSS-bad` depuis `main`.
2. Ingestion des 5 lignes, dont les lignes sales.
3. **`dbt build`** → les **tests passent au rouge**.
4. → **PAS de merge**, une **alerte** est levée, et la **branche est conservée** pour inspection.

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
