# 005 — Heroku deployment: gunicorn + gevent, forced HTTPS

**Date / commits:** `3c71db5` (Procfile), `9d8706a` (gevent deps),
`5a1f73d` + `522247e` (HTTPS redirect, 2015-10-20)
**Status:** as shipped.

## Context

A weekend project needs free, zero-ops hosting. Heroku in 2015 offered
that; gunicorn with gevent workers was the standard recipe for handling
many concurrent slow HTTP requests on a single small dyno — relevant
because every search linearly scans 236k records while the user waits,
and the geocoding round-trips add latency.

## Decision

- `Procfile`: `web: gunicorn --preload --log-file=- app:app
  --worker-class gevent --workers=4 --timeout=10`.
- Pin the full transitive dependency set in `requirements.txt`
  (`gunicorn==19.3.0`, `gevent==1.0.2`, `greenlet==0.4.9`, …).
- Serve at `find-nonprofit.herokuapp.com`; `.htaccess` redirects port-80
  traffic to the HTTPS hostname (initially with a typo — `522247e` fixed
  `find-nonprofite` → `find-nonprofit`).

## Consequences

- **`--preload` matters:** CSV parsing happens once per dyno in the master
  before forking four workers, instead of four times.
- **`--timeout=10` is generous but finite:** a cold dyno loading 28 MB of
  CSVs can flirt with it.
- **The `.htaccess` approach is odd on Heroku** (no Apache in front); it
  only works where Apache actually serves the app — effectively symbolic,
  with real HTTPS provided by Heroku's router. Its true purpose was
  guaranteeing a secure origin so geolocation works.
- **Pinned 2015 stack:** Python 2 + Flask 0.10 + gevent 1.0 do not build
  cleanly on modern platforms; running this today requires an era-appropriate
  environment (see AGENTS.md gotchas).

## Alternatives rejected

- Sync workers: fewer concurrent users per dyno during slow searches.
- Flask's dev server in production: never.
