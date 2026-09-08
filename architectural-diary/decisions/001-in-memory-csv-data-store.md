# 001 — In-memory CSV data store (no database)

**Date / commit:** 2015-10-01, `3c71db5` (structure refined in `f42f8e1`)
**Status:** as shipped, never revisited.

## Context

The source data is IRS exempt-organizations information, already distilled
into three pipe-delimited text files (`emails.csv` ~18k rows,
`websites.csv` ~214k rows, `none.csv` ~3.6k rows; ~28 MB total). The app
needs substring search over name, city, and state — no writes, no
relations, no transactions.

## Decision

Skip any database. At module import, read each CSV into a Python list of
`Nonprofit` objects; search = linear scan with substring matching per
field. The `Nonprofit` constructor splits rows on `|` into typed fields
(ein, name, url, year, person, addr1, addr2, city, state), zero-pads
8-digit EINs, and normalizes missing URL schemes.

## Consequences

- **Simplicity:** zero infra beyond the dyno; deploys are stateless.
- **Startup cost:** every dyno boot (and any import of `app.py`, including
  by tooling) parses ~236k rows — seconds of CPU and substantial RAM.
  The Procfile's `--preload` exists to pay this once per dyno, not per
  worker.
- **Scale ceiling:** linear scan per request is fine for one user, dicey
  for many; gevent workers paper over latency, not algorithmic cost.
- **Data updates require redeploy** (CSVs are git-tracked).
- **Parser fragility:** splitting on `|` assumes no field ever contains a
  pipe and column order never changes — true for this frozen dataset.

## Alternatives rejected

- SQLite/Postgres: real, but pointless overhead for read-only, rarely
  changing data in a weekend project.
- Client-side search (ship the CSV to the browser): 28 MB download in 2015
  was a non-starter.
