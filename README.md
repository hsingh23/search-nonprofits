# Search Nonprofits

A small Flask web app that makes IRS nonprofit registry data searchable by
name, city, and state — built in October 2015 and deployed to Heroku at
`find-nonprofit.herokuapp.com`. Given a location (optionally auto-detected
from the browser), it surfaces nearby nonprofits along with the best known
contact channel: an email address, a website, or neither.

## Why

The raw IRS Exempt Organizations data is a pile of pipe-delimited text files
that ordinary people can't query. This app loads ~236,000 nonprofit records
into memory and provides a one-screen search over them, prioritizing
organizations that actually have a reachable contact (email first, website
second). It was built for people who need to reach local nonprofits —
journalists, organizers, donors — without wrestling with government data
dumps.

## Features

- **Search by name, city, and/or state** — substring matching across all
  three fields (case-insensitive).
- **Location auto-detect** — on load, the browser's geolocation is
  reverse-geocoded via the Google Maps Geocoding API to prefill city/state
  and run an initial search automatically.
- **Contact-tiered results** — matches grouped into "Nonprofits with email",
  "Nonprofits with websites", and (opt-in) "Nonprofits with no easy contact".
- **Mailto composition** — email results link to `mailto:` with a
  pre-filled subject naming the nonprofit's contact person.
- **IRS record deep-links** — the record year links to the Melissa Data
  nonprofit lookup by EIN for verification.
- **URL normalization** — bare domains from IRS data get `http://` prepended
  so result links work.
- **Loading indicator and automatic retry** — searches show feedback and
  retry once on failure.
- **Forced HTTPS** — `.htaccess` redirects port-80 traffic to the HTTPS
  Heroku domain (geolocation requires a secure context).

## Stack (versions as pinned in `requirements.txt`)

| Component  | Version  | Role                                             |
| ---------- | -------- | ------------------------------------------------ |
| Python     | 2 (era)  | Runtime — code uses `str.decode("utf8")`         |
| Flask      | 0.10.1   | Web framework, Jinja2 templates                  |
| gunicorn   | 19.3.0   | WSGI server (`--preload`, 4 workers)             |
| gevent     | 1.0.2    | gunicorn worker class                            |
| greenlet   | 0.4.9    | gevent dependency                                |
| Jinja2     | 2.8      | Templating (bundled with Flask pins)             |
| Werkzeug   | 0.10.4   | WSGI toolkit                                     |
| Frontend   | —        | jQuery 2.1.4, Bootstrap 4 (alpha, CDN), Modernizr 3.1.0 (geolocation build) |

No environment variables are required; there is no database — all data lives
in the three CSV files shipped in the repo.

## Quickstart

```bash
# Python 2 era code; use a Python 2.7 interpreter (pyenv or system python2)
python2 -m virtualenv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py            # serves on http://0.0.0.0:9000 (debug mode)
```

Production-style (as on Heroku):

```bash
gunicorn --preload --log-file=- app:app --worker-class gevent --workers=4 --timeout=10
```

Note: geolocation only works on `localhost` or HTTPS origins; run behind TLS
(or rely on the `.htaccess` redirect) to exercise the auto-locate flow.

## How it works

1. On startup, `app.py` reads the three datasets into memory as `Nonprofit`
   objects (this takes a moment — ~236k rows).
2. `GET /` serves `templates/index.html`. The page attempts geolocation,
   prefills city/state, and fires the first search.
3. The form submits via jQuery `$.get("/api?" + form.serialize())`.
4. `GET /api/` filters each dataset with `Nonprofit.match(name, city, state)`
   (substring match on all provided fields) and renders the
   `templates/api_results.html` HTML fragment, which the browser injects
   into `#results`.

## Data

Pipe-delimited CSVs derived from IRS exempt-organizations filings; each row:
`ein|name|url_or_email|year|person|addr1|addr2|city|state`.

| File          | Rows      | Meaning of 3rd column |
| ------------- | --------- | --------------------- |
| `emails.csv`  | ~18,000   | contact email address |
| `websites.csv`| ~214,000  | website URL           |
| `none.csv`    | ~3,600    | no easy contact (echoes name; shown only with `include_none`) |

The CSVs contain public IRS registry data (organization details and officer
contact info as filed). They are large (~28 MB total) and drive startup time.

## Project structure

```
app.py                  # Flask app: Nonprofit model, data loading, / and /api/ routes
templates/index.html    # search UI (Bootstrap 4 alpha, jQuery, Modernizr geolocation)
templates/api_results.html  # results fragment (three contact-tiered groups)
emails.csv / websites.csv / none.csv   # IRS-derived datasets
requirements.txt        # pinned Python 2-era dependencies
Procfile                # Heroku gunicorn + gevent launch
.htaccess               # HTTP → HTTPS redirect
```

## Further reading

- [CHANGELOG.md](CHANGELOG.md) — every commit, newest first.
- [AGENTS.md](AGENTS.md) — developer/agent guide: commands, conventions, gotchas.
- [architectural-diary/main.md](architectural-diary/main.md) — design decisions index.
- [prompt.md](prompt.md) — one-shot prompt to recreate this app from scratch.
