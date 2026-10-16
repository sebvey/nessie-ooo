# T011 Global security audit

T010 audits the Python dependencies only. The rest of what runs is not audited: the container images in `docker-compose.yml` (Nessie and Nessie CLI `0.106.0`, `postgres:15`, Silo and `mc` from the `pgsty` community fork), and the tools mise installs (`uv = "latest"`). Think through what a global audit should cover before building anything.

## Questions to settle when refining

- **Scope**: which parts deserve an audit for a local demo stack (images, OS packages inside them, the Java dependencies inside Nessie, mise tools), and which risks matter here (a laptop demo, no exposure) versus at a client.
- **Tools**: an image scanner (Trivy, Grype, Docker Scout…), to compare on coverage, cost and how it fits in a mise task. Facts to check at refining time.
- **Image versions**: `postgres:15` is a floating tag; the Silo images come from a community fork (supply-chain trust). Whether to pin by digest, and how this fits ADR001's logic (lock as source of truth) for images.
- **What to do with findings** we can't fix (a CVE in the Nessie image): accept, record, upgrade Nessie.
- **One task or several**: a `mise run audit` running every audit, or one task per part.
- Whether a decision here deserves an ADR (`00-agentic/processes/adr.md`).

## Notes

- Lead to compare first: **OSV-Scanner** (Google), which reads `uv.lock` and, since v2, scans container images too ([guide](https://appsecsanta.com/osv-scanner)); one tool could cover both parts. Trivy also reads `uv.lock` and images but excludes dev dependencies ([Trivy docs](https://trivy.dev/docs/dev/coverage/language/python/)). Neither was tested (2026-10-16).
- The Python part may move to `uv audit` first (T013).

## Outcome
