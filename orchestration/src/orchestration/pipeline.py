"""The demo pipeline orchestrator.

Flow:
  0. starting point: where main is, how many rows it holds (main is prepared by `mise run stack-up`)
  1. open branch  pipeline-ok|ko-HHMMSS  from main     (Nessie API)
  2. ingest raw orders onto the branch                 (PyIceberg)
  3. dbt build  = run transforms + run tests           (dbt + DuckDB)
  4. tests green -> merge branch into main + tag       (Nessie API, atomic)
     tests red   -> DO NOT merge, alert, keep branch   (for inspection)

The console output is the support of the live talk: one block per step, with a pause between
steps (Enter) so the presenter can explain what just happened.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

import duckdb
from ingestion.ingest import RAW_TABLE, ingest
from lakehouse_client.catalog import branch_catalog, row_count
from lakehouse_client.lake import branch_lake
from lakehouse_client.nessie import Nessie
from lakehouse_client.settings import settings

from . import display
from .alert import alert
from .display import check, line, rows, short, step

REPO_ROOT = Path(__file__).resolve().parents[3]
DBT_DIR = REPO_ROOT / "transformation"
MAIN = settings.main_branch
MART_TABLE = "marts.daily_orders"

# How dbt nodes read on screen.
MODEL_LABELS = {
    "stg_orders": ("stg_orders", "DuckDB view"),
    "daily_orders": ("daily_orders", "Iceberg table written on the branch"),
}
TEST_LABELS = {
    "not_null_stg_orders_order_id": "order_id not null",
    "unique_stg_orders_order_id": "order_id unique",
    "not_null_stg_orders_customer_id": "customer_id not null",
    "assert_amount_non_negative": "amount ≥ 0",
    "not_null_daily_orders_order_date": "order_date not null",
    "unique_daily_orders_order_date": "order_date unique",
}


def run_dbt(branch: str, verbose: bool = False) -> bool:
    """Run `dbt build` (run + test) on `branch`, print a per-node summary. True if all green."""
    cmd = ["dbt", "build", "--project-dir", str(DBT_DIR), "--profiles-dir", str(DBT_DIR)]
    if not verbose:
        cmd.insert(1, "--quiet")
    line(f"[dim]$ NESSIE_BRANCH={branch} dbt build")
    result = subprocess.run(
        cmd,
        env={**os.environ, "NESSIE_BRANCH": branch},
        cwd=str(REPO_ROOT),
        capture_output=not verbose,
        text=True,
    )

    results_file = DBT_DIR / "target" / "run_results.json"
    if result.returncode not in (0, 1) or not results_file.exists():
        # dbt itself crashed (not a test failure): show what it said.
        line("[bold red]dbt failed before the end of the build:")
        display.console.print(result.stdout or "", result.stderr or "")
        return False

    results = json.loads(results_file.read_text())["results"]
    n_ok = 0
    for r in results:
        kind, name = r["unique_id"].split(".")[0], r["unique_id"].split(".")[2]
        status = r["status"]
        ok = {"success": True, "pass": True, "skipped": None}.get(status, False)
        n_ok += ok is True
        if kind == "model":
            label, detail = MODEL_LABELS.get(name, (name, ""))
            if ok is None:
                detail = "not built: upstream tests failed"
            check(ok, label, detail)
        else:
            label = "  " + TEST_LABELS.get(name, name)
            detail = f"{r['failures']} failing row(s)" if ok is False and r.get("failures") else ""
            check(ok, label, detail)
    colour = "green" if n_ok == len(results) else "red"
    line(f"[bold {colour}]{n_ok}/{len(results)} OK")
    return result.returncode == 0


def mart(branch: str) -> str:
    """daily_orders aggregates by day, so its row count barely moves: show days + orders instead.

    Read with DuckDB, which wrote the table (see lake.py)."""
    try:
        days, orders = branch_lake(branch).sql(f"SELECT count(*), sum(n_orders) FROM lake.{MART_TABLE}").fetchall()[0]
    except duckdb.CatalogException:
        return "doesn't exist yet"
    return f"{days} day{'s' if days > 1 else ''}, {orders} order{'s' if orders > 1 else ''}"


def tables(branch: str) -> list[str]:
    """State of both tables of the demo on a branch, one line per table."""
    return [
        f"{RAW_TABLE:<19} {rows(row_count(branch_catalog(branch), RAW_TABLE))}",
        f"{MART_TABLE:<19} {mart(branch)}",
    ]


def run_pipeline(ko: bool = False, keep: bool = False, verbose: bool = False) -> int:
    nessie = Nessie()
    branch = f"pipeline-{'ko' if ko else 'ok'}-{datetime.now():%H%M%S}"
    main_catalog = branch_catalog(MAIN)

    display.header(f"Pipeline Nessie · {branch}")

    # --- 0. starting point
    step(0, "Starting point", "Nessie API")
    main_before = nessie.ref_hash(MAIN)
    if main_before == nessie.no_ancestor_hash():
        # A main without history can't be a merge target ("No common ancestor").
        line("[bold red]main has no commit yet: run `mise run stack-up` first.")
        return 2
    line(f"main @ [bold]{short(main_before)}[/]")
    for t in tables(MAIN):
        line(t)

    # --- 1. branch
    step(1, "Opening a branch for the pipeline", "Nessie API")
    if nessie.branch_exists(branch):
        nessie.delete_branch(branch)
    nessie.create_branch(branch, from_ref=MAIN)
    line(f"[bold]{branch}[/] created from main @ {short(main_before)}")
    line("[dim]no data copied: a new pointer to the same commit")

    # --- 2. ingest
    step(2, "Ingesting orders onto the branch", "PyIceberg")
    data = ingest(branch, ko=ko)
    line(f"+{data.num_rows} orders in {RAW_TABLE}" + (" [bold red](some of them dirty)" if ko else ""))
    display.orders_table(data)
    branch_rows = row_count(branch_catalog(branch), RAW_TABLE)
    main_rows = row_count(main_catalog, RAW_TABLE)
    line(f"{RAW_TABLE}: branch = [bold]{rows(branch_rows)}[/] · main = {rows(main_rows)} [dim](unchanged)")
    line(f"[dim]{branch} @ {short(nessie.ref_hash(branch))} (+1 commit) · main @ {short(nessie.ref_hash(MAIN))}")

    # --- 3. dbt build
    step(3, "Transforming and testing the branch", "dbt + DuckDB")
    ok = run_dbt(branch, verbose=verbose)
    if ok:
        line(f"{MART_TABLE}: branch = [bold]{mart(branch)}[/] · main = {mart(MAIN)} [dim](unchanged)")

    # --- 4. decide
    if ok:
        step(4, "Merging into main and tagging (tests green)", "Nessie API")
        nessie.merge(branch, into=MAIN)
        main_after = nessie.ref_hash(MAIN)
        line(f"merge {branch} → main     main: {short(main_before)} → [bold]{short(main_after)}")
        tag = f"release-{datetime.now():%H%M%S}"  # HHMMSS -> a distinct tag per run
        if nessie.branch_exists(tag):  # same-second re-run -> move the tag to the new state
            nessie.delete_tag(tag)
        nessie.create_tag(tag, from_ref=MAIN)
        line(f"tag [bold]{tag}[/] → {short(main_after)} [dim](marks this release)")
        if keep:
            line(f"branch {branch} kept (--keep)")
        else:
            nessie.delete_branch(branch)
            line(f"branch {branch} deleted")
        display.pause("Summary")
        display.success("main updated", tables(MAIN))
        return 0

    step(4, "No merge, branch kept (tests red)", "Nessie API")
    main_now = nessie.ref_hash(MAIN)
    unchanged = "unchanged" if main_now == main_before else "[bold red]moved![/]"
    line(f"main @ [bold]{short(main_now)}[/] ({unchanged})")
    for t in tables(MAIN):
        line(t)
    line(f"branch [bold]{branch}[/] kept for investigation")
    display.pause("Alert")
    display.console.print()
    alert(
        title=f"Pipeline failed on {branch}",
        message=(
            f"dbt tests red: the bad data stays isolated on its branch.\n"
            f"Nothing was merged into {MAIN}.\n\n"
            f"To investigate: mise run dbt-inspect {branch}"
        ),
    )
    display.failure("main stayed clean: the bad data never touched it")
    return 1


def main() -> None:
    p = argparse.ArgumentParser(description="Run the Nessie branch->test->merge demo pipeline.")
    p.add_argument("--ko", action="store_true", help="ingest dirty data so tests fail (no merge)")
    p.add_argument("--keep", action="store_true", help="keep the branch even on success")
    p.add_argument("--no-pause", action="store_true", help="don't wait for Enter between steps")
    p.add_argument("--verbose", action="store_true", help="show the raw dbt output")
    args = p.parse_args()
    display.PAUSE = not args.no_pause
    raise SystemExit(run_pipeline(ko=args.ko, keep=args.keep, verbose=args.verbose))


if __name__ == "__main__":
    main()
