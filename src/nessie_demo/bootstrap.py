"""`mise run stack-up`: start the stack and prepare main, with an output meant to be narrated.

  1. start the stack            (docker compose: Postgres, Silo (MinIO fork) + bucket, Nessie)
  2. initial state of Nessie    (main sits on the "commit zero", no content)
  3. create the namespaces      (raw, marts) on main -> one commit each

Why step 3 exists: a brand-new main has no commit, and Nessie can't merge into a branch without
history ("No common ancestor"). Creating the namespaces gives main its first commits.
"""

from __future__ import annotations

import subprocess
import sys

from . import display
from .catalog import branch_catalog, ensure_namespace
from .display import line, short, step
from .nessie import Nessie
from .settings import settings

MAIN = settings.main_branch
NAMESPACES = {
    "raw": "raw data, as ingested",
    "marts": "transformed and tested data, ready to use",
}


def start_stack() -> None:
    result = subprocess.run(["docker", "compose", "up", "-d", "--wait", "nessie"], capture_output=True, text=True)
    if result.returncode != 0:
        line("[bold red]docker compose failed:")
        display.console.print(result.stdout, result.stderr)
        sys.exit(1)
    line("postgres [green]✓[/] · silo [green]✓[/] · bucket iceberg-warehouse [green]✓[/] · nessie [green]✓")
    line(f"[dim]Nessie        {settings.nessie_uri}")
    line("[dim]Silo console  http://localhost:29090 (credentials in mise.local.toml)")


def describe(entries: list[dict]) -> str:
    if not entries:
        return "no namespace, no table"
    kinds = {"NAMESPACE": "namespace", "ICEBERG_TABLE": "table"}
    names = [f"{kinds.get(e['type'], e['type'].lower())} {'.'.join(e['name']['elements'])}" for e in entries]
    return ", ".join(sorted(names))


def main() -> None:
    display.PAUSE = False
    display.header("Setup")

    step(1, "Starting the stack", "docker compose", total=3)
    start_stack()

    nessie = Nessie()
    step(2, "Initial state of Nessie", "Nessie API", total=3)
    before = nessie.ref_hash(MAIN)
    zero = nessie.no_ancestor_hash()
    commits = "no commit (commit zero)" if before == zero else "already has commits"
    line(f"main @ [bold]{short(before)}[/]: {commits}")
    line(f"content: {describe(nessie.entries(MAIN))}")

    step(3, "Creating the namespaces on main", "PyIceberg", total=3)
    existing = {".".join(e["name"]["elements"]) for e in nessie.entries(MAIN) if e["type"] == "NAMESPACE"}
    catalog = branch_catalog(MAIN)
    created = 0
    for ns, role in NAMESPACES.items():
        if ns in existing:
            line(f"{ns:<7} [dim]already there[/]  {role}")
        else:
            ensure_namespace(catalog, ns)
            created += 1
            line(f"[bold]{ns:<7}[/] {role}")
    after = nessie.ref_hash(MAIN)
    if created:
        line(f"main @ [bold]{short(after)}[/] (+{created} commits: one per namespace)")
    else:
        line(f"main @ [bold]{short(after)}[/] (unchanged)")
    display.console.print()


if __name__ == "__main__":
    main()
