import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    from lakehouse_client.lake import branch_lake
    from lakehouse_client.nessie import Nessie

    return Nessie, branch_lake, mo


@app.cell(hide_code=True)
def _(Nessie, mo):
    _branches = sorted(r["name"] for r in Nessie().list_branches() if r["type"] == "BRANCH")
    branch = mo.ui.dropdown(
        options=_branches,
        value="main" if "main" in _branches else _branches[0],
        label="Nessie branch",
    )
    branch
    return (branch,)


@app.cell(hide_code=True)
def _(branch, branch_lake, mo):
    # The branch's Nessie catalog, attached as the `lake` database: query its tables as
    # lake.<namespace>.<table> (e.g. lake.raw.orders). DuckDB reads the Parquet files from Silo at
    # query time, without loading anything in advance.
    con = branch_lake(branch.value)
    _tables = []
    for _ns, _name in con.sql(
        "SELECT schema_name, table_name FROM duckdb_tables() WHERE database_name = 'lake' ORDER BY ALL"
    ).fetchall():
        # Not duckdb_tables().column_count: the Iceberg extension only loads a table's schema on use.
        _table = f"lake.{_ns}.{_name}"
        _tables.append({
            "table": _table,
            "rows": con.sql(f"SELECT count(*) FROM {_table}").fetchall()[0][0],
            "columns": len(con.sql(f"FROM {_table}").columns),
        })

    mo.vstack([
        mo.md(f"**{len(_tables)} table(s)** on branch `{branch.value}`"),
        mo.ui.table(_tables, selection=None) if _tables else mo.md("_No table on this branch._"),
    ])
    return (con,)


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT * FROM lake.raw.orders where amount < 0
        """,
        engine=con
    )
    return


if __name__ == "__main__":
    app.run()
