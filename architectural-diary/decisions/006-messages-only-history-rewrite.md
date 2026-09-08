# 006 — Messages-only git history rewrite (2026)

**Date:** 2026-09-08
**Status:** completed; remote force-pushed.

## Context

A 2026 documentation pass found the original commit messages unusable for
history archaeology: "Works", "adds req", "updates ui", "wat", "I know
where you live", "fixes urls", "fixes navigator bug", "minor https". The
code was small enough that every diff could be re-derived and accurately
described.

## Decision

Rewrite `master`'s 8 commit messages via `git filter-branch --msg-filter`,
substituting approved Conventional-Commits messages keyed by original SHA
(messages ONLY — no author, date, or tree changes). Verified afterwards
that `master^{tree}` was byte-identical to a pre-rewrite backup branch,
then force-pushed with `--force-with-lease`. A local backup branch
`backup/pre-docs-20260908` (never pushed) preserves the original chain.

## Consequences

- All commit hashes changed from `bb8a1fc…538a78f` (old) to
  `3c71db5…522247e` (new). Old clones and any links to old SHAs no longer
  resolve on the remote `master`.
- File contents, history shape, authorship, and dates are provably
  unchanged (tree diff empty).
- The 30-odd stale `snyk-fix/*` remote branches still reference old-SHA
  history; they were deliberately left untouched.

## Alternatives rejected

- `git rebase -i` with reword: equivalent effect, but filter-branch gave a
  cleaner scripted, auditable one-shot with per-SHA message files.
- Leaving messages as-is: the CHANGELOG and diary would be built on
  quotes like "wat".
