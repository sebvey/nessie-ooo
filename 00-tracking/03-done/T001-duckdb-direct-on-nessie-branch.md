# T001 DuckDB reads and writes Iceberg directly on a Nessie branch

DuckDB would read and write directly on a Nessie branch (`ATTACH` with the branch in the catalog URI), without the PyIceberg detour described in [architecture](../../docs/project/architecture.md#why-pyiceberg-and-not-duckdb-directly) and [ADR003](../../docs/adr/ADR003-pyiceberg-as-the-data-plane.md). The fix (duckdb-iceberg#1230) won't be in a stable release before DuckDB 2.0. This is a POC: a DuckDB 2.0 pre-release is acceptable.

Scope: the dbt project and the notebook move to DuckDB. PyIceberg stays for ingestion and for the row counts in `catalog.py`. The slides are out of scope.

## Acceptance criteria

- [x] `duckdb` is `>=2.0`, a pre-release if 2.0 isn't out yet, and `mise run audit-python` passes. (`2.0.0.dev2610151406`; audit: no vulnerability in 111 packages.)
- [x] `uv run pipeline --no-pause` merges; `uv run pipeline --bad --no-pause` doesn't merge and `main` is unchanged. (On the existing stack, without `stack-reset`: `main` already had `daily_orders`. The path where the table doesn't exist yet was checked apart, see the next criteria.)
- [x] dbt reads `raw.orders` and writes `marts.daily_orders` through an `ATTACH` on the branch, with no dbt plugin; `src/nessie_demo/dbt_plugins/` is deleted.
- [x] Two `dbt build` in a row on the same branch both succeed, and the second replaces the model's data. (On a throwaway branch after dropping `daily_orders`: `Create ICEBERG_TABLE` then `Update ICEBERG_TABLE`, the counts match `raw.orders`. `table` fails, so the marts are `incremental` with a `replace` strategy of ours.)
- [x] The notebook reads the selected branch through an `ATTACH`. (Run headless on `main` and its table listing on another branch; the marimo UI wasn't opened.)
- [x] A new ADR (status `proposed`) supersedes ADR003; `architecture.md` describes the new data path. (ADR004.)
- [x] A doc in `docs/` explains how dbt-duckdb's `table` and `incremental` materializations run on an attached Iceberg catalog: the SQL statements issued, and the Nessie commits each run leaves on the branch. (`docs/project/dbt-on-iceberg.md`; built-in `append` and `delete+insert` and `--full-refresh` not tried.)
- [x] A backlog ticket exists to update the slides (slide 05 "Le détour par PyIceberg", the "Maturité" slide, the PyIceberg and plugin cards). (T018.)
- [x] If DuckDB 2.0 stable isn't out when the ticket closes: a backlog ticket exists to move from the pre-release to the stable release. (T019; 2.0 not out on 2026-10-16.)

## Notes

- **Facts re-checked on 2026-10-16**: latest stable DuckDB is 1.5.6; 2.0.0 is planned for 2026-10-21 and 2.0.1 for 2026-11-18 (duckdb.org release calendar, tentative dates); duckdb-iceberg#1230 merged on 2026-07-26; #784 still open; dbt-duckdb 1.11.0 requires `duckdb>=1.0.0` with no upper bound (whether it works with 2.0 is not tested).
- **Materialization** (quick look, 2026-10-16: dbt-duckdb macros read in `.venv`, nothing run on Iceberg). dbt-duckdb's `table` materialization never issues `CREATE OR REPLACE`: it runs `create table <model>__dbt_tmp as …`, renames the existing table to `<model>__dbt_backup`, renames the temporary table to the model, commits, then drops the backup. So duckdb-iceberg#784 doesn't block it; what is untested is `ALTER TABLE … RENAME` on an Iceberg table through Nessie's REST catalog (needed from the first run) and `BEGIN`/`COMMIT` around several statements. Each statement likely becomes a Nessie commit (about 4 per run), a noisier `SHOW LOG` than today. First step of the ticket: test `RENAME`. If it works, keep `table`; otherwise, `incremental` with `delete+insert` (its intermediate table is a local DuckDB temporary table; `DELETE` and `INSERT` are tested), or a custom `DROP` + `CREATE AS` materialization. The `CREATE OR REPLACE` limitation itself is tracked in T017. **Result (2026-10-16, tested)**: a rename alone works, but dbt-duckdb runs its renames inside a transaction with the table creation, which the REST catalog refuses; `table` fails from the first run. Details in `docs/project/dbt-on-iceberg.md`.
- **Configuration as-is**: credentials and endpoints stay where they are today (hardcoded in `dbt/profiles.yml`). Moving them out is [T006](../00-backlog/T006-configuration-and-secrets.md); the rest of the dbt clean-up is [T004](../00-backlog/T004-refactor-dbt-project.md). T001 comes first, and T004 no longer has to decide the `iceberg_write` plugin's future.

### Status (tests of 2026-10-15)

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

### Reproduce the test (5 minutes)

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

### Integration plan

Nothing below is tested. Suggested order, each step validated before the next. Step 6 is out of scope (follow-up ticket).

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
   - **Main risk**: the materialization, see the Materialization note above.

4. **Notebook.** Replace the `iceberg_scan` views with a single `ATTACH` on the selected branch.

5. **Cleanup.** If everything passes, delete `src/nessie_demo/dbt_plugins/`. `catalog.py` and PyIceberg stay useful for ingestion and the narrated output (row counts from metadata), unless rewritten in DuckDB too.

6. **Slides.** Slide 05 ("Le détour par PyIceberg") becomes "what we did before DuckDB 2.0", or goes; the "Maturité" slide moves DuckDB to "Mature (≥ 2.0)".

## Outcome

- dbt attaches the branch's Nessie catalog as `lake` (`dbt/profiles.yml`: `iceberg` extension, S3 secret, `iceberg_use_metadata_log = false`). Sources read `lake.raw`; `stg_orders` stays a view in dbt's local DuckDB file (the catalog has no views); `daily_orders` is `incremental` with a `replace` strategy of ours (`dbt/macros/incremental_replace.sql`: delete then insert by name, one transaction, one Nessie commit per run). `dbt/macros/generate_schema_name.sql` keeps the `marts` namespace as is. The `config(location = …)` of `daily_orders.sql` is gone.
- `src/nessie_demo/dbt_plugins/` deleted. New `src/nessie_demo/lake.py` (DuckDB with the branch's catalog attached read-only); the pipeline reads `daily_orders` through it, and the notebook lists and queries `lake.<namespace>.<table>`.
- `duckdb>=2.0.0.dev2610151406` (pre-release, picked by uv's default pre-release rule since the specifier names one); audit clean.
- Findings: dbt-duckdb's `table` materialization fails (the REST catalog refuses a transaction mixing a table creation with renames); the extension can't create views; PyIceberg 0.10 doesn't apply the position delete files DuckDB writes, so marts must be read with DuckDB; `relation.fetchone()` is gone in DuckDB 2.0.
- ADR004 accepted, supersedes ADR003. New doc `docs/project/dbt-on-iceberg.md`; `architecture.md`, `pipeline.md`, `README.md` and the indexes updated. T004 notes updated (plugin and `location` gone).
- Follow-ups: T017 (`CREATE OR REPLACE`), T018 (slides), T019 (DuckDB 2.0 stable), T020 (PyIceberg and DuckDB delete files), T021 (`NESSIE_BRANCH` overridden by mise).
- Left aside: the full end-to-end check with `stack-reset` (the stack held refs not created in this session); both pipelines ran on the existing stack, and they left a merge and the tag `release-165844` on `main`.
- Not verified: `stack-reset` then a first pipeline run from an empty `main` (the create path was checked on a branch after dropping the table); the marimo UI (notebook run headless only); the built-in `append` and `delete+insert` strategies and `--full-refresh`; dbt-duckdb 1.11.0 (1.10.1 stays locked).
