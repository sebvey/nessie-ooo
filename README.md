# Démo Nessie — pipeline *branch → test → merge* sur un lakehouse Iceberg

Démo pour présenter **Project Nessie** : un catalogue de tables **versionné « à la Git »**.
Elle met en scène une pipeline data qui traite les données **sur une branche isolée**, les
**teste avec dbt**, et ne les **merge sur `main`** que si les tests passent — sinon la mauvaise
donnée reste confinée sur la branche et une **alerte** est levée. `main` n'est jamais pollué.

```
ouvre branche  ──►  ingère données  ──►  dbt build (transform + test)  ──►  tests verts ? ──► MERGE + TAG sur main ✅
pipeline-HHMMSS      (raw.orders)        (marts.daily_orders)                    │      release-HHMMSS
       ▲                                                                        └─ tests rouges ? ──► PAS de merge + ALERTE ⛔
       └── créée depuis main                                                        (branche pipeline-HHMMSS-bad conservée)
```

## La stack

| Rôle | Techno | Pourquoi |
|---|---|---|
| Catalogue versionné (branches/merge) | **Nessie** | le sujet de la démo — Git pour les tables |
| Format de table | **Apache Iceberg** | tables ouvertes, snapshots |
| Stockage objet | **MinIO** (S3) | fichiers de données/métadonnées Iceberg |
| Version store de Nessie | **PostgreSQL** | persiste l'historique des commits/branches |
| Moteur de transformation + tests | **dbt** sur **DuckDB** | léger |
| Accès catalogue + **branches** | **PyIceberg** | seul chemin propre pour cibler une branche Nessie |
| Control plane (branch/merge/alerte) | **API REST Nessie** (Python) | opérations Git *hors* dbt |

> **Pourquoi ce découpage ?** Nessie sépare deux plans. Le *control plane* (créer/merger une
> branche) est propre à Nessie et vit dans l'orchestrateur Python. Le *data plane* (lire/écrire
> des tables **sur une branche**) passe par PyIceberg : la branche est encodée dans l'URI REST
> (`/iceberg/<branche>`). DuckDB ne sert que de moteur de calcul SQL : jusqu'à sa version 1.5.6,
> son accès REST natif **ne sait pas cibler une branche Nessie ≠ main**
> ([duckdb-iceberg#1145](https://github.com/duckdb/duckdb-iceberg/issues/1145), corrigé dans
> l'extension mais pas encore publié). D'où PyIceberg pour le catalogue.

## Prérequis

- Docker (+ compose)
- [`mise`](https://mise.jdx.dev) (variables d'environnement dans `mise.toml`, tâches dans `tasks.toml`)
- [`uv`](https://docs.astral.sh/uv/) (installé par mise)

## Démarrage

```bash
mise run stack-up      # démarre Nessie + Postgres + MinIO, crée le bucket et les namespaces raw / marts
mise run pipeline-ok   # pipeline nominale : branche → ingest → dbt build (vert) → MERGE sur main ✅
mise run pipeline-ko   # pipeline en échec : mauvaise donnée → tests rouges → PAS de merge + ALERTE ⛔
```

Autres commandes :

```bash
mise run branches              # liste les branches et tags Nessie
mise run cli                   # REPL Nessie (voir presentation/demo-cli.md)
mise run notebook              # notebook marimo pour explorer une branche
mise run dbt-inspect <branche> # rejoue dbt sur une branche (ex. la branche -bad conservée)
mise run stack-down            # arrête la stack (garde les données)
mise run stack-reset           # arrête et efface tout (repart de zéro)
```

- Nessie API : http://localhost:19120
- Console MinIO : http://localhost:29090 (`minioadmin` / `8qqR90Az`)

## Explorer les données (notebook marimo)

```bash
mise run notebook   # ouvre notebooks/explore.mo.py dans marimo
```

Notebook **réactif** pour comparer les branches :
- un **sélecteur de branche**, alimenté par l'API Nessie (branches seulement, pas les tags) ;
- le chargement de `raw.orders` sur la branche choisie, via PyIceberg ;
- une **cellule SQL DuckDB** sur cette table, qui filtre les commandes à montant négatif.

Changer de branche relance tout : sur `main`, la requête ne renvoie rien ; sur une branche
`pipeline-…-bad`, elle renvoie la ligne rejetée. Le notebook plante sur une branche qui n'a pas
encore `raw.orders` (par exemple `main` avant le premier run).

## Déroulé de présentation

Notes à suivre en live : [`presentation/demo-scenario.md`](presentation/demo-scenario.md) (les trois
actes) et [`presentation/demo-cli.md`](presentation/demo-cli.md) (parcours du REPL, rollback compris).

## Ce qui se passe sous le capot

- **mise en place** (`stack-up`, `bootstrap.py`) — démarre la stack puis crée les namespaces `raw`
  et `marts` sur `main` : un `main` sans commit ne peut pas recevoir de merge (« No common ancestor »).
- **0. état de départ** — hash de `main` et contenu des tables, lus via l'API Nessie et les
  métadonnées Iceberg.
- **1. branche** — `Nessie.create_branch("pipeline-HHMMSS", from_ref="main")` (API REST Nessie).
- **2. ingestion** — `ingest.py` génère 5 commandes synthétiques et les ajoute à `raw.orders`
  **sur la branche** via PyIceberg (`--bad` injecte un montant négatif et un client `null`).
- **3. dbt build** — `NESSIE_BRANCH=<branche> dbt build` :
  - lit `raw.orders` sur la branche (plugin iceberg de lecture),
  - construit `stg_orders` (vue) puis `marts.daily_orders`, **matérialisé en table Iceberg sur la
    branche** via un petit plugin dbt-duckdb custom (`iceberg_write`),
  - lance les **tests** (`not_null`, `unique`, montant ≥ 0…).
- **4. décision** — tests verts → `Nessie.merge(branche → main)` (atomique), tag `release-HHMMSS`,
  branche supprimée ; tests rouges → pas de merge, `alert()`, branche conservée.

## Arborescence

```
├─ docker-compose.yml          # Nessie + Postgres + MinIO + init bucket
├─ mise.toml                   # outils + variables d'environnement
├─ tasks.toml                  # tâches : stack-up / pipeline-ok / pipeline-ko / branches / stack-reset …
├─ src/nessie_demo/
│  ├─ settings.py              # config (URIs Nessie, S3) — défauts locaux
│  ├─ nessie.py                # client Nessie v2 : branch / merge / tag / delete / list
│  ├─ catalog.py               # catalogue PyIceberg scopé à une branche
│  ├─ ingest.py                # dataset synthétique → raw.orders (--bad pour l'échec)
│  ├─ bootstrap.py             # mise en place (stack-up) : stack + namespaces sur main
│  ├─ pipeline.py              # orchestrateur : les étapes 0 à 4 ci-dessus
│  ├─ display.py               # sortie console narrée (étapes, pauses, tableaux)
│  ├─ alert.py                 # alerte (console + webhook Slack optionnel)
│  └─ dbt_plugins/iceberg_write.py  # plugin dbt-duckdb : écrit un modèle en Iceberg sur la branche
└─ dbt/
   ├─ profiles.yml             # dbt-duckdb, branche = env NESSIE_BRANCH
   ├─ models/staging/          # sources.yml, stg_orders (+ tests)
   ├─ models/marts/            # daily_orders (table Iceberg) (+ tests)
   └─ tests/                   # test singulier : montant ≥ 0

notebooks/explore.mo.py  — notebook marimo
presentation/            — slides (iceberg.html, presentation.html) et notes de démo
docs/                    — fiches d'apprentissage Nessie/Iceberg (conservées de l'exploration initiale)
```

## Alerte Slack (optionnel)

```bash
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/…
mise run pipeline-ko   # l'alerte est aussi postée sur Slack
```
