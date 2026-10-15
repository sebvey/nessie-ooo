import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import duckdb
    import marimo as mo

    from nessie_demo.catalog import branch_catalog
    from nessie_demo.nessie import Nessie

    return Nessie, branch_catalog, duckdb, mo


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
def _(branch, branch_catalog, duckdb, mo):
    # Toutes les tables de la branche, chargées en mémoire dans DuckDB sous le nom
    # <namespace>_<table> (ex. raw.orders -> raw_orders).
    _catalog = branch_catalog(branch.value)
    con = duckdb.connect()
    _loaded = []
    for _ns in _catalog.list_namespaces():
        for _ident in _catalog.list_tables(_ns):
            _arrow = _catalog.load_table(_ident).scan().to_arrow()
            _name = "_".join(_ident)
            con.register(_name, _arrow)
            _loaded.append({"table": _name, "lignes": _arrow.num_rows, "colonnes": _arrow.num_columns})

    mo.vstack([
        mo.md(f"**{len(_loaded)} table(s)** chargée(s) depuis la branche `{branch.value}`"),
        mo.ui.table(_loaded, selection=None) if _loaded else mo.md("_Aucune table sur cette branche._"),
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
