# Nix flake dev shell (Java only)

Use Nix flakes to get a consistent JDK for PySpark/Nessie work.

## Prereqs
- Nix installed with flakes enabled (e.g., `nix.conf` has `experimental-features = nix-command flakes`).

## Enter the dev shell
From the repo root:
```bash
nix develop -c $SHELL
```

With direnv (auto-enter flake and re-exec your shell once):
```bash
cat > .envrc <<'EOF'
use flake
if [ -z "${DIRENV_SHELL_REEXEC-}" ]; then
  export DIRENV_SHELL_REEXEC=1
  exec "$SHELL"
fi
EOF
direnv allow
```

## What you get
- Java 17 (`JAVA_HOME` exported; binaries on PATH).
- No Python here; keep Python deps managed via `uv`.

Exit with `exit` or Ctrl+D.***
