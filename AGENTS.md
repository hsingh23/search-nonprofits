# AGENTS.md — Guide for AI agents and developers working in this repo

## What this is

A tiny 2015-era Flask app (Python 2) that searches ~236k IRS nonprofit
records loaded from three pipe-delimited CSVs, deployed to Heroku
(`find-nonprofit.herokuapp.com`). Two source files of logic
(`app.py` + two Jinja templates), one data model, one API endpoint.

## Commands

```bash
# Setup (Python 2.7 required — code calls str.decode("utf8"))
python2 -m virtualenv venv && source venv/bin/activate
pip install -r requirements.txt

# Run dev server (0.0.0.0:9000, debug=True)
python app.py

# Run like production (what Heroku's Procfile does)
gunicorn --preload --log-file=- app:app --worker-class gevent --workers=4 --timeout=10

# Exercise the API directly
curl "http://localhost:9000/api/?name=lions&city=brunswick&state=GA"
curl "http://localhost:9000/api/?state=NY&include_none=1"
```

There are no tests, no linter config, and no CI in this repo.

## Architecture map

```
app.py
 ├─ Nonprofit          # parses "ein|name|url|year|person|addr1|addr2|city|state"
 │   └─ match(name, city, state)   # case-insensitive substring AND across fields
 ├─ module-level CSV loads (emails.csv, websites.csv, none.csv) → 3 global lists
 ├─ GET /      → templates/index.html
 └─ GET /api/  → filters the 3 lists, renders templates/api_results.html
                 (returns an HTML *fragment*, not JSON)

templates/index.html     # Bootstrap 4 alpha + jQuery 2.1.4 + Modernizr geolocation;
                         # geolocation → Google reverse-geocode → prefill → search
templates/api_results.html  # three sections: email / website / no-contact
Procfile / requirements.txt / .htaccess   # Heroku deploy + HTTPS redirect
```

Key behavioral details:

- `/api/` requires at least one of `name`, `city`, `state`, else it returns
  a usage string with status 200.
- `include_none` is truthy-string checked (any non-empty value counts).
- Frontend calls `/api` (no trailing slash); Flask's redirect to `/api/`
  makes this work — don't "fix" one side without the other.
- EINs shorter than 9 digits are zero-padded to conform to IRS format.
- Officer "person" and filing "year" come from Melissa Data-derived fields;
  results link there by EIN for verification.

## Conventions

- Single-file backend; templates own all presentation. Keep it that way
  unless a real refactor is requested.
- Commit messages: Conventional Commits style (`feat:`, `fix:`, `build:` …),
  imperative subject ≤ 72 chars, body explaining why.
- Dependencies are pinned exactly in `requirements.txt` (Heroku style).

## Gotchas

- **Python 2 syntax**: `l.decode("utf8")` on `str`, print statements era.
  Running under Python 3 fails at import with `AttributeError`/`TypeError`.
- **CSVs are tracked in git** (~28 MB total). Don't reformat them; the
  parser splits on `|` with no quoting/escaping.
- **Data loads at import time** (module level). Any import of `app.py`
  (including by tooling) parses ~236k rows — expect seconds of delay and
  high memory use. `--preload` in the Procfile exists to do this once.
- **No `person` escaping**: the `mailto:` subject is URL-encoded but names
  are rendered raw in Jinja (autoescape is on for `.html` files via Flask
  defaults — actually note Jinja2 autoescape only applies to templates
  rendered through `render_template`; CSV fields pass through it).
- **Error handling is minimal**: empty geocode results crash the callback
  (`data.results[0]` assumes success); the AJAX retry has no backoff and
  can loop.
- **Dead/legacy endpoints from commit 1 were removed**: history only.
- **Known untracked branch litter**: many stale `snyk-fix/*` remote branches
  exist from an old Snyk integration; ignore them.

## Verifying changes

1. `python app.py` starts and `GET /` returns the search page.
2. `curl "http://localhost:9000/api/?name=lions&city=brunswick&state=GA"`
   returns the three-section HTML fragment.
3. `GET /api/` with no params returns the usage message.
4. For template changes: search, then confirm loading indicator and retry
   behavior in a browser over HTTPS or localhost (geolocation needs a
   secure context).

## Pointers

- Per-commit history: [CHANGELOG.md](CHANGELOG.md)
- Design decisions: [architectural-diary/main.md](architectural-diary/main.md)
- Full recreation spec: [prompt.md](prompt.md)
