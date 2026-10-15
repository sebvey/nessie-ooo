# Se passer de PyIceberg avec la préversion DuckDB 2.0

Objectif : que DuckDB lise et écrive **directement** sur une branche Nessie (slide 04, « La branche,
c'est une adresse »), sans le détour par les plugins PyIceberg (slide 05).

## Où on en est (tests du 15/10/2026)

| Version | Adresse appelée | Résultat |
|---|---|---|
| DuckDB 1.5.6 (stable), extension `core` | `/iceberg/<br>/v1/<br>\|warehouse/…` | ❌ aucune table visible |
| DuckDB 1.5.6, extension `core_nightly` | idem | ❌ (extension construite depuis la branche 1.5, sans le correctif) |
| DuckDB `2.0.0.dev2610011535` (préversion PyPI, 02/10/2026) | `/iceberg/v1/<br>\|warehouse/…` | ✅ lecture et écriture sur la branche |

Le correctif est [duckdb/duckdb-iceberg#1230](https://github.com/duckdb/duckdb-iceberg/pull/1230)
(« Honor REST catalog URI overrides », mergée le 26/07/2026 sur `main`). Il n'arrivera dans une
version stable qu'avec DuckDB 2.0.

Opérations testées sur une branche jetable (`main` intact) :

| Opération | Résultat |
|---|---|
| `SELECT` sur `raw.orders` | ✅ |
| `CREATE TABLE … AS SELECT` | ✅ commit « Create ICEBERG_TABLE » sur la branche |
| `INSERT`, `DELETE`, `DROP TABLE` | ✅ avec `SET iceberg_use_metadata_log = false` (sinon ❌) |
| `CREATE OR REPLACE TABLE` | ❌ non supporté ([#784](https://github.com/duckdb/duckdb-iceberg/issues/784)) : passer par `DROP` + `CREATE` |

## Reproduire le test (5 minutes)

Prérequis : la stack tourne (`mise run stack-up`) et au moins un `mise run pipeline-ok` a été lancé.

1. Créer une branche jetable depuis `main` :

```bash
mise run cli -c "CREATE BRANCH duckdb-probe FROM main;"
```

2. Enregistrer ce script, par exemple dans `/tmp/duckdb_probe.py` :

```python
import duckdb

c = duckdb.connect()
c.sql("INSTALL httpfs; LOAD httpfs; INSTALL iceberg; LOAD iceberg")
# Accès aux fichiers Iceberg dans MinIO
c.sql("""CREATE SECRET (TYPE s3, KEY_ID 'minioadmin', SECRET '8qqR90Az',
         ENDPOINT 'localhost:29000', URL_STYLE 'path', USE_SSL false, REGION 'us-east-1')""")
# Sans ce réglage, toute écriture après la création d'une table échoue
# ("table metadata does not contain a metadata-log").
c.sql("SET iceberg_use_metadata_log = false")
# La branche est dans l'adresse
c.sql("""ATTACH 'warehouse' AS lake (TYPE iceberg, AUTHORIZATION_TYPE 'none',
         ENDPOINT 'http://localhost:19120/iceberg/duckdb-probe')""")

print(c.sql("SELECT count(*) FROM lake.raw.orders").fetchone())
c.sql("""CREATE TABLE lake.marts.probe AS
         SELECT cast(order_ts AS date) AS order_date, count(*) AS n
         FROM lake.raw.orders GROUP BY 1""")
c.sql("INSERT INTO lake.marts.probe VALUES (DATE '2000-01-01', 0)")
c.sql("DELETE FROM lake.marts.probe WHERE n = 0")
print(c.sql("FROM lake.marts.probe").fetchall())
c.sql("DROP TABLE lake.marts.probe")
```

3. Le lancer avec la préversion, sans toucher à l'environnement du projet :

```bash
uv run --isolated --no-project --prerelease allow --with duckdb==2.0.0.dev2610011535 python /tmp/duckdb_probe.py
```

4. Constater les commits sur la branche, et que `main` n'a pas bougé :

```bash
mise run cli -c "SHOW LOG ON BRANCH duckdb-probe;" -c "SHOW LOG ON BRANCH main;"
```

5. Nettoyer :

```bash
mise run cli -c "DROP BRANCH duckdb-probe;"
```

Pour voir les adresses appelées par DuckDB, ajouter `c.sql("CALL enable_logging('HTTP')")` après le
`LOAD iceberg`, puis `c.sql("SELECT message FROM duckdb_logs WHERE type = 'HTTP'").fetchall()`.

## Brancher la démo dessus

Rien de ce qui suit n'est testé. Ordre conseillé, chaque étape validée avant la suivante :

1. **Dépendances.** Dans `pyproject.toml`, passer `duckdb` sur la préversion
   (`duckdb==2.0.0.dev2610011535`) et autoriser les préversions pour uv
   (`[tool.uv] prerelease = "allow"`). Point à vérifier en premier : **dbt-duckdb accepte-t-il DuckDB
   2.0 ?** Si `uv sync` ou `dbt debug` échoue, on s'arrête là.

2. **Profil dbt** (`dbt/profiles.yml`). Remplacer les deux plugins par un `attach` sur l'adresse de la
   branche, un secret S3 et le réglage `iceberg_use_metadata_log`. Esquisse (syntaxe dbt-duckdb à
   vérifier) :

   ```yaml
   extensions: [httpfs, iceberg]
   settings:
     iceberg_use_metadata_log: false
   secrets:
     - type: s3
       key_id: minioadmin
       secret: 8qqR90Az
       endpoint: localhost:29000
       url_style: path
       use_ssl: false
       region: us-east-1
   attach:
     - path: warehouse
       alias: lake
       type: iceberg
       options:
         endpoint: "http://localhost:19120/iceberg/{{ env_var('NESSIE_BRANCH', 'main') }}"
         authorization_type: none
   ```

3. **Sources et modèles.**
   - `sources.yml` : la source `raw` pointe sur `lake.raw` (`database: lake`), plus de `meta.plugin`.
   - `daily_orders` : matérialisation `table` dans `lake.marts` au lieu de `external` + plugin.
   - **Risque principal** : la matérialisation `table` de dbt-duckdb recrée la table à chaque run
     (création d'une table temporaire puis renommage, ou `CREATE OR REPLACE`). L'extension Iceberg ne
     supporte pas `CREATE OR REPLACE`, et le renommage n'est pas testé. Plan B : un modèle
     `incremental` (stratégie `delete+insert`), ou une matérialisation maison qui fait `DROP` puis
     `CREATE TABLE AS`.

4. **Nettoyage.** Si tout passe : supprimer `src/nessie_demo/dbt_plugins/`. `catalog.py` et PyIceberg
   restent utiles pour l'ingestion et la sortie narrée (nombre de lignes lu dans les métadonnées), sauf
   à les réécrire aussi en DuckDB.

5. **Slides.** La slide 05 devient « ce qu'on faisait avant DuckDB 2.0 », ou disparaît ; la slide
   « Maturité » passe DuckDB en « Mature (≥ 2.0) ».

## À ne pas faire ce soir

Garder la démo de la présentation sur DuckDB 1.4.3 et le contournement : il est testé et validé.
Faire ces essais sur une branche git à part.
