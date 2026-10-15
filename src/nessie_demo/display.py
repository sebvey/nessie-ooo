"""Console output of the demo pipeline: one block per step, written to be narrated live."""

from __future__ import annotations

import sys

import pyarrow as pa
from rich.console import Console
from rich.padding import Padding
from rich.table import Table

console = Console(highlight=False)

PAUSE = True  # set by the CLI (--no-pause); also skipped automatically when stdin isn't a TTY


def short(h: str) -> str:
    """Git-style short hash."""
    return h[:7]


def header(title: str) -> None:
    console.print()
    console.rule(f"[bold]{title}", align="left", style="cyan")


def step(n: int, title: str, tool: str, total: int = 4) -> None:
    if n > 0:  # l'étape 0 suit directement le lancement
        pause(title)
    console.print()
    t = Table.grid(expand=True)
    t.add_column()
    t.add_column(justify="right")
    t.add_row(f"[bold cyan]\\[{n}/{total}][/] [bold]{title}", f"[dim]{tool}")
    console.print(t)


def rows(n: int | None) -> str:
    """Row count of a table, or the fact that it doesn't exist yet."""
    if n is None:
        return "n'existe pas encore"
    return f"{n} ligne" if n <= 1 else f"{n} lignes"


def line(text: str = "") -> None:
    console.print(f"      {text}")


def pause(next_step: str) -> None:
    """Wait for Enter, announcing what comes next."""
    if not PAUSE or not sys.stdin.isatty():
        return
    console.print(f"\n[dim]      ⏎  Entrée pour la suite : {next_step[0].lower() + next_step[1:]}[/]", end="")
    input()
    # efface la ligne du prompt pour garder une sortie propre
    sys.stdout.write("\x1b[1A\x1b[2K")
    sys.stdout.flush()


def orders_table(data: pa.Table) -> None:
    """The freshly ingested rows, dirty values in red."""
    t = Table(box=None, padding=(0, 2), pad_edge=False, header_style="dim")
    t.add_column("order_id", justify="right")
    t.add_column("client")
    t.add_column("produit")
    t.add_column("montant", justify="right")
    t.add_column("qté", justify="right")
    for row in data.to_pylist():
        client = row["customer_id"] if row["customer_id"] is not None else "[bold red]∅ (null)[/]"
        amount = f"{row['amount']:.2f}"
        if row["amount"] < 0:
            amount = f"[bold red]{amount}[/]"
        t.add_row(str(row["order_id"]), client, row["product"], amount, str(row["quantity"]))
    console.print(Padding(t, (0, 0, 0, 8)))


def check(ok: bool | None, label: str, detail: str = "") -> None:
    """ok=True ✓, ok=False ✗, ok=None ⏭ (skipped)."""
    mark = {True: "[green]✓[/]", False: "[bold red]✗[/]", None: "[yellow]⏭[/]"}[ok]
    line(f"{mark} {label:<26} [dim]{detail}[/]" if detail else f"{mark} {label}")


def success(text: str, details: list[str] = ()) -> None:
    console.print()
    console.print(f"[bold green]✅ {text}")
    for d in details:
        console.print(f"   {d}")
    console.print()


def failure(text: str) -> None:
    console.print()
    console.print(f"[bold red]⛔ {text}")
    console.print()
