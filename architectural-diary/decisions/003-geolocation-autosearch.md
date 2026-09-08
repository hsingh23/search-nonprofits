# 003 — Auto-detect visitor location and run the first search

**Date / commit:** 2015-10-17, `dc0b8e8` (hardened in `c91e2c6`, `5a1f73d`)
**Status:** as shipped.

## Context

The app's core question is "which nonprofits are near me?" Forcing users to
type city and state on every visit was friction; the browser already knows
the answer.

## Decision

Ship a custom Modernizr 3.1.0 build that tests only for geolocation. On
load, if supported, call `navigator.geolocation.getCurrentPosition`, then
reverse-geocode the coordinates via the (keyless, 2015-era) Google Maps
Geocoding API, extract `locality` and
`administrative_area_level_1` address components, fill the city/state
inputs, and immediately trigger the search.

## Consequences

- **Zero-query onboarding:** most visitors get local results without
  typing anything.
- **HTTPS dependency:** geolocation requires a secure context — this is
  the real reason the app grew an HTTP→HTTPS redirect (`5a1f73d`,
  `522247e`).
- **Fragile happy path:** the callback assumes `data.results[0]` exists;
  a failed/empty geocode response throws silently. Error handling went
  through two iterations — per-code error messages written with
  `document.write` (which wiped the page, removed in `5a1f73d`), leaving
  errors effectively swallowed.
- **Keyless Google API:** worked in 2015, deprecated since — a modern
  rebuild needs a key or a different provider.
- **Privacy:** coordinates are sent to Google and (implicitly) the request
  reveals location to the server; no consent screen beyond the browser's
  native prompt.

## Alternatives rejected

- HTML5 geolocation only for explicit "use my location" button: less
  magical, more robust — the auto-run version won for demo effect.
- IP-based geolocation: too coarse for city-level nonprofit search.
