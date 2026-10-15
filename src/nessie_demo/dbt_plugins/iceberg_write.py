"""dbt-duckdb plugin: materialize a model as an Iceberg table on a Nessie branch (via PyIceberg).

Used by models with `materialized='external', plugin='iceberg_write'`. The branch lives in the
`uri` passed from profiles.yml (e.g. .../iceberg/{{ env_var('NESSIE_BRANCH') }}), so every write
lands on the pipeline branch — never on main directly.
"""

from __future__ import annotations

import warnings
from typing import Any, Dict

import pyarrow as pa
from pyiceberg.catalog import load_catalog
from pyiceberg.exceptions import NamespaceAlreadyExistsError, NoSuchTableError

from dbt.adapters.duckdb.plugins import BasePlugin
from dbt.adapters.duckdb.plugins.pd_utils import target_to_df
from dbt.adapters.duckdb.utils import TargetConfig


class Plugin(BasePlugin):
    def initialize(self, config: Dict[str, Any]):
        name = config.pop("catalog", "nessie")
        self._catalog = load_catalog(name, **config)

    def store(self, target_config: TargetConfig):
        rel = target_config.relation
        namespace = "marts"
        identifier = f"{namespace}.{rel.identifier}"

        df = target_to_df(target_config)
        arrow = pa.Table.from_pandas(df, preserve_index=False)

        try:
            self._catalog.create_namespace(namespace)
        except NamespaceAlreadyExistsError:
            pass
        try:
            table = self._catalog.load_table(identifier)
        except NoSuchTableError:
            table = self._catalog.create_table(identifier, schema=arrow.schema)
        # Le modèle a gagné des colonnes : on les ajoute au schéma Iceberg (commit sur la branche).
        with table.update_schema() as update:
            update.union_by_name(arrow.schema)
        with warnings.catch_warnings():
            # 1er run : overwrite sur une table vide -> "Delete operation did not match any records".
            warnings.filterwarnings("ignore", message="Delete operation did not match any records")
            table.overwrite(arrow)
