# T005 Refactor the Python package

`src/nessie_demo/` was built quickly for a live demo; make it maintainable. To be split into smaller tickets when refined.

## Notes

Observed:
- **Nessie client** (`nessie.py`): no timeouts, no session or retries, no authentication, raw dicts in and out, hash-then-act races (`delete_branch`, `merge`). Could become its own project (typed Nessie API v2 client, with tests): to discuss, `pynessie` being dead.
- **No tests** at all, no lint, format or type checking, no CI.
- **Settings**: secrets as code defaults (`settings.py`), `env_prefix=""` so generic variable names (`WAREHOUSE`, `S3_ENDPOINT`…).
- **`pipeline.py` mixes orchestration and narrated display** (`display.py`): the demo output should be a layer on top of a reusable pipeline.
- Packaging: dependencies to review (`pandas` is only there for the dbt plugin path, `numpy` only for synthetic data), `uv_build<0.10` constraint warning with the current uv, `ingest` script entry point still exposed.

Leads: decide the client's scope first (in repo or separate package); pytest with the stack as a fixture for integration tests; ruff and a type checker; split core and presentation.
