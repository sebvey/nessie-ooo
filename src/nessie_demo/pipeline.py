"""The demo pipeline orchestrator.

Flow:
  1. open branch  pipeline_YYYYMMDD  from main         (Nessie)
  2. ingest raw orders onto the branch                 (PyIceberg)
  3. dbt build  = run transforms + run tests           (dbt-duckdb)
  4. tests green -> merge branch into main             (Nessie, atomic)
     tests red   -> DO NOT merge, alert, keep branch   (for inspection)
"""

from __future__ import annotations

import argparse
import subprocess
from datetime import datetime
from pathlib import Path

from .alert import alert
from .catalog import branch_catalog, ensure_namespace
from .ingest import ingest
from .nessie import Nessie
from .settings import settings

REPO_ROOT = Path(__file__).resolve().parents[2]
DBT_DIR = REPO_ROOT / "dbt"


def run_dbt(branch: str) -> bool:
    """Return True if `dbt build` (run + test) succeeds."""
    (DBT_DIR / "target" / "ext").mkdir(parents=True, exist_ok=True)
    env = {"NESSIE_BRANCH": branch}
    cmd = ["dbt", "build", "--project-dir", str(DBT_DIR), "--profiles-dir", str(DBT_DIR)]
    print(f"\n$ NESSIE_BRANCH={branch} {' '.join(cmd)}\n")
    result = subprocess.run(cmd, env={**_base_env(), **env}, cwd=str(REPO_ROOT))
    return result.returncode == 0


def _base_env() -> dict:
    import os

    return dict(os.environ)


def ensure_main_seeded(nessie: Nessie) -> None:
    """A brand-new Nessie 'main' sits at the empty no-ancestor hash, which can't be a merge
    target (no common ancestor). Seed it with a first commit so every pipeline merge works.
    """
    if nessie.ref_hash(settings.main_branch) == nessie.no_ancestor_hash():
        print(f"    main is empty -> seeding it with raw/ and marts/ namespaces (first commit)")
        catalog = branch_catalog(settings.main_branch)
        ensure_namespace(catalog, "raw")
        ensure_namespace(catalog, "marts")


def run_pipeline(bad: bool = False, keep: bool = False) -> int:
    nessie = Nessie()
    ensure_main_seeded(nessie)
    branch = f"pipeline-{datetime.now():%H%M%S}"
    if bad:
        branch += "-bad"

    print(f"==> [1/4] open branch '{branch}' from '{settings.main_branch}'")
    if nessie.branch_exists(branch):
        print(f"    branch already exists, deleting it first for a clean demo run")
        nessie.delete_branch(branch)
    nessie.create_branch(branch, from_ref=settings.main_branch)

    print(f"==> [2/4] ingest raw orders onto '{branch}'" + (" [BAD DATA]" if bad else ""))
    n = ingest(branch, bad=bad)
    print(f"    {n} rows appended to raw.orders")

    print(f"==> [3/4] dbt build (transform + test) on '{branch}'")
    ok = run_dbt(branch)

    if ok:
        print(f"\n==> [4/4] tests GREEN -> merge '{branch}' into '{settings.main_branch}'")
        res = nessie.merge(branch, into=settings.main_branch)
        print(f"    merge successful={res.successful} applied={res.applied}")
        tag = f"release-{datetime.now():%H%M%S}"  # HHMMSS -> a distinct tag per run
        if nessie.branch_exists(tag):  # same-second re-run -> move the tag to the new state
            nessie.delete_tag(tag)
        nessie.create_tag(tag, from_ref=settings.main_branch)
        print(f"    tagged '{settings.main_branch}' as '{tag}' (immutable snapshot)")
        nessie.delete_branch(branch)
        print(f"    branch '{branch}' merged and deleted. main is updated. ✅")
        return 0
    else:
        print(f"\n==> [4/4] tests RED -> NO merge. main stays clean.")
        alert(
            title=f"Pipeline FAILED on branch {branch}",
            message=(
                f"dbt tests failed. The bad data is isolated on branch '{branch}' and was "
                f"NOT merged into '{settings.main_branch}'. Inspect it with:\n"
                f"  mise run dbt-inspect {branch}"
            ),
        )
        if not keep:
            # In a real setup you'd keep it; for the demo we keep it too so it can be inspected.
            pass
        print(f"    branch '{branch}' preserved for debugging. ⛔")
        return 1


def main() -> None:
    p = argparse.ArgumentParser(description="Run the Nessie branch->test->merge demo pipeline.")
    p.add_argument("--bad", action="store_true", help="ingest dirty data so tests fail (no merge)")
    p.add_argument("--keep", action="store_true", help="keep the branch even on success")
    args = p.parse_args()
    raise SystemExit(run_pipeline(bad=args.bad, keep=args.keep))


if __name__ == "__main__":
    main()
