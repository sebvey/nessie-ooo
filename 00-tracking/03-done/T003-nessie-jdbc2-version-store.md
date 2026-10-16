# T003 Nessie version store: JDBC to JDBC2

`docker-compose.yml` used `nessie.version.store.type=JDBC`, deprecated for removal in favor of
`JDBC2`. No migration needed: local data can be reset.

## Acceptance criteria

- [x] Nessie runs on `JDBC2` on Postgres, with no deprecated or unused version store settings.
- [x] `mise run stack-reset`, `stack-up`, `pipeline-ok` and `pipeline-ko` pass.
- [x] Branches and tags survive a restart of the Nessie container.
- [x] Docs describe the new setup.

## Outcome

Branch `nessie-jdbc2` (before ticket IDs existed), squashed into one commit on `main`.
- Quarkus datasource named `postgresql` (`nessie.version.store.persist.jdbc.datasource`); the
  `nessie.version.store.jdbc.*` keys, which don't exist, are gone. Nessie creates `refs2` and
  `objs2` (one serialized value per object instead of a wide table).
- Postgres credentials moved to `mise.local.toml` (`NESSIE_PG_USER` / `NESSIE_PG_PASSWORD`),
  template in `mise.local.toml.example`.
- Updated: `docs/project/architecture.md`, `docs/concepts/nessie-deployment.md`.
