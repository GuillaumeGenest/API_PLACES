# Ticket body — annotated template

This is the database's actual default page template, **"Title Task SunnyOnRoads"**
(`https://app.notion.com/p/63c7cbd66d76440eaf60bd16815eb53a`), reproduced from its real content —
not invented. See `../examples.md` for two real tickets filled from it.

## `## Description of the task`

What the task is, in plain terms — one to a few sentences. Not the implementation, the ask.

> Add a `/search/coordinates` endpoint that returns the latitude and longitude of a place from its
> Google `place_id`, using the Place Details Essentials SKU.

## `## Purpose / Objective`

**Why** — the product/technical reason this exists. This is where cost, UX, or architectural
rationale belongs, not in the description. A reader should understand the motivation without reading
any code.

## `## Success Criteria / Test`

Concrete, checkable conditions — exact routes, exact status codes, exact response fields, named test
functions. "Works correctly" is not a success criterion; `GET /search/coordinates?place_id=ChIJ...`
returning `place_id, formatted_address, latitude, longitude` is.

## `## Sub-tasks / Tasks`

A checklist, one item per concrete step. **For a newly-created ticket, every box starts unticked**
(`- [ ]`) — the two examples in `examples.md` show ticked boxes only because they were written
retrospectively alongside their PR. Don't copy that part when opening a ticket for work not yet
started.

## `## Dependencies`

Real files, services, or external APIs the task actually touches or relies on — named directly
(`app/core/config.py`, `app/core/security.py`), not generic categories like "the config system".

## `## Support Files / References`

The list of files this task will touch, plus any external documentation worth linking (e.g. the
Google Places API docs for the endpoint being integrated).

## `## Notes / Comments` (optional)

Non-obvious rationale that doesn't fit elsewhere — a deliberate exclusion, an open question for
someone else, a constraint discovered mid-task. Drop the section entirely if there's nothing that
earns a line; don't pad it.

## Fixed properties for this repo (`API_PLACES`)

| Property | Value | Why |
|---|---|---|
| `Sub project` | `["API"]` | This repo is the API sub-project. |
| `État` | `Todo` | Every new ticket starts here. |
| `Projet` | `["https://app.notion.com/p/42c732aa3c544d5d83fa90120024970a"]` | Links the ticket into the SunnyOnRoads project's kanban/filtered views. |

## Properties to ask or infer, never guess silently

| Property | Options |
|---|---|
| `Task Type` | `Bug`, `Maintenance`, `New Feature`, `Improvement`, `Optional` |
| `Priority` | `0 - Critical`, `1 - Hight` *(sic — real option name)*, `2 - Medium`, `3 - Low`, `4 - Option` |

## Alternative template — "Title issue"

A simpler shape exists (`https://app.notion.com/p/5436a0a501644ff2a745dd74eae06cee`) for a pure bug
report, when the full task template is overkill:

```
## Description
## Test :
Repeat the issue too understand
## Task to fix issue
- [ ]
- [ ]
- [ ]
## Support
```

Use it only when the default template's extra sections (`Purpose / Objective`, `Dependencies`) would
genuinely be empty — a one-line reproduction bug, not a feature.
