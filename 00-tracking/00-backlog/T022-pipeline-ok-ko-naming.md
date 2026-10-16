# T022 Rename the pipeline branches after pipeline-ok and pipeline-ko

The mise tasks are called `pipeline-ok` and `pipeline-ko`, but the branches the pipeline opens keep the older naming: `pipeline-HHMMSS` for the nominal run and `pipeline-HHMMSS-bad` for the failing one. Find every use of the old naming (`pipeline` / `pipeline-bad`, the `-bad` suffix) and replace it with the ok / ko naming.

## Notes

- The exact new names are to be decided when refining (for example `pipeline-ok-HHMMSS` and `pipeline-ko-HHMMSS`), and whether the `--bad` option of `pipeline` and `ingest` is renamed too (`--ko`?).
- Found on 2026-10-16 (`grep -- "-bad\|pipeline-HHMMSS\|--bad"`):
  - code: `src/nessie_demo/pipeline.py` (branch name, docstring, `--bad`), `src/nessie_demo/ingest.py` (`--bad`), `dbt/tests/assert_amount_non_negative.sql` (comment);
  - tasks: `tasks.toml` (`pipeline-ko`, `dbt-inspect` example);
  - docs: `README.md`, `docs/project/pipeline.md`, `docs/project/nessie-cli.md`, `CLAUDE.md` (end-to-end check);
  - slides (French): `docs/presentation/demo-cli.md`, `docs/presentation/presentation.html`.
- T001 (in progress) also names the `--bad` run in its criteria; tickets in `03-done/` keep the old names: they describe what was true then.
