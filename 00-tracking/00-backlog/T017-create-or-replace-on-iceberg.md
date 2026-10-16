# T017 Decide where to record that DuckDB's Iceberg extension refuses CREATE OR REPLACE

DuckDB's Iceberg extension doesn't support `CREATE OR REPLACE TABLE` on an attached Iceberg catalog ([duckdb/duckdb-iceberg#784](https://github.com/duckdb/duckdb-iceberg/issues/784), "Feature: Support Create or replace table", open on 2026-10-16). Replacing a table takes `DROP TABLE` then `CREATE TABLE … AS`, which isn't atomic: the table doesn't exist between the two, and it makes two commits on the Nessie branch. Observed on 2026-10-15 with the pre-release `2.0.0.dev2610011535` (test in T001).

It doesn't block T001: dbt-duckdb's `table` materialization creates a temporary table and renames it, without `CREATE OR REPLACE`. It can matter later: a custom materialization, a script or a notebook that replaces a table, or a dbt-duckdb version that starts issuing `CREATE OR REPLACE`.

Decide what to do with this information: where to record it (a concepts or project doc on DuckDB and Iceberg, the materialization doc T001 produces, an ADR, nowhere), and how to notice when #784 is fixed.

## Notes

- The issue status is dated: re-check #784 before refining.
