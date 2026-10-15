"""`mise run stack-up`: start the stack and prepare main, with an output meant to be narrated.

  1. start the stack            (docker compose: Postgres, MinIO + bucket, Nessie)
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
    "raw": "données brutes, telles qu'ingérées",
    "marts": "données transformées et testées, prêtes à consommer",
}


def start_stack() -> None:
    result = subprocess.run(["docker", "compose", "up", "-d", "--wait", "nessie"], capture_output=True, text=True)
    if result.returncode != 0:
        line("[bold red]docker compose a échoué :")
        display.console.print(result.stdout, result.stderr)
        sys.exit(1)
    line("postgres [green]✓[/] · minio [green]✓[/] · bucket iceberg-warehouse [green]✓[/] · nessie [green]✓")
    line("[dim]Nessie        http://localhost:19120")
    line("[dim]console MinIO http://localhost:29090 (minioadmin / 8qqR90Az)")


def describe(entries: list[dict]) -> str:
    if not entries:
        return "aucun namespace, aucune table"
    kinds = {"NAMESPACE": "namespace", "ICEBERG_TABLE": "table"}
    names = [f"{kinds.get(e['type'], e['type'].lower())} {'.'.join(e['name']['elements'])}" for e in entries]
    return ", ".join(sorted(names))


def main() -> None:
    display.PAUSE = False
    display.header("Mise en place")

    step(1, "Démarrage de la stack", "docker compose", total=3)
    start_stack()

    nessie = Nessie()
    step(2, "État initial de Nessie", "API Nessie", total=3)
    before = nessie.ref_hash(MAIN)
    zero = nessie.no_ancestor_hash()
    commits = "aucun commit (commit zéro)" if before == zero else "déjà des commits"
    line(f"main @ [bold]{short(before)}[/] : {commits}")
    line(f"contenu : {describe(nessie.entries(MAIN))}")

    step(3, "Création des namespaces sur main", "PyIceberg", total=3)
    existing = {".".join(e["name"]["elements"]) for e in nessie.entries(MAIN) if e["type"] == "NAMESPACE"}
    catalog = branch_catalog(MAIN)
    created = 0
    for ns, role in NAMESPACES.items():
        if ns in existing:
            line(f"{ns:<7} [dim]déjà en place[/]  {role}")
        else:
            ensure_namespace(catalog, ns)
            created += 1
            line(f"[bold]{ns:<7}[/] {role}")
    after = nessie.ref_hash(MAIN)
    if created:
        line(f"main @ [bold]{short(after)}[/] (+{created} commits : un par namespace)")
    else:
        line(f"main @ [bold]{short(after)}[/] (inchangé)")
    display.console.print()


if __name__ == "__main__":
    main()
