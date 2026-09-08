# prompt.md — One-shot recreation prompt

Use the prompt below to recreate this application from scratch. It encodes
every deliberate design decision made in the original (October 2015) build,
verified against the final code.

---

Build a small web application called **Search Nonprofits** that makes IRS
nonprofit registry data searchable so a person can find local nonprofits
and immediately see the best way to contact each one.

## Goal

A visitor opens the page; the app detects their city and state, runs a
search automatically, and shows nearby nonprofits grouped by contact
channel — those with a filed email first, those with a website second, and
(optionally) those with no easy contact. Every result offers a one-click
way to reach the organization (mailto link with a composed subject, or the
website) plus a verification link to the IRS record.

## Exact stack

- **Python 2.7** runtime.
- **Flask 0.10.1** with **Jinja2 2.8** / **Werkzeug 0.10.4** templates.
- **gunicorn 19.3.0** with **gevent 1.0.2** + **greenlet 0.4.9** worker
  class, `--preload --workers=4 --timeout=10`, logs to stdout
  (`--log-file=-`), per `Procfile` for Heroku.
- Pin also `itsdangerous==0.24`, `MarkupSafe==0.23`, `wheel==0.24.0`.
- Frontend: **jQuery 2.1.4**, **Bootstrap 4 alpha** CSS+JS via CDN
  (`cdn.rawgit.com/twbs/bootstrap/v4-dev`), **Modernizr 3.1.0 custom
  geolocation-only build** inlined in `<head>`.
- **No database, no env vars, no API keys.** All data ships as three
  pipe-delimited CSV files in the repo.

## Data model

Row format in every CSV, split on `|`, trimmed:
`ein|name|url_or_email|year|person|addr1|addr2|city|state`

- `emails.csv` (~18k rows): third column is the contact **email**.
- `websites.csv` (~214k rows): third column is the **website URL**.
- `none.csv` (~3.6k rows): no easy contact (third column echoes the name).

`Nonprofit` class (in `app.py`): fields ein, name, url, year, person,
addr1, addr2, city, state, plus derived `full_addr`
(`"{addr1} {addr2}, {city}, {state}"`). Constructor rules:
- EIN zero-padded to 9 digits when it is 8 long.
- URL lowercased; if it does not start with `http`, prepend `http://`.
- `match(name, city, state)`: case-insensitive substring `find(...) > -1`
  AND-ed across name, city, state.

Load all three files once at module import into global lists
(`emails`, `websites`, `none`), skipping lines ≤ 5 chars; decode utf-8,
strip. Serve `python app.py` on `0.0.0.0:9000` with `debug=True`.

## APIs (by name)

- **`GET /`** — renders `templates/index.html` (the search page).
- **`GET /api/`** — query params `name`, `city`, `state`, `include_none`.
  - If all three of name/city/state are empty, return the string
    `<b> You must specify a name, city or state</b>` (status 200).
  - Otherwise filter all three lists with `match()`; `none` list is
    filtered only when `include_none` is a non-empty value.
  - Return `render_template("api_results.html", ...)` — a server-rendered
    **HTML fragment**, not JSON.

## UI / UX / design decisions (all of them)

**index.html:**
- Bootstrap 4 alpha navbar, dark, `bg-primary`, brand text "Search
  Nonprofits" (no link).
- Centered inline form with three inputs — Nonprofit Name, City, State
  (labels sr-only, placeholders carry the meaning) — and a green
  `btn-success` submit labeled "Search!".
- Form `onsubmit` runs `populateResults(); return false;` — search is
  AJAX-only via `$.get("/api?" + $form.serialize())`, injecting the
  fragment into `#results`.
- On `$.get` failure, retry by re-invoking `populateResults()` (no
  backoff).
- Loading indicator: a hidden `#loadingDiv` ("Fetching your results -
  please be patient.") shown on `ajaxStart`, hidden on `ajaxStop`.
- If `Modernizr.geolocation`: on load call
  `navigator.geolocation.getCurrentPosition` with
  `{enableHighAccuracy: true, timeout: 10000, maximumAge: 0}`; on success
  GET the Google Maps Geocoding API
  (`https://maps.googleapis.com/maps/api/geocode/json?latlng=…&sensor=true`,
  keyless), take the `locality` short_name into the city input and
  `administrative_area_level_1` short_name into the state input, then run
  `populateResults()` automatically. On error do nothing visible (do NOT
  use document.write — that wiped the page historically).

**api_results.html** — three conditional sections, in priority order:
1. **"Nonprofits with email"** — name links to
   `mailto:{email}?Subject=Seeking%20{person}%20reguarding%20{name}`
   (subject URL-encoded; keep the original "reguarding" typo); shows
   email, full address, contact person bolded, and the filing year linked
   to `http://www.melissadata.com/lookups/np.asp?mp=p&ein={ein}`
   (target `_blank`).
2. **"Nonprofits with websites"** — name links to the org URL; same
   address/person/year/EIN-link treatment.
3. **"Nonprofits with no easy contact"** — rendered only when
   `include_none` is set; plain text name, same metadata treatment.

**Infra/deploy:**
- `Procfile`: `web: gunicorn --preload --log-file=- app:app
  --worker-class gevent --workers=4 --timeout=10`.
- `.htaccess`: `RewriteEngine On`, redirect any port-80 request to
  `https://find-nonprofit.herokuapp.com/$1` `[R,L]` — purpose: secure
  origin for geolocation.
- `.gitignore`: `venv/` and `*pyc`.

## Build order (phases)

1. Flask skeleton; CSV loading into `Nonprofit` objects; root page.
2. `GET /api/` filtering + `api_results.html` fragment; wire the form AJAX,
   loading indicator, and retry.
3. Geolocation → reverse geocode → prefill → auto-search; URL scheme
   normalization in the parser.
4. Deploy hardening: Procfile/gunicorn/gevent pins, HTTPS redirect,
   `include_none` tier visible.

## Acceptance criteria

1. `python app.py` serves the search page at `/` on port 9000.
2. Searching name=lions, city=brunswick, state=GA returns matching
   records in the email and/or website sections, grouped and ordered
   email → website → (opt-in) none.
3. `/api/` with no params returns the "You must specify…" message.
4. `include_none` (any non-empty value) makes the third section appear.
5. Result website links are absolute (`http://` prepended when the data
   lacked a scheme).
6. On an HTTPS or localhost origin with location permission granted, the
   city/state fields self-populate and a search runs without user input.
7. The loading message appears during requests and hides after.
8. `gunicorn --preload --log-file=- app:app --worker-class gevent
   --workers=4 --timeout=10` serves the same behavior as the dev server.
