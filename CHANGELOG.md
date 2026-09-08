# Changelog

All notable changes to this project are documented here, newest first.

> **Note on history:** On 2026-09-08 the commit messages on `master` were
> rewritten (messages only — every tree is byte-identical to the original;
> no file content, author, or date changed). Commit hashes before that date
> differ from earlier clones. See `architectural-diary/main.md` for details.

## 2015-10-20 — 522247e — fix: correct Heroku hostname in .htaccess HTTPS redirect

- Fix a one-character typo in the Apache `RewriteRule`: the redirect target
  was `find-nonprofite.herokuapp.com` (nonexistent domain) instead of
  `find-nonprofit.herokuapp.com`.
- Restores the HTTP → HTTPS redirect so port-80 visitors land on the app.

## 2015-10-20 — 5a1f73d — fix: drop document.write on geolocation error, add HTTPS redirect

- Remove the `document.write(errorMessage)` call from the geolocation error
  callback, which wiped the entire page and left only bare error text
  whenever location lookup failed (denied, unavailable, or timed out).
- Add `.htaccess` forcing all port-80 traffic to the HTTPS Heroku domain —
  browser geolocation requires a secure context.

## 2015-10-17 — c91e2c6 — fix: add loading indicator, retry failed searches, https geocode

- Show a "Fetching your results - please be patient." div during AJAX
  requests (`ajaxStart`/`ajaxStop`) so slow searches give feedback.
- Retry `populateResults` automatically when the `/api` request fails.
- Switch the Google Maps reverse-geocoding call from `http:` to `https:` to
  match the secure page origin.

## 2015-10-17 — 35343a0 — fix: prepend http:// to nonprofit URLs lacking a scheme

- IRS records often contain bare domains (e.g. `www.example.org`), which
  browsers would resolve as relative paths, producing broken links.
- `Nonprofit.__init__` now prepends `http://` when the URL does not already
  start with `http`.

## 2015-10-17 — dc0b8e8 — feat: autofill city and state from browser geolocation

- Add a custom Modernizr 3.1.0 geolocation build to detect support.
- On page load, request the visitor's position, reverse-geocode it via the
  Google Maps Geocoding API, and prefill the city/state form fields.
- Trigger the initial search automatically once location is known; handle
  permission-denied, unavailable, and timeout errors distinctly.

## 2015-10-16 — f42f8e1 — feat: add search form UI and structured /api/ results endpoint

- Replace the URL-path substring search with a real UI: a Bootstrap-styled
  `index.html` form (name / city / state) that AJAX-loads results.
- Introduce the `Nonprofit` class parsing pipe-delimited CSV rows into
  ein, name, url, year, person, address, city, and state fields with a
  `match(name, city, state)` filter; serve `GET /api/`.
- Render results via `api_results.html` in three groups: nonprofits with
  email, with websites, and (opt-in via `include_none`) no easy contact.
- Add `none.csv` as a third dataset and refresh `emails.csv`/`websites.csv`.

## 2015-10-01 — 9d8706a — build: add gevent and greenlet to requirements

- Declare `gevent==1.0.2` and `greenlet==0.4.9` in `requirements.txt` so
  gunicorn's gevent worker-class dependencies install on Heroku.

## 2015-10-01 — 3c71db5 — feat: initial Flask app for searching nonprofit contact data

- First working version: Flask loads the IRS nonprofit email and website
  datasets into memory and serves substring search over `/<search>` and
  `/city/<search>`, returning raw pipe-delimited records.
- Heroku deployment scaffolding: `Procfile` (gunicorn + gevent workers),
  pinned `requirements.txt`, `.gitignore` for `venv/` and `*.pyc`.
