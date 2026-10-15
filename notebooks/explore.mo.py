import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    from nessie_demo.nessie import Nessie
    from pyiceberg.catalog.rest import RestCatalog

    return Nessie, RestCatalog, mo


@app.cell
def _(Nessie, mo):
    _nessie = Nessie()
    _branches = [r["name"] for r in _nessie.list_branches() if r["type"] == "BRANCH"]
    branch = mo.ui.dropdown(
        options=sorted(_branches),
        value="main" if "main" in _branches else (_branches[0] if _branches else None),
        label="Branche Nessie",
    )
    branch
    return (branch,)


@app.cell
def _(RestCatalog, branch):


    catalog = RestCatalog(
        "nessie",
        **{
            "uri": f"http://localhost:19120/iceberg/{branch.value}",
            "warehouse": "s3://iceberg-warehouse",
            "s3.endpoint": "http://localhost:29000",
            "s3.access-key-id": "minioadmin",
            "s3.secret-access-key": "8qqR90Az",
            "s3.region": "us-east-1",
            "s3.path-style-access": "true",
        },
    )
    catalog
    return (catalog,)


@app.cell
def _(catalog):
    # load_table() renvoie un objet catalogue pyiceberg ;
    # .scan().to_arrow() matérialise en pyarrow Table, que DuckDB sait scanner.
    raw__orders = catalog.load_table("raw.orders").scan().to_arrow()
    marts__daily_orders = catalog.load_table("marts.daily_orders").scan().to_arrow()
    return marts__daily_orders, raw__orders


@app.cell
def _(mo, raw__orders):
    _df = mo.sql(
        f"""
        SELECT *
        FROM raw__orders
        --WHERE amount < 0;
        """
    )
    return


@app.cell
def _(marts__daily_orders, mo):
    _df = mo.sql(
        f"""
        SELECT * FROM marts__daily_orders;
        """
    )
    return


if __name__ == "__main__":
    app.run()
