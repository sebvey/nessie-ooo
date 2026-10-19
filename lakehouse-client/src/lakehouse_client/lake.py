"""DuckDB access to the Iceberg tables of Nessie branches: each branch's catalog is an attached database.

Reads tables that DuckDB wrote (the dbt marts) with the engine that wrote them, position delete files
included.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

import duckdb

from .settings import settings


def lake_connection() -> duckdb.DuckDBPyConnection:
    """In-memory DuckDB connection with the Iceberg extensions and the Silo secret, no catalog attached."""
    con = duckdb.connect()
    con.sql("INSTALL httpfs; LOAD httpfs; INSTALL iceberg; LOAD iceberg")
    con.sql(f"""
        CREATE SECRET (TYPE s3, KEY_ID '{settings.s3_access_key}', SECRET '{settings.s3_secret_key}',
            ENDPOINT '{urlparse(settings.s3_endpoint).netloc}', URL_STYLE 'path', USE_SSL false,
            REGION '{settings.s3_region}')
    """)
    return con


def attach_branch(con: duckdb.DuckDBPyConnection, branch: str, alias: str) -> None:
    """Attach the Nessie catalog of `branch` read-only as the database `alias`."""
    con.sql(f"""
        ATTACH 'warehouse' AS "{alias}" (TYPE iceberg, AUTHORIZATION_TYPE 'none', READ_ONLY,
            ENDPOINT '{settings.nessie_iceberg_uri}/{branch}')
    """)


def lake_alias(branch: str) -> str:
    """Database name for `branch`: `lake_` and the branch name, every character other than a letter, a
    digit or `_` replaced by `_` (`pipeline-ko-1` -> `lake_pipeline_ko_1`). Prefixed because DuckDB
    reserves `main` as a database name; usable without quotes."""
    return "lake_" + re.sub(r"[^0-9A-Za-z_]", "_", branch)


def attach_branches(con: duckdb.DuckDBPyConnection, branches: list[str]) -> dict[str, str]:
    """Attach each branch read-only as `lake_alias(branch)`. Returns {alias: branch}."""
    aliases: dict[str, str] = {}
    for branch in branches:
        alias = lake_alias(branch)
        if alias in aliases:
            raise ValueError(f"Branches {aliases[alias]!r} and {branch!r} both map to the database name {alias!r}")
        aliases[alias] = branch
    for alias, branch in aliases.items():
        attach_branch(con, branch, alias)
    return aliases


def branch_lake(branch: str) -> duckdb.DuckDBPyConnection:
    """In-memory DuckDB connection with the Nessie catalog of `branch` attached read-only as `lake`."""
    con = lake_connection()
    attach_branch(con, branch, "lake")
    return con
