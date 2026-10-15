# Démo Nessie — pipeline *branch → test → merge* sur un lakehouse Iceberg

Démo pour présenter **Project Nessie** : un catalogue de tables **versionné « à la Git »**.
Elle met en scène une pipeline data qui traite les données **sur une branche isolée**, les
**teste avec dbt**, et ne les **merge sur `main`** que si les tests passent — sinon la mauvaise
donnée reste confinée sur la branche et une **alerte** est levée. `main` n'est jamais pollué.

```
ouvre branche  ──►  ingère données  ──►  dbt build (transform + test)  ──►  tests verts ? ──► MERGE sur main ✅
pipeline_YYYYMMDD      (raw.orders)        (marts.daily_orders)                    │
       ▲                                                                          └─ tests rouges ? ──► PAS de merge + ALERTE ⛔
       └── créée depuis main                                                          (branche conservée pour debug)
```

## La stack

| Rôle | Techno | Pourquoi |
|---|---|---|
| Catalogue versionné (branches/merge) | **Nessie** | le sujet de la démo — Git pour les tables |
| Format de table | **Apache Iceberg** | tables ouvertes, snapshots |
| Stockage objet | **MinIO** (S3) | fichiers de données/métadonnées Iceberg |
| Version store de Nessie | **PostgreSQL** | persiste l'historique des commits/branches |
| Moteur de transformation + tests | **dbt** sur **DuckDB** | léger, pas de JVM |
| Accès catalogue + **branches** | **PyIceberg** | seul chemin propre pour cibler une branche Nessie |
| Control plane (branch/merge/alerte) | **API REST Nessie** (Python) | opérations Git *hors* dbt |

> **Pourquoi ce découpage ?** Nessie sépare deux plans. Le *control plane* (créer/merger une
> branche) est propre à Nessie et vit dans l'orchestrateur Python. Le *data plane* (lire/écrire
> des tables **sur une branche**) passe par PyIceberg : la branche est encodée dans l'URI REST
> (`/iceberg/<branche>`). DuckDB ne sert que de moteur de calcul SQL. On a testé DuckDB en accès
> REST natif : il sait écrire de l'Iceberg mais **ne sait pas cibler une branche Nessie ≠ main** —
> d'où PyIceberg pour le catalogue.

## Prérequis

- Docker (+ compose)
- [`mise`](https://mise.jdx.dev) (tâches + variables d'environnement, voir `mise.toml`)
- [`uv`](https://docs.astral.sh/uv/)

## Démarrage

```bash
mise run stack-up      # démarre Nessie + Postgres + MinIO, crée le bucket et les namespaces raw / marts
mise run pipeline     # pipeline nominale : branche → ingest → dbt build (vert) → MERGE sur main ✅
mise run pipeline-bad    # pipeline en échec : mauvaise donnée → tests rouges → PAS de merge + ALERTE ⛔
```

Autres commandes :

```bash
mise run branches                 # liste les branches Nessie
mise run dbt-inspect <branche> # rejoue dbt sur une branche (ex. la branche _bad conservée)
mise run stack-down                     # arrête la stack (garde les données)
mise run stack-reset                    # arrête et efface tout (repart de zéro)
```

- Nessie API : http://localhost:19120
- Console MinIO : http://localhost:29090 (`minioadmin` / `8qqR90Az`)

## Explorer les données (notebook marimo)

```bash
mise run notebook   # ouvre notebooks/explore.mo.py dans marimo
```

Notebook **réactif** pour explorer le catalogue :
- un **sélecteur de branche** (alimenté par l'API Nessie) + bouton refresh ;
- l'**historique des commits** de la branche choisie ;
- un **navigateur de tables** Iceberg (namespaces → tables) avec schéma et nb de snapshots ;
- une **table interactive** (tri / filtre / pagination) ;
- un **éditeur SQL DuckDB** sur toutes les tables de la branche.

Changer de branche recharge automatiquement tout le reste — pratique pour montrer, côte à côte,
`main` (données validées) vs une branche `pipeline_…_bad` (données rejetées, isolées).

## Déroulé de présentation suggéré

1. **`mise run stack-up`** — la stack monte, `main` contient les namespaces `raw` et `marts`, aucune table.
2. **`mise run pipeline`** — commente chaque étape `[1/4] … [4/4]`. À la fin, montre via `mise run branches`
   que `main` contient maintenant `raw.orders` et `marts.daily_orders`, et que la branche
   `pipeline_YYYYMMDD` a été **mergée puis supprimée**.
3. **`mise run pipeline-bad`** — le moment fort : on injecte une donnée sale (montant négatif, client `null`).
   Les tests dbt passent au **rouge**, la pipeline **refuse le merge**, lève une **alerte**, et
   **conserve la branche** `pipeline_YYYYMMDD_bad`. Insiste : *`main` est resté propre, la mauvaise
   donnée ne l'a jamais touché.*
4. **`mise run dbt-inspect pipeline_YYYYMMDD_bad`** — montre qu'on peut rejouer/déboguer la
   pipeline sur la branche fautive, en isolation totale, sans rien casser en production.

## Ce qui se passe sous le capot

- **1. branche** — `Nessie.create_branch(pipeline_YYYYMMDD, from=main)` (API REST Nessie).
- **2. ingestion** — `ingest.py` génère un petit dataset synthétique et l'écrit dans `raw.orders`
  **sur la branche** via PyIceberg (`--bad` injecte les lignes fautives).
- **3. dbt build** — `NESSIE_BRANCH=<branche> dbt build` :
  - lit `raw.orders` sur la branche (plugin iceberg de lecture),
  - construit `stg_orders` (vue) puis `marts.daily_orders` — **matérialisé en table Iceberg sur la
    branche** via un petit plugin dbt-duckdb custom (`iceberg_write`),
  - lance les **tests** (`not_null`, `unique`, montant ≥ 0…).
- **4. décision** — tests verts → `Nessie.merge(branche → main)` (atomique) ; tests rouges → pas de
  merge, `alert()`, branche conservée.

## Arborescence

```
├─ docker-compose.yml          # Nessie + Postgres + MinIO + init bucket
├─ mise.toml                   # tâches : up / pipeline / pipeline-bad / branches / reset …
├─ src/nessie_demo/
│  ├─ settings.py              # config (URIs Nessie, S3) — défauts locaux
│  ├─ nessie.py                # client Nessie v2 : branch / merge / delete / list
│  ├─ catalog.py               # catalogue PyIceberg scoppé à une branche
│  ├─ ingest.py                # dataset synthétique → raw.orders (--bad pour l'échec)
│  ├─ pipeline.py              # orchestrateur : les 4 étapes ci-dessus
│  ├─ alert.py                 # alerte (console + webhook Slack optionnel)
│  └─ dbt_plugins/iceberg_write.py  # plugin dbt-duckdb : écrit un modèle en Iceberg sur la branche
└─ dbt/
   ├─ profiles.yml             # dbt-duckdb, branche = env NESSIE_BRANCH
   ├─ models/staging/          # sources.yml, stg_orders (+ tests)
   ├─ models/marts/            # daily_orders (table Iceberg) (+ tests)
   └─ tests/                   # test singulier : montant ≥ 0

docs/  — fiches d'apprentissage Nessie/Iceberg (conservées de l'exploration initiale)
```

## Alerte Slack (optionnel)

```bash
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/…
mise run pipeline-bad   # l'alerte est aussi postée sur Slack
```
