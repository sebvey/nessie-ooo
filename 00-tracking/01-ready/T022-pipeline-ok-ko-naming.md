# T022 Rename the pipeline branches after pipeline-ok and pipeline-ko

The mise tasks are called `pipeline-ok` and `pipeline-ko`, but the branches the pipeline opens keep the older naming: `pipeline-HHMMSS` for the nominal run and `pipeline-HHMMSS-bad` for the failing one. Find every use of the old naming (`pipeline` / `pipeline-bad`, the `-bad` suffix) and replace it with the ok / ko naming.

## Acceptance criteria

- [ ] `mise run pipeline-ok` opens a `pipeline-ok-HHMMSS` branch and merges; `mise run pipeline-ko` opens `pipeline-ko-HHMMSS`, doesn't merge, and leaves `main` unchanged (end-to-end check after `stack-reset`).
- [ ] `uv run pipeline --help` and `uv run ingest --help` show `--ko`; `--bad` is rejected.
- [ ] A grep for the old naming (`pipeline-HHMMSS`, `-bad`, `--bad`) outside `03-done/` finds only prose about bad data and the `.act.bad` CSS class.
- [ ] `tasks.toml`, `README.md`, `CLAUDE.md` (end-to-end check), `docs/project/` and the French slides (`demo-cli.md`, `presentation.html`) use the new names.

## Notes

- Decided when refining (2026-10-16): branches `pipeline-ok-HHMMSS` and `pipeline-ko-HHMMSS` (prefix like the mise tasks, time last like `release-HHMMSS`; arbitrary, `pipeline-HHMMSS-ok` would do too). The `--bad` option of `pipeline` and `ingest` becomes `--ko`, with no alias (a demo, no users); the Python parameter `bad` becomes `ko`. "Bad data" stays in prose where it describes the data, and the `.act.bad` CSS class of the slides stays (not visible).
- Found on 2026-10-16 (`grep -- "-bad\|pipeline-HHMMSS\|--bad"`):
  - code: `src/nessie_demo/pipeline.py` (branch name, docstring, `--bad`), `src/nessie_demo/ingest.py` (`--bad`), `dbt/tests/assert_amount_non_negative.sql` (comment);
  - tasks: `tasks.toml` (`pipeline-ko`, `dbt-inspect` example);
  - docs: `README.md`, `docs/project/pipeline.md`, `docs/project/nessie-cli.md`, `CLAUDE.md` (end-to-end check);
  - slides (French): `docs/presentation/demo-cli.md`, `docs/presentation/presentation.html`.
- Tickets in `03-done/` (T001 among them) keep the old names: they describe what was true then.
