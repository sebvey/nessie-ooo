# T002 Test Snowflake on a Nessie branch

Snowflake dominates our clients' stacks: can it read (and write?) a given Nessie branch?
Documentation research only, nothing tested.

## Notes

- Approach: one `ICEBERG_REST` catalog integration with `PREFIX = '<branch>'` and one catalog-linked
  database per branch.
- Prerequisites: Nessie reachable from the internet and authenticated (Snowflake only accepts OAuth,
  bearer or SigV4), files on a real S3 (external volume).
- To check: is `PREFIX` honored? Does Snowflake cope with a `metadata.json` that only holds the
  current snapshot?
