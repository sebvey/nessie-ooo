# ADR002 No dependency cooldown

- Status: accepted
- Date: 2026-10-16
- Tickets: T008
- Basis: arbitrary (cost and benefit not examined: how often a compromised release gets pulled within a week, how long fixes would be delayed, how to bypass the delay for an urgent fix)

## Context

uv can ignore releases younger than a duration: `[tool.uv] exclude-newer = "1 week"`, or per package with `exclude-newer-package` ([uv docs, dependency cooldowns](https://github.com/astral-sh/uv/blob/main/docs/concepts/resolution.md)). The delay leaves time for a compromised or broken release to be spotted and yanked before we pick it up. It also delays security fixes by the same duration.

## Decision

No cooldown for now. The decision was taken in T008 without going into the subject: it is arbitrary and open to challenge.

## Alternatives ruled out

- A global cooldown (for instance one week): not chosen because upgrades here are manual and already infrequent (before a talk, on a vulnerability alert), so new releases rarely reach the lock in their first days. Not weighed further.
- Per-package cooldowns: not examined.

## Consequences

- An upgrade can pick a release published minutes earlier. The protection relies on the manual procedure: one package at a time, read what uv changed, end-to-end check.
- A security fix can be taken as soon as it's published.

## Revisit when

- Upgrades become automated (Renovate, Dependabot) or frequent: fresh releases then reach the lock without anyone choosing them.
- A supply-chain attack hits a package in our tree, or our context starts to require a supply-chain policy.
- Someone examines the subject: this ADR then gets superseded by an investigated one, whatever the outcome.
