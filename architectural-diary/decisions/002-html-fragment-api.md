# 002 — `/api/` returns a server-rendered HTML fragment

**Date / commit:** 2015-10-16, `f42f8e1`
**Status:** as shipped.

## Context

The UI needed to show search results without a full page reload. The
original prototype returned raw pipe-delimited lines. The rewrite needed
grouped, styled, linkified results.

## Decision

`GET /api/` accepts `name`, `city`, `state`, `include_none` query params,
filters the in-memory lists, and returns `render_template("api_results.html",
...)` — a Jinja fragment containing the three result sections. The frontend
does `$.get("/api?" + $form.serialize(), function(data){ $results.html(data); })`.

## Consequences

- **One template, two consumers:** `api_results.html` is the results
  markup; injecting it keeps markup in Jinja instead of JS string
  concatenation (the 2015 norm before fetch/JSON habits settled).
- **Not a real API:** the endpoint is unusable by non-browser clients
  wanting structured data; there is no JSON anywhere in the app.
- **Trailing-slash coupling:** the frontend requests `/api` while the route
  is `/api/`; Flask issues the redirect that makes this work. Changing
  either side alone breaks search.
- **No status codes / content negotiation:** validation failure (no params)
  returns an HTML `<b>` usage string with status 200.
- **Retry-on-failure** was later added around this call (`c91e2c6`) with no
  backoff — a fragment-returning API makes client-side error handling easy
  to skip.

## Alternatives rejected

- JSON + client-side rendering: would have meant hand-building the
  mailto/melissadata links in JS; server templates were faster to ship.
