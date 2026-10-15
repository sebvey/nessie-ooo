"""The demo pipeline orchestrator.

Flow:
  0. starting point: where main is, how many rows it holds (main is prepared by `mise run stack-up`)
  1. open branch  pipeline-HHMMSS  from main           (Nessie API)
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

from pyiceberg.exceptions import NoSuchTableError

from . import display
from .alert import alert
from .catalog import branch_catalog, row_count
from .display import check, line, rows, short, step
from .ingest import RAW_TABLE, ingest
from .nessie import Nessie
from .settings import settings

REPO_ROOT = Path(__file__).resolve().parents[2]
DBT_DIR = REPO_ROOT / "dbt"
MAIN = settings.main_branch
MART_TABLE = "marts.daily_orders"

# How dbt nodes read on screen.
MODEL_LABELS = {
    "stg_orders": ("stg_orders", "vue DuckDB"),
    "daily_orders": ("daily_orders", "table Iceberg écrite sur la branche"),
}
TEST_LABELS = {
    "not_null_stg_orders_order_id": "order_id non null",
    "unique_stg_orders_order_id": "order_id unique",
    "not_null_stg_orders_customer_id": "customer_id non null",
    "assert_amount_non_negative": "montant ≥ 0",
    "not_null_daily_orders_order_date": "order_date non null",
    "unique_daily_orders_order_date": "order_date unique",
}


def run_dbt(branch: str, verbose: bool = False) -> bool:
    """Run `dbt build` (run + test) on `branch`, print a per-node summary. True if all green."""
    (DBT_DIR / "target" / "ext").mkdir(parents=True, exist_ok=True)
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
        line("[bold red]dbt a échoué avant la fin du build :")
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
                detail = "non construit : des tests en amont ont échoué"
            check(ok, label, detail)
        else:
            label = "  " + TEST_LABELS.get(name, name)
            detail = f"{r['failures']} ligne(s) en échec" if ok is False and r.get("failures") else ""
            check(ok, label, detail)
    colour = "green" if n_ok == len(results) else "red"
    line(f"[bold {colour}]{n_ok}/{len(results)} OK")
    return result.returncode == 0


def mart(catalog) -> str:
    """daily_orders aggregates by day, so its row count barely moves: show days + orders instead."""
    try:
        data = catalog.load_table(MART_TABLE).scan(selected_fields=("n_orders",)).to_arrow()
    except NoSuchTableError:
        return "n'existe pas encore"
    days = data.num_rows
    return f"{days} jour{'s' if days > 1 else ''}, {sum(data['n_orders'].to_pylist())} commandes"


def tables(catalog) -> list[str]:
    """State of both tables of the demo on a branch, one line per table."""
    return [
        f"{RAW_TABLE:<19} {rows(row_count(catalog, RAW_TABLE))}",
        f"{MART_TABLE:<19} {mart(catalog)}",
    ]


def run_pipeline(bad: bool = False, keep: bool = False, verbose: bool = False) -> int:
    nessie = Nessie()
    branch = f"pipeline-{datetime.now():%H%M%S}" + ("-bad" if bad else "")
    main_catalog = branch_catalog(MAIN)

    display.header(f"Pipeline Nessie · {branch}")

    # --- 0. starting point
    step(0, "État de départ", "API Nessie")
    main_before = nessie.ref_hash(MAIN)
    if main_before == nessie.no_ancestor_hash():
        # A main without history can't be a merge target ("No common ancestor").
        line("[bold red]main n'a encore aucun commit : lance d'abord `mise run stack-up`.")
        return 2
    line(f"main @ [bold]{short(main_before)}[/]")
    for t in tables(main_catalog):
        line(t)

    # --- 1. branch
    step(1, "Ouverture d'une branche pour la pipeline", "API Nessie")
    if nessie.branch_exists(branch):
        nessie.delete_branch(branch)
    nessie.create_branch(branch, from_ref=MAIN)
    line(f"[bold]{branch}[/] créée depuis main @ {short(main_before)}")
    line("[dim]aucune donnée copiée : un nouveau pointeur sur le même commit")

    # --- 2. ingest
    step(2, "Ingestion des commandes sur la branche", "PyIceberg")
    data = ingest(branch, bad=bad)
    line(f"+{data.num_rows} commandes dans {RAW_TABLE}" + (" [bold red](dont des lignes sales)" if bad else ""))
    display.orders_table(data)
    branch_rows = row_count(branch_catalog(branch), RAW_TABLE)
    main_rows = row_count(main_catalog, RAW_TABLE)
    line(f"{RAW_TABLE} : branche = [bold]{rows(branch_rows)}[/] · main = {rows(main_rows)} [dim](inchangé)")
    line(f"[dim]{branch} @ {short(nessie.ref_hash(branch))} (+1 commit) · main @ {short(nessie.ref_hash(MAIN))}")

    # --- 3. dbt build
    step(3, "Transformation et tests de la branche", "dbt + DuckDB")
    ok = run_dbt(branch, verbose=verbose)
    if ok:
        line(f"{MART_TABLE} : branche = [bold]{mart(branch_catalog(branch))}[/] · main = {mart(main_catalog)} [dim](inchangé)")

    # --- 4. decide
    if ok:
        step(4, "Merge dans main et tag (tests verts)", "API Nessie")
        nessie.merge(branch, into=MAIN)
        main_after = nessie.ref_hash(MAIN)
        line(f"merge {branch} → main     main : {short(main_before)} → [bold]{short(main_after)}")
        tag = f"release-{datetime.now():%H%M%S}"  # HHMMSS -> a distinct tag per run
        if nessie.branch_exists(tag):  # same-second re-run -> move the tag to the new state
            nessie.delete_tag(tag)
        nessie.create_tag(tag, from_ref=MAIN)
        line(f"tag [bold]{tag}[/] → {short(main_after)} [dim](immuable)")
        if keep:
            line(f"branche {branch} conservée (--keep)")
        else:
            nessie.delete_branch(branch)
            line(f"branche {branch} supprimée")
        display.pause("Bilan")
        display.success("main mis à jour", tables(main_catalog))
        return 0

    step(4, "Pas de merge, branche conservée (tests rouges)", "API Nessie")
    main_now = nessie.ref_hash(MAIN)
    unchanged = "inchangé" if main_now == main_before else "[bold red]a bougé ![/]"
    line(f"main @ [bold]{short(main_now)}[/] ({unchanged})")
    for t in tables(main_catalog):
        line(t)
    line(f"branche [bold]{branch}[/] conservée pour l'enquête")
    display.pause("Alerte")
    display.console.print()
    alert(
        title=f"Pipeline en échec sur {branch}",
        message=(
            f"Tests dbt rouges : la mauvaise donnée reste isolée sur sa branche.\n"
            f"Rien n'a été mergé dans {MAIN}.\n\n"
            f"Pour enquêter : mise run dbt-inspect {branch}"
        ),
    )
    display.failure("main est resté propre : la mauvaise donnée ne l'a jamais touché")
    return 1


def main() -> None:
    p = argparse.ArgumentParser(description="Run the Nessie branch->test->merge demo pipeline.")
    p.add_argument("--bad", action="store_true", help="ingest dirty data so tests fail (no merge)")
    p.add_argument("--keep", action="store_true", help="keep the branch even on success")
    p.add_argument("--no-pause", action="store_true", help="don't wait for Enter between steps")
    p.add_argument("--verbose", action="store_true", help="show the raw dbt output")
    args = p.parse_args()
    display.PAUSE = not args.no_pause
    raise SystemExit(run_pipeline(bad=args.bad, keep=args.keep, verbose=args.verbose))


if __name__ == "__main__":
    main()
