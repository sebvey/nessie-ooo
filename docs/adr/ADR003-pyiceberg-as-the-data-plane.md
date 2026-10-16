# ADR003 PyIceberg is the data plane until DuckDB can read and write Iceberg on a Nessie branch

- Status: superseded by ADR004
- Date: 2026-10-15
- Tickets: T001
- Basis: investigated (tests of 2026-10-15, recorded in T001)
- Amended: 2026-10-16: the basis pointed to `docs/project/duckdb-2.0.md`, whose test results moved to T001

## Context

The demo works on Nessie branches: every read and write must target a branch, not only `main`. DuckDB's Iceberg extension can attach an Iceberg REST catalog, but up to DuckDB 1.5 it ignores the `overrides.uri` Nessie returns, so it only sees `main` (duckdb-iceberg#1145). The fix, duckdb-iceberg#1230, was merged on the extension's `main` branch on 2026-07-26 and will only ship with DuckDB 2.0. On 2026-10-15, DuckDB 1.5.6 fails on a branch; the pre-release `2.0.0.dev2610011535` reads and writes there, except `CREATE OR REPLACE TABLE` (duckdb-iceberg#784). The detour has been in place since the start of the project (December 2025); this ADR records it after the fact.

## Decision

PyIceberg talks to the Nessie catalog, with the branch in its URI:

- ingestion writes through PyIceberg;
- dbt-duckdb reads sources through its `iceberg` plugin (PyIceberg scan to Arrow) and writes models through `iceberg_write`; DuckDB only runs the SQL;
- the notebook gets each table's `metadata.json` from PyIceberg and reads it with DuckDB's `iceberg_scan`.

## Alternatives ruled out

- DuckDB attached to the REST catalog: only works on `main` before 2.0.
- DuckDB 2.0 pre-release: works on a branch, but a dev build in a live demo, and `CREATE OR REPLACE` still refused.
- A JVM engine (Spark, Trino): supports Nessie branches, but too heavy for a laptop demo.

## Consequences

- Two dbt plugins built on dbt-duckdb internals (`target_to_df`, `union_by_name`) to maintain; upgrades of dbt-duckdb or pyiceberg must be checked against them.
- Data goes through Arrow in Python memory: fine at demo scale, not beyond.
- The talk has to explain the detour.

## Revisit when

DuckDB 2.0 ships as a stable release with duckdb-iceberg#1230 and dbt-duckdb supports it: T001 then supersedes this ADR.
