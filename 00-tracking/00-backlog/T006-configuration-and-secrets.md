# T006 Configuration and secrets

The same values are repeated in `docker-compose.yml`, `mise.toml`, `settings.py`, `dbt/profiles.yml` and `bootstrap.py` (Silo `minioadmin` / `8qqR90Az`, Nessie and S3 URLs). Goal: one source of truth, secrets kept out of tracked files.

## Notes

- Done for the Postgres credentials (see [T003](../03-done/T003-nessie-jdbc2-version-store.md)): `NESSIE_PG_USER` / `NESSIE_PG_PASSWORD` in `mise.local.toml`, read by `docker-compose.yml` with `${VAR:?…}`. Same pattern to apply to Silo.
- Open question for a team: share secrets encrypted (sops, supported by mise) rather than by copying a local file.
