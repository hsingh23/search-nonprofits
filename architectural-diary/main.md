# Architectural Diary — Index

This diary records the design decisions behind `search-nonprofits`, written
retrospectively (2026-09-08) from git history and code analysis. Each entry
captures what was chosen, why, and what it cost.

## Decisions

| # | Decision | Commit (era) | File |
| - | -------- | ------------ | ---- |
| 001 | No database — load IRS pipe-delimited CSVs into memory at startup | 3c71db5 (2015-10-01) | [decisions/001-in-memory-csv-data-store.md](decisions/001-in-memory-csv-data-store.md) |
| 002 | `/api/` returns a server-rendered HTML fragment, not JSON | f42f8e1 (2015-10-16) | [decisions/002-html-fragment-api.md](decisions/002-html-fragment-api.md) |
| 003 | Auto-detect visitor location on page load | dc0b8e8 (2015-10-17) | [decisions/003-geolocation-autosearch.md](decisions/003-geolocation-autosearch.md) |
| 004 | Tier results by contact channel (email / website / none) | f42f8e1 (2015-10-16) | [decisions/004-contact-tiered-results.md](decisions/004-contact-tiered-results.md) |
| 005 | Heroku + gunicorn/gevent + forced HTTPS | 3c71db5 / 5a1f73d / 522247e | [decisions/005-heroku-gevent-https.md](decisions/005-heroku-gevent-https.md) |
| 006 | Messages-only git history rewrite (2026) | docs commit, 2026-09-08 | [decisions/006-messages-only-history-rewrite.md](decisions/006-messages-only-history-rewrite.md) |

## Timeline at a glance

- **2015-10-01** — working prototype: path-based search over raw CSV lines,
  deployed to Heroku. (`3c71db5`, `9d8706a`)
- **2015-10-16** — productization: structured `Nonprofit` model, form UI,
  `/api/` endpoint, third dataset for no-contact orgs. (`f42f8e1`)
- **2015-10-17** — polish day: geolocation autofill, URL scheme fix,
  loading/retry feedback. (`dc0b8e8`, `35343a0`, `c91e2c6`)
- **2015-10-20** — HTTPS hardening: remove page-clobbering error handler,
  add and fix the HTTP→HTTPS redirect. (`5a1f73d`, `522247e`)
- **2026-09-08** — documentation pass: commit messages improved via a
  messages-only history rewrite; docs added.
