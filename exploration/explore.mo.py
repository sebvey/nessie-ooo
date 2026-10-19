import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    from lakehouse_client.lake import attach_branches, lake_connection
    from lakehouse_client.nessie import Nessie

    return Nessie, attach_branches, lake_connection, mo


@app.cell(hide_code=True)
def _(mo):
    # The selection survives a refresh of the branch list.
    get_selected, set_selected = mo.state(["main"])
    refresh = mo.ui.button(label="Refresh branches")
    return get_selected, refresh, set_selected


@app.cell(hide_code=True)
def _(Nessie, get_selected, mo, refresh, set_selected):
    refresh  # re-run on click: re-read the branches from Nessie
    _branches = sorted(r["name"] for r in Nessie().list_branches() if r["type"] == "BRANCH")
    selector = mo.ui.multiselect(
        options=_branches,
        value=[b for b in get_selected() if b in _branches],
        label="Nessie branches",
        on_change=set_selected,
    )
    mo.hstack([selector, refresh], justify="start")
    return (selector,)


@app.cell(hide_code=True)
def _(attach_branches, lake_connection, mo, selector):
    # Each selected branch's Nessie catalog, attached read-only as lake_<branch> (dashes and other
    # characters become `_`). Its tables and columns show in the Data sources panel; query them as
    # lake_<branch>.<namespace>.<table>. DuckDB reads the Parquet files from Silo at query time.
    mo.stop(not selector.value, mo.md("_Select at least one branch._"))
    con = lake_connection()
    _aliases = attach_branches(con, selector.value)
    mo.md("  \n".join(f"`{_alias}`: branch `{_branch}`" for _alias, _branch in _aliases.items()))
    return (con,)


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT * FROM lake_main.raw.orders WHERE amount < 0
        """,
        engine=con
    )
    return


if __name__ == "__main__":
    app.run()
