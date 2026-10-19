"""`mise run stack-up`: start the stack and prepare main, with an output meant to be narrated.

  1. start the stack            (docker compose: Postgres, Silo + bucket, Nessie)
  2. initial state of Nessie    (main sits on the "commit zero", no content)
  3. create the namespaces      (raw, marts) on main -> one commit each

Why step 3 exists: a brand-new main has no commit, and Nessie can't merge into a branch without
history ("No common ancestor"). Creating the namespaces gives main its first commits.
"""

from __future__ import annotations

import subprocess
import sys

from lakehouse_client.catalog import branch_catalog, ensure_namespace
from lakehouse_client.nessie import Nessie
from lakehouse_client.settings import settings
from rich.console import Console
from rich.table import Table

MAIN = settings.main_branch
NAMESPACES = {
    "raw": "raw data, as ingested",
    "marts": "transformed and tested data, ready to use",
}

TOTAL_STEPS = 3

console = Console(highlight=False)


def short(h: str) -> str:
    """Git-style short hash."""
    return h[:7]


def header(title: str) -> None:
    console.print()
    console.rule(f"[bold]{title}", align="left", style="cyan")


def step(n: int, title: str, tool: str) -> None:
    console.print()
    t = Table.grid(expand=True)
    t.add_column()
    t.add_column(justify="right")
    t.add_row(f"[bold cyan]\\[{n}/{TOTAL_STEPS}][/] [bold]{title}", f"[dim]{tool}")
    console.print(t)


def line(text: str = "") -> None:
    console.print(f"      {text}")


def start_stack() -> None:
    result = subprocess.run(["docker", "compose", "up", "-d", "--wait", "nessie"], capture_output=True, text=True)
    if result.returncode != 0:
        line("[bold red]docker compose failed:")
        console.print(result.stdout, result.stderr)
        sys.exit(1)
    line("postgres [green]✓[/] · silo [green]✓[/] · bucket iceberg-warehouse [green]✓[/] · nessie [green]✓")
    line(f"[dim]Nessie        {settings.nessie_uri}")
    line(f"[dim]Silo console  {settings.silo_console_url} (credentials in mise.local.toml)")


def describe(entries: list[dict]) -> str:
    if not entries:
        return "no namespace, no table"
    kinds = {"NAMESPACE": "namespace", "ICEBERG_TABLE": "table"}
    names = [f"{kinds.get(e['type'], e['type'].lower())} {'.'.join(e['name']['elements'])}" for e in entries]
    return ", ".join(sorted(names))


def main() -> None:
    header("Setup")

    step(1, "Starting the stack", "docker compose")
    start_stack()

    nessie = Nessie()
    step(2, "Initial state of Nessie", "Nessie API")
    before = nessie.ref_hash(MAIN)
    zero = nessie.no_ancestor_hash()
    commits = "no commit (commit zero)" if before == zero else "already has commits"
    line(f"main @ [bold]{short(before)}[/]: {commits}")
    line(f"content: {describe(nessie.entries(MAIN))}")

    step(3, "Creating the namespaces on main", "PyIceberg")
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
    console.print()


if __name__ == "__main__":
    main()
