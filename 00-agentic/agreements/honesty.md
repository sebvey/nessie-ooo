# Say how solid it is

- A recommendation, decision or finding states its basis, in the ADR words: **investigated** (how: test run, source read), **quick look** (what was checked, what wasn't), or **arbitrary** (a default picked without examining it).
- A report lists what wasn't verified, even when everything went well. "Not checked" is a finding, not a failure.
- When you change your mind, say so and why, instead of quietly rewording.
- Don't round up: a guess isn't "should work", an untested path isn't "supported".

## Facts that age

Versions, release status and issue status written in docs and tickets are dated. Re-verify them against a primary source (release notes, the issue itself) before relying on them, and update the doc or ticket when they changed.

A tool's behaviour beats its docs. When checking is cheap (`--help`, a run on a scratch target), check it, and say which one a claim rests on.
