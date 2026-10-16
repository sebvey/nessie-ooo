"""DuckDB access to the Iceberg tables of a Nessie branch: the catalog is attached as `lake`.

Reads tables that DuckDB wrote (the dbt marts): PyIceberg doesn't apply the position delete files
DuckDB writes when it replaces a table's rows, so it would count the deleted rows too.
"""

from __future__ import annotations

from urllib.parse import urlparse

import duckdb

from .settings import settings


def branch_lake(branch: str) -> duckdb.DuckDBPyConnection:
    """In-memory DuckDB connection with the Nessie catalog of `branch` attached read-only as `lake`."""
    con = duckdb.connect()
    con.sql("INSTALL httpfs; LOAD httpfs; INSTALL iceberg; LOAD iceberg")
    con.sql(f"""
        CREATE SECRET (TYPE s3, KEY_ID '{settings.s3_access_key}', SECRET '{settings.s3_secret_key}',
            ENDPOINT '{urlparse(settings.s3_endpoint).netloc}', URL_STYLE 'path', USE_SSL false,
            REGION '{settings.s3_region}')
    """)
    con.sql(f"""
        ATTACH 'warehouse' AS lake (TYPE iceberg, AUTHORIZATION_TYPE 'none', READ_ONLY,
            ENDPOINT '{settings.nessie_iceberg_uri}/{branch}')
    """)
    return con
