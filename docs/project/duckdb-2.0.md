# Dropping PyIceberg with DuckDB 2.0

Goal: DuckDB reads and writes **directly** on a Nessie branch (`ATTACH` with the branch in the catalog URI), without the PyIceberg detour described in [architecture](architecture.md#why-pyiceberg-and-not-duckdb-directly).

## Status (tests of 2026-10-15)

| Version | URL called | Result |
|---|---|---|
| DuckDB 1.5.6 (stable), `core` extension | `/iceberg/<br>/v1/<br>\|warehouse/…` | ❌ no table visible |
| DuckDB 1.5.6, `core_nightly` extension | same | ❌ (built from the 1.5 branch, without the fix) |
| DuckDB `2.0.0.dev2610011535` (PyPI pre-release, 2026-10-02) | `/iceberg/v1/<br>\|warehouse/…` | ✅ reads and writes on the branch |

The fix is [duckdb/duckdb-iceberg#1230](https://github.com/duckdb/duckdb-iceberg/pull/1230) ("Honor REST catalog URI overrides", merged on 2026-07-26 on `main`). It will only reach a stable release with DuckDB 2.0.

Operations tested on a throwaway branch (`main` untouched):

| Operation | Result |
|---|---|
| `SELECT` on `raw.orders` | ✅ |
| `CREATE TABLE … AS SELECT` | ✅ "Create ICEBERG_TABLE" commit on the branch |
| `INSERT`, `DELETE`, `DROP TABLE` | ✅ with `SET iceberg_use_metadata_log = false` (❌ otherwise) |
| `CREATE OR REPLACE TABLE` | ❌ not supported ([#784](https://github.com/duckdb/duckdb-iceberg/issues/784)): use `DROP` + `CREATE` |

## Reproduce the test (5 minutes)

Prerequisites: the stack is running (`mise run stack-up`) and `mise run pipeline-ok` ran at least once.

1. Create a throwaway branch from `main`:

```bash
mise run cli -c "CREATE BRANCH duckdb-probe FROM main;"
```

2. Save this script, for example as `/tmp/duckdb_probe.py`:

```python
import duckdb

c = duckdb.connect()
c.sql("INSTALL httpfs; LOAD httpfs; INSTALL iceberg; LOAD iceberg")
# Access to the Iceberg files in Silo
c.sql("""CREATE SECRET (TYPE s3, KEY_ID 'minioadmin', SECRET '8qqR90Az',
         ENDPOINT 'localhost:29000', URL_STYLE 'path', USE_SSL false, REGION 'us-east-1')""")
# Without this, any write after a table creation fails
# ("table metadata does not contain a metadata-log").
c.sql("SET iceberg_use_metadata_log = false")
# The branch is in the URL
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

3. Run it with the pre-release, without touching the project's environment:

```bash
uv run --isolated --no-project --prerelease allow --with duckdb==2.0.0.dev2610011535 python /tmp/duckdb_probe.py
```

4. Check the commits on the branch, and that `main` didn't move:

```bash
mise run cli -c "SHOW LOG ON BRANCH duckdb-probe;" -c "SHOW LOG ON BRANCH main;"
```

5. Clean up:

```bash
mise run cli -c "DROP BRANCH duckdb-probe;"
```

To see the URLs DuckDB calls, add `c.sql("CALL enable_logging('HTTP')")` after `LOAD iceberg`, then `c.sql("SELECT message FROM duckdb_logs WHERE type = 'HTTP'").fetchall()`.

## Plugging the demo into it

Nothing below is tested. Suggested order, each step validated before the next; do it on a separate git branch.

1. **Dependencies.** In `pyproject.toml`, pin `duckdb` to the pre-release (`duckdb==2.0.0.dev2610011535`) and allow pre-releases for uv (`[tool.uv] prerelease = "allow"`). Check first: **does dbt-duckdb accept DuckDB 2.0?** If `uv sync` or `dbt debug` fails, stop there.

2. **dbt profile** (`dbt/profiles.yml`). Replace both plugins with an `attach` on the branch URL, an S3 secret and the `iceberg_use_metadata_log` setting. Sketch (dbt-duckdb syntax to check):

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

3. **Sources and models.**
   - `sources.yml`: the `raw` source points to `lake.raw` (`database: lake`), no more `meta.plugin`.
   - `daily_orders`: `table` materialization in `lake.marts` instead of `external` + plugin.
   - **Main risk**: dbt-duckdb's `table` materialization recreates the table on every run (temporary table then rename, or `CREATE OR REPLACE`). The Iceberg extension doesn't support `CREATE OR REPLACE`, and rename isn't tested. Plan B: an `incremental` model (`delete+insert` strategy), or a custom materialization doing `DROP` then `CREATE TABLE AS`.

4. **Notebook.** Replace the `iceberg_scan` views with a single `ATTACH` on the selected branch.

5. **Cleanup.** If everything passes, delete `src/nessie_demo/dbt_plugins/`. `catalog.py` and PyIceberg stay useful for ingestion and the narrated output (row counts from metadata), unless rewritten in DuckDB too.

6. **Slides.** Slide 05 ("Le détour par PyIceberg") becomes "what we did before DuckDB 2.0", or goes; the "Maturité" slide moves DuckDB to "Mature (≥ 2.0)".
