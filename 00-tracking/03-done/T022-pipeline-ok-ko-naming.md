# T022 Rename the pipeline branches after pipeline-ok and pipeline-ko

The mise tasks are called `pipeline-ok` and `pipeline-ko`, but the branches the pipeline opens keep the older naming: `pipeline-HHMMSS` for the nominal run and `pipeline-HHMMSS-bad` for the failing one. Find every use of the old naming (`pipeline` / `pipeline-bad`, the `-bad` suffix) and replace it with the ok / ko naming.

## Acceptance criteria

- [x] `mise run pipeline-ok` opens a `pipeline-ok-HHMMSS` branch and merges; `mise run pipeline-ko` opens `pipeline-ko-HHMMSS`, doesn't merge, and leaves `main` unchanged (end-to-end check after `stack-reset`). (`stack-reset`, `stack-up`, `uv run pipeline --no-pause` and `--ko --no-pause`, then both mise tasks, 2026-10-16)
- [x] `uv run pipeline --help` and `uv run ingest --help` show `--ko`; `--bad` is rejected. (both `--help`, and `--bad` exits 2 with "unrecognized arguments", 2026-10-16)
- [x] A grep for the old naming (`pipeline-HHMMSS`, `-bad`, `--bad`) outside `03-done/` finds only prose about bad data and the `.act.bad` CSS class. (`git grep` for `-bad`, `pipeline-HHMMSS`, `--bad`, `pipeline-[0-9]{6}`: no hit; `git grep -w bad`: prose and CSS only, 2026-10-16)
- [x] `tasks.toml`, `README.md`, `CLAUDE.md` (end-to-end check), `docs/project/` and the French slides (`demo-cli.md`, `presentation.html`) use the new names. (diff read, same grep, 2026-10-16)

## Notes

- Decided when refining (2026-10-16): branches `pipeline-ok-HHMMSS` and `pipeline-ko-HHMMSS` (prefix like the mise tasks, time last like `release-HHMMSS`; arbitrary, `pipeline-HHMMSS-ok` would do too). The `--bad` option of `pipeline` and `ingest` becomes `--ko`, with no alias (a demo, no users); the Python parameter `bad` becomes `ko`. "Bad data" stays in prose where it describes the data, and the `.act.bad` CSS class of the slides stays (not visible).
- Found on 2026-10-16 (`grep -- "-bad\|pipeline-HHMMSS\|--bad"`):
  - code: `src/nessie_demo/pipeline.py` (branch name, docstring, `--bad`), `src/nessie_demo/ingest.py` (`--bad`), `dbt/tests/assert_amount_non_negative.sql` (comment);
  - tasks: `tasks.toml` (`pipeline-ko`, `dbt-inspect` example);
  - docs: `README.md`, `docs/project/pipeline.md`, `docs/project/nessie-cli.md`, `CLAUDE.md` (end-to-end check);
  - slides (French): `docs/presentation/demo-cli.md`, `docs/presentation/presentation.html`.
- Tickets in `03-done/` (T001 among them) keep the old names: they describe what was true then.

## Outcome

The pipeline opens `pipeline-ok-HHMMSS` for the nominal run and `pipeline-ko-HHMMSS` for the failing one, and the `--bad` option of `pipeline` and `ingest` became `--ko` (Python parameter `ko`). Renamed in `src/nessie_demo/pipeline.py`, `src/nessie_demo/ingest.py`, the dbt test comment, `tasks.toml`, `README.md`, `CLAUDE.md`, `docs/project/pipeline.md`, `docs/project/nessie-cli.md` and the French slides (`demo-cli.md`, `presentation.html`, including the sample branch `pipeline-143205`, now `pipeline-ok-143205`).

- End-to-end check (2026-10-16), after `stack-reset` (which deleted the refs left by earlier sessions, with the developer's agreement) and `stack-up`: `uv run pipeline --no-pause` opened `pipeline-ok-202204`, merged and tagged `release-202207`; `uv run pipeline --ko --no-pause` opened `pipeline-ko-202211`, exited 1 without merging, `main` stayed on `f6360f4`. `mise run pipeline-ko` then `pipeline-ok` (Enter fed through stdin) gave the same, and `mise run dbt-inspect pipeline-ko-202211` replayed dbt build on the kept branch (2 errors, as expected).
- Left aside: "bad data" stays in prose where it describes the data, and the `.act.bad` CSS class of the slides stays (not visible).
- Not verified: the slides weren't rendered; the longer sample branch name was only estimated to fit its SVG boxes (monospace width). The mise tasks weren't run from an interactive terminal (stdin was piped).
