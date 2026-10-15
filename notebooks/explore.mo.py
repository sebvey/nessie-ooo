import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    from urllib.parse import urlparse

    import duckdb
    import marimo as mo

    from nessie_demo.catalog import branch_catalog
    from nessie_demo.nessie import Nessie
    from nessie_demo.settings import settings

    return Nessie, branch_catalog, duckdb, mo, settings, urlparse


@app.cell(hide_code=True)
def _(Nessie, mo):
    _branches = sorted(r["name"] for r in Nessie().list_branches() if r["type"] == "BRANCH")
    branch = mo.ui.dropdown(
        options=_branches,
        value="main" if "main" in _branches else _branches[0],
        label="Branche Nessie",
    )
    branch
    return (branch,)


@app.cell(hide_code=True)
def _(branch, branch_catalog, duckdb, mo, settings, urlparse):
    # Une vue DuckDB par table de la branche, nommée <namespace>_<table> (ex. raw.orders -> raw_orders).
    # Nessie ne donne que le pointeur (le metadata.json courant de chaque table) ; DuckDB lit les
    # fichiers Parquet dans Silo au moment de la requête, sans rien charger à l'avance.
    con = duckdb.connect()
    con.sql("INSTALL httpfs; LOAD httpfs; INSTALL iceberg; LOAD iceberg")
    con.sql(f"""
        CREATE SECRET (TYPE s3, KEY_ID '{settings.s3_access_key}', SECRET '{settings.s3_secret_key}',
            ENDPOINT '{urlparse(settings.s3_endpoint).netloc}', URL_STYLE 'path', USE_SSL false,
            REGION '{settings.s3_region}')
    """)

    _catalog = branch_catalog(branch.value)
    _views = []
    for _ns in _catalog.list_namespaces():
        for _ident in _catalog.list_tables(_ns):
            _table = _catalog.load_table(_ident)
            _name = "_".join(_ident)
            _snapshot = _table.current_snapshot()
            con.sql(f"CREATE VIEW {_name} AS SELECT * FROM iceberg_scan('{_table.metadata_location}')")
            _views.append({
                "vue": _name,
                "lignes": int(_snapshot.summary.get("total-records", 0)) if _snapshot else 0,
                "colonnes": len(_table.schema().fields),
                "metadata.json": _table.metadata_location.rsplit("/", 1)[-1],
            })

    mo.vstack([
        mo.md(f"**{len(_views)} table(s)** sur la branche `{branch.value}`"),
        mo.ui.table(_views, selection=None) if _views else mo.md("_Aucune table sur cette branche._"),
    ])
    return (con,)


@app.cell
def _(con, mo, raw_orders):
    _df = mo.sql(
        f"""
        SELECT * FROM raw_orders where amount < 0
        """,
        engine=con
    )
    return


if __name__ == "__main__":
    app.run()
