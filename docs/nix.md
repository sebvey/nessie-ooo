# Nix flake dev shell (Java only)

Use Nix flakes to get a consistent JDK for PySpark/Nessie work.

## Prereqs
- Nix installed with flakes enabled (e.g., `nix.conf` has `experimental-features = nix-command flakes`).

## Enter the dev shell
From the repo root:
```bash
nix develop
```

With direnv:
```bash
echo "use flake" > .envrc
direnv allow
```

## What you get
- Java 17 (`JAVA_HOME` exported; binaries on PATH).
- No Python here; keep Python deps managed via `uv`.

Exit with `exit` or Ctrl+D.***
