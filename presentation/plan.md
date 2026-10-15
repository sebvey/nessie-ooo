# Présentation Nessie — grandes lignes

> Plan de la présentation. Les sections suivantes sont à étoffer.

---

## 1. Pourquoi Nessie

**Le problème**
- Une pipeline écrit **directement dans les tables de prod**.
- La mauvaise donnée est **visible tout de suite** par les consommateurs.
- Tester en isolation, revenir en arrière, coordonner plusieurs tables : **douloureux**.

**L'idée : Git, mais pour les données**
Nessie versionne le **catalogue** de tables (les pointeurs de métadonnées), pas les fichiers.
On récupère les réflexes de Git — **branch / commit / merge / tag** — sur des tables Iceberg,
**sans copier la donnée**.

**Ce que ça débloque**
- **Isolation** — on transforme et on teste sur une **branche**, invisible de la prod.
- **Merge atomique** — promotion tout-ou-rien vers `main` (plusieurs tables d'un coup).
- **Rollback** — revenir à un commit précédent en une opération.
- **Reproductibilité** — rejouer/auditer l'état exact via un tag ou un commit.

**Le fil rouge de la démo**
> Traiter la donnée **comme du code** : brancher → tester → ne merger que si c'est vert.
> La mauvaise donnée n'atteint **jamais** `main`.

---

## 2. La stack

**Infra (docker-compose)**
- **Nessie** — le catalogue versionné « à la Git » (branches / merge). *La star.*
- **PostgreSQL** — le version store de Nessie (persiste commits & branches).
- **Silo** — stockage objet S3 pour les fichiers **Iceberg** (fork communautaire de MinIO, image `pgsty/minio`).

**Orchestration** — au-dessus du data plane et du control plane
- **pipeline.py** — l'orchestrateur : enchaîne les étapes et **décide** merge ou alerte (la porte de
  qualité). En production : Airflow, Dagster, Prefect ou une CI. Ne pilote pas l'infra.

**Data plane (Python) — lire, transformer**
- **PyIceberg** — accès au catalogue **scopé à une branche** (lecture/écriture Iceberg).
- **dbt** sur **DuckDB** — les transformations + les **tests** de qualité.
- **Plugin dbt-duckdb custom** — matérialise les marts en tables Iceberg sur la branche.

**Control plane (Python) — agir, prévenir**
- **nessie.py** — classe Python qui appelle l'API REST de Nessie : branche, merge, tag.
- **Alerte** — console, plus un webhook Slack en option.

L'infra est démarrée par `mise run stack-up` ; la pipeline par `mise run pipeline-ok` / `pipeline-ko`.

**En une phrase :** Nessie + Iceberg + Silo côté infra, PyIceberg + dbt-DuckDB côté data plane,
`nessie.py` côté control plane, et `pipeline.py` qui orchestre les deux — le tout
**100 % local**.

---

## 3. La pipeline

Une pipeline = **4 étapes**, orchestrées par un script Python (`pipeline.py`).

```
ouvre branche ──► ingère ──► dbt build (transform + test) ──► vert ? ──► MERGE + TAG sur main ✅
pipeline-HHMMSS    (raw)      (marts)                           │
      ▲                                                         └─ rouge ? ──► pas de merge + ALERTE ⛔
      └── depuis main                                                          (branche conservée)
```

**Étape par étape**
1. **Ouvrir une branche** `pipeline-HHMMSS` depuis `main` — *control plane*, via l'**API Nessie**.
2. **Ingérer** 5 commandes dans `raw.orders`, **sur la branche** — **PyIceberg** (append).
3. **`dbt build`** (DuckDB) — `raw` → `stg_orders` → `daily_orders` **+ tests** ; le mart est écrit
   en Iceberg sur la branche (plugin custom).
4. **Décider** — verts → **merge** branche→`main` + **tag `release-HHMMSS`** (atomique, Nessie) ;
   rouges → **pas de merge**, **alerte**, branche **conservée** pour debug.

**Le point d'architecture** : le *control plane* (brancher / merger / tag) passe par l'**API Nessie** ;
le *data plane* (lire/écrire les tables **sur la branche**) passe par **PyIceberg** (la branche est
dans l'URI). dbt ne fait qu'une chose : **transformer + tester** la branche qu'on lui désigne.
Résultat : la mauvaise donnée est **confinée**, `main` n'est touché qu'après un test vert.

---

## 4. Travailler sur une branche : le principe

**La branche, c'est une adresse.** Nessie sert un catalogue Iceberg REST par branche :
`/iceberg/<branche>`. Un client branché sur cette adresse voit un catalogue normal, et chaque écriture
devient un commit sur la branche.

Dans le cas idéal, **un seul moteur** suffit : DuckDB attache l'adresse de la branche, lit `raw.orders`,
calcule `stg_orders` → `daily_orders`, lance les tests et écrit le mart, le tout en SQL.

```sql
ATTACH 'warehouse' AS lake (TYPE iceberg, ENDPOINT 'http://localhost:19120/iceberg/pipeline-143205');
```

Personne n'utilise `/iceberg/main` avant le merge : `main` ne peut pas bouger.

---

## 5. Travailler sur une branche : le contournement actuel

**Le bug.** Nessie répond à `/v1/config` avec `prefix = <branche>` et `overrides.uri = /iceberg/`. La
bonne adresse est donc `/iceberg/v1/<branche>/…` (200). DuckDB ignore `overrides.uri` et colle le
préfixe derrière l'adresse de la branche : `/iceberg/<branche>/v1/<branche>/…` (404). Reproduit avec
DuckDB 1.4.3, y compris sur `main`.

**Le détour.** DuckDB ne fait que calculer et tester. PyIceberg, qui respecte `overrides.uri`, parle à
la branche :
- **lecture** : le plugin `iceberg` fourni avec dbt-duckdb charge `raw.orders` via PyIceberg, en Arrow ;
- **écriture** : notre plugin `iceberg_write` réécrit `daily_orders` sur la branche via PyIceberg.

**Le prix.** Les données transitent en mémoire (Arrow), un plugin maison à maintenir, et le mart est
réécrit en entier à chaque run.

**La suite.** Corrigé dans l'extension DuckDB ([#1230](https://github.com/duckdb/duckdb-iceberg/pull/1230),
juillet 2026), pas encore dans une version publiée (la 1.5.6 du 28/09/2026 ne l'inclut pas). Dès sa
sortie : retirer les plugins et revenir au principe de la section 4.

---

## 6. Le scénario de démo

Trois actes : le run qui marche → le run qui casse (*le moment fort*) → explorer & prouver.

→ **Détail pas-à-pas dans [`demo-scenario.md`](demo-scenario.md) ; commandes du REPL pour l'acte 3 dans [`demo-cli.md`](demo-cli.md)** (notes à suivre en live).

---

## 7. Maturité des moteurs face à Nessie

Nessie est **niche** : tous les moteurs ne gèrent pas ses **branches** au même niveau. La maturité
ci-dessous porte sur l'intégration Nessie (surtout : **écrire/lire sur une branche ≠ `main`**), pas
sur le support Iceberg en général.

| Moteur | Rôle ici | Maturité Nessie | Détail |
|---|---|---|---|
| **Spark** | — | ✅ **Mature (natif)** | Extensions SQL Nessie : `CREATE BRANCH`, `USE REFERENCE`, `MERGE BRANCH … INTO main` en SQL. La voie canonique. Contrepartie : JVM, lourd. |
| **PyIceberg** | ingestion + écriture des marts | ✅ **Mature** | Parle à Nessie via l'endpoint Iceberg REST ; la **branche est dans l'URI** (`/iceberg/<branche>`). Respecte la redirection `overrides.uri` du protocole → marche sur **n'importe quelle branche**, en lecture **et** écriture. |
| **DuckDB** | transformations (dbt) | ⚠️ **Pas encore** | Jusqu'à la **1.5.6** (28/09/2026), le client **ignore `overrides.uri`** et double le prefix → il ne sait cibler que **`main`** ([#1145](https://github.com/duckdb/duckdb-iceberg/issues/1145)). **Corrigé** dans l'extension par [#1230](https://github.com/duckdb/duckdb-iceberg/pull/1230) (mergée le 26/07/2026 sur la branche principale), **pas encore dans une version publiée** de DuckDB (non testé de notre côté). `CREATE OR REPLACE TABLE` toujours non supporté ([#784](https://github.com/duckdb/duckdb-iceberg/issues/784), ouverte). **On a rusé** : DuckDB ne fait que **calculer**, et **PyIceberg** lit/écrit sur la branche (pont via Arrow + plugin dbt custom). |
| **Trino** | — | ⚠️ **Pas mature** | La branche Nessie est une **propriété statique du catalogue** (`iceberg.nessie-catalog.ref`), pas sélectionnable par session/requête (propriété de session demandée dans [#24134](https://github.com/trinodb/trino/issues/24134), fermée « not planned » en avril 2025). Trino a ajouté en 2025 `CREATE / DROP / FAST FORWARD BRANCH … IN TABLE` et l'écriture sur une branche, mais ce sont des **branches Iceberg, table par table** : rien à voir avec une branche Nessie qui couvre tout le catalogue. |

**À retenir** : pour un workflow **multi-branches dynamique** comme le nôtre, seuls **Spark** (natif,
lourd) et **PyIceberg** (léger, via l'URI) sont vraiment prêts. DuckDB et Trino sont excellents sur
Iceberg « classique », mais butent encore sur les **branches Nessie**. D'où notre choix :
**PyIceberg pour le catalogue/branches + DuckDB pour le calcul** — le meilleur compromis léger
aujourd'hui.
