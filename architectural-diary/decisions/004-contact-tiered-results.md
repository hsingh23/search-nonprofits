# 004 — Tier results by contact channel (email / website / none)

**Date / commit:** 2015-10-16, `f42f8e1` (third tier added here)
**Status:** as shipped.

## Context

The app exists to help people *reach* nonprofits. IRS data offers three
realistic contact channels: a filed email address, a website, or nothing
easily usable. Dumping all matches alphabetically buries the reachable
ones.

## Decision

Physically partition the data into three CSVs at ingestion time —
`emails.csv`, `websites.csv`, `none.csv` — load them as three separate
lists, and render matches in three labeled sections in that priority
order. The no-contact tier is opt-in via the `include_none` query param
(default off). Email rows render as `mailto:` links whose subject is
pre-composed ("Seeking {person} regarding {name}"); website rows link out;
every row links to the Melissa Data IRS lookup by EIN showing the filing
year.

## Consequences

- **Search quality as UX:** the most actionable contacts are always at
  the top without scoring logic — the ordering is baked into the data
  files.
- **Awkward data model:** the "url" field means email in one file and
  website in another; the `Nonprofit` class papers over this with scheme
  normalization (`35343a0`), and `none.csv` repeats the org name in the
  url slot.
- **Three full scans per query:** each request filters all lists (the
  none-list only when opted in).
- **`include_none` truthiness:** any non-empty string enables it, an easy
  source of surprise.
- **Mailto composition lives in the template**, URL-encoding the subject
  there — changing copy means editing Jinja, not Python.

## Alternatives rejected

- Single CSV with a `contact_type` column + sort: cleaner model, but the
  pre-split files already existed from the prototype era.
