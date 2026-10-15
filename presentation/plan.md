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
- **MinIO** — stockage objet S3 pour les fichiers **Iceberg**.

**Traitement (Python, sans JVM)**
- **PyIceberg** — accès au catalogue **scopé à une branche** (lecture/écriture Iceberg).
- **dbt** sur **DuckDB** — les transformations + les **tests** de qualité.
- **Plugin dbt-duckdb custom** — matérialise les marts en tables Iceberg sur la branche.

**Orchestration**
- **Client API Nessie** (Python) — le *control plane* : create branch / merge / alerte.
- **mise** — les commandes de démo (`stack-up`, `pipeline-ok`, `pipeline-ko`, `branches`).

**En une phrase :** Nessie + Iceberg + MinIO côté catalogue/stockage, dbt-DuckDB + PyIceberg
côté transformation/tests, orchestrés par un script Python et des tâches mise — le tout
**100 % local, zéro Java côté machine**.

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

## 4. Le scénario de démo

Trois actes : le run qui marche → le run qui casse (*le moment fort*) → explorer & prouver.

→ **Détail pas-à-pas dans [`demo-scenario.md`](demo-scenario.md) ; commandes du REPL pour l'acte 3 dans [`demo-cli.md`](demo-cli.md)** (notes à suivre en live).

---

## 5. Maturité des moteurs face à Nessie

Nessie est **niche** : tous les moteurs ne gèrent pas ses **branches** au même niveau. La maturité
ci-dessous porte sur l'intégration Nessie (surtout : **écrire/lire sur une branche ≠ `main`**), pas
sur le support Iceberg en général.

| Moteur | Rôle ici | Maturité Nessie | Détail |
|---|---|---|---|
| **Spark** | — | ✅ **Mature (natif)** | Extensions SQL Nessie : `CREATE BRANCH`, `USE REFERENCE`, `MERGE BRANCH … INTO main` en SQL. La voie canonique. Contrepartie : JVM, lourd. |
| **PyIceberg** | ingestion + écriture des marts | ✅ **Mature** | Parle à Nessie via l'endpoint Iceberg REST ; la **branche est dans l'URI** (`/iceberg/<branche>`). Respecte la redirection `overrides.uri` du protocole → marche sur **n'importe quelle branche**, en lecture **et** écriture. |
| **DuckDB** | transformations (dbt) | ⚠️ **Pas mature** | L'écriture Iceberg REST existe, mais le client **ignore `overrides.uri`** et double le prefix → il ne sait cibler que **`main`** ([bug #1145](https://github.com/duckdb/duckdb-iceberg/issues/1145), ouvert). En prime, `CREATE OR REPLACE TABLE` non supporté. **On a rusé** : DuckDB ne fait que **calculer**, et **PyIceberg** lit/écrit sur la branche (pont via Arrow + plugin dbt custom). |
| **Trino** | — | ⚠️ **Pas mature** | La branche est une **propriété statique du catalogue** (`iceberg.nessie-catalog.ref`), pas sélectionnable par session/requête ; pas de `CREATE/MERGE BRANCH` en SQL (propriété de session demandée, [issue #24134](https://github.com/trinodb/trino/issues/24134), non implémentée). |

**À retenir** : pour un workflow **multi-branches dynamique** comme le nôtre, seuls **Spark** (natif,
lourd) et **PyIceberg** (léger, via l'URI) sont vraiment prêts. DuckDB et Trino sont excellents sur
Iceberg « classique », mais butent encore sur les **branches Nessie**. D'où notre choix :
**PyIceberg pour le catalogue/branches + DuckDB pour le calcul** — le meilleur compromis léger
aujourd'hui.
