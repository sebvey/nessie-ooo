# T023 A data explorer that doesn't modify its own file

`mise run notebook` opens `notebooks/explore.mo.py` with `marimo edit`. To explore the data, you edit the SQL cell, and marimo saves the query into the notebook file: every exploration leaves a diff in git (seen on 2026-10-16: the default `SELECT * FROM lake.raw.orders where amount < 0` became `SELECT * FROM lake.raw.orders`). What we want: a data explorer on a Nessie branch, with a default query, where using it never changes the file.

First decide whether marimo is the right tool for that; if it isn't, consider something else.

## Notes

Leads, not checked:

- **Stay on marimo**: keep the code fixed and put the query in a UI element (a `mo.ui.code_editor` or `mo.ui.text_area` with the default query, its value fed to `mo.sql`), whose state isn't written to the `.py` file; and/or open the notebook with `marimo run` (app mode: code read-only) instead of `marimo edit`. Check what marimo saves in each mode, and the `notebooks/__marimo__/` session files.
- **Something else**: the DuckDB UI (`CALL start_ui()`, a local web SQL editor, to check how it fits with an `ATTACH` done in Python), a terminal SQL client such as Harlequin, or a plain DuckDB CLI session with the `ATTACH` pre-run.
- Whatever the tool, it keeps the branch picker and goes through `src/nessie_demo/lake.py` (DuckDB with the branch's catalog attached as `lake`, since T001).
- Re-check versions and features against current docs before deciding: these leads are from memory.
