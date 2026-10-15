"""PyIceberg catalog access, always scoped to a Nessie branch (the branch is in the REST URI)."""

from __future__ import annotations

import pyarrow as pa
import pyarrow.compute as pc
from pyiceberg.catalog import Catalog, load_catalog
from pyiceberg.exceptions import NamespaceAlreadyExistsError, NoSuchTableError

from .settings import settings


def branch_catalog(branch: str) -> Catalog:
    return load_catalog(f"nessie_{branch}", **settings.pyiceberg_props(branch))


def ensure_namespace(catalog: Catalog, namespace: str) -> None:
    try:
        catalog.create_namespace(namespace)
    except NamespaceAlreadyExistsError:
        pass


def overwrite_table(catalog: Catalog, identifier: str, data: pa.Table) -> None:
    """Create the table if missing (schema inferred from Arrow), then replace its contents."""
    namespace = identifier.split(".")[0]
    ensure_namespace(catalog, namespace)
    try:
        table = catalog.load_table(identifier)
    except NoSuchTableError:
        table = catalog.create_table(identifier, schema=data.schema)
    table.overwrite(data)


def append_table(catalog: Catalog, identifier: str, data: pa.Table) -> None:
    """Create the table if missing (schema inferred from Arrow), then append rows."""
    namespace = identifier.split(".")[0]
    ensure_namespace(catalog, namespace)
    try:
        table = catalog.load_table(identifier)
    except NoSuchTableError:
        table = catalog.create_table(identifier, schema=data.schema)
    table.append(data)


def column_max(catalog: Catalog, identifier: str, column: str) -> int:
    """Max value of an integer column, or 0 if the table doesn't exist / is empty.

    Used to continue order_id across appends so it stays globally unique.
    """
    try:
        table = catalog.load_table(identifier)
    except NoSuchTableError:
        return 0
    arrow = table.scan(selected_fields=(column,)).to_arrow()
    if arrow.num_rows == 0:
        return 0
    return int(pc.max(arrow[column]).as_py() or 0)


def row_count(catalog: Catalog, identifier: str) -> int | None:
    """Row count read from the Iceberg snapshot summary (metadata only, no data file read).
    None if the table doesn't exist on this branch."""
    try:
        snapshot = catalog.load_table(identifier).current_snapshot()
    except NoSuchTableError:
        return None
    if snapshot is None or snapshot.summary is None:
        return 0
    return int(snapshot.summary.get("total-records", 0))
