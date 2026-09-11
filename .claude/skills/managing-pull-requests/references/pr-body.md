# Pull request body — sections used in this repo

No `.github/PULL_REQUEST_TEMPLATE.md` exists (checked 2026-09-10), so there's no fixed template to
fill — these are the sections this project's PRs use going forward (see `../examples.md` for the
older, pre-refactor style, and its note on what changed). Drop a section that carries nothing; add a
free section when it answers a question a reviewer (or future-you) would otherwise have to ask.

Reproduce the headings **verbatim, emoji included**, in the order below.

## `## 📓 Description`

One to a few lines on **the problem, as it is observed** — what goes wrong (or what capability is
missing), in which flow, and what it costs. For a feature or a chore, the same rule reads *why the
change exists and what it delivers*.

**No code here.** No file name, no symbol, no framework internal. A reviewer opens the description to
learn what they are being asked to judge; the mechanism is real content, but it belongs in
`Changes proposed in this pull request`, next to the item it explains.

> `get_storage_path()` built a filesystem path directly from the user-supplied `place_id`, with no
> validation. `is_stored()` — a bare `os.path.exists` check — was reachable with an arbitrary string
> and acted as a file-existence oracle.

This is the section most likely to be left thin — one line stating only *what* changed instead of
*why it needed to*. A description that could be guessed from the diffstat alone hasn't done its job.

**Stacked PR** — when the base is another feature branch, not `main`, open with a callout instead of
the paragraph above:

```markdown
> ⚠️ Stacked on `fix/SOR-249-docker-python-version`, not yet merged. **Merge the base branch first.**
```

## `## 📋 Changes proposed in this pull request`

A checklist: `- [x]` for what's done, `- [ ]` for what's legitimately still pending (a deferred test,
a follow-up ticket). One item per load-bearing change — file or function named directly.

This is where the **mechanism** lives: what was wrong in the code, and why the new form is correct.
Cause and remedy in the same item, so the reviewer reads them together instead of holding the
description in their head while scrolling the diff:

```markdown
- [x] `get_storage_path()` (`app/services/storage_service.py`) now validates `place_id` against
      `^[A-Za-z0-9_-]+$` before building the path — the single chokepoint used by both `is_stored()`
      and `download_and_store()`, so both endpoints are covered without duplicating the check
- [x] New `InvalidPlaceIdError` (`app/core/exceptions.py`) → 400 `INVALID_PLACE_ID`, following the
      existing per-exception handler pattern
- [ ] Regression test for the rejection path (`tests/unit/test_routes_images.py`) — separate commit
```

A bare file list (`Updated storage_service.py`) is a defect here, not a style choice — say what
changed *in* the file, and why it's correct.

Plumbing — formatting, renames, generated files, dead imports — stays out, **unless it is the
change**.

### Free sections

Add one only when it earns its place. Seen in this repo's own history, or worth adopting now:

| Section | What it carries |
|---|---|
| `Cost notes` | Pricing/quota rationale for an external API choice (SKU, model, tier). |
| `Notes on scope` | Why an adjacent thing was deliberately **not** changed. |
| `Relationship with #NNNN` | How this PR interacts with another one in flight — in particular a stacked base, or two PRs touching the same area (e.g. #22 and #23 both live against `main` at once). |
| `To revert` | The removal recipe, for temporary or instrumentation code. |
| `Rollout & rollback` | For an infra/deploy-risk change (a base image bump, a migration): what to watch after merge, what tells you to revert. |

Keep them after the checklist and before `## 🧪 How to test`.

## `## 🧪 How to test`

The single most useful section for an API repo with no UI. Two acceptable shapes, pick whichever
actually proves the change:

- **Runnable `curl`**, copied from real testing during development (real path, real params, real
  expected JSON or status code) — not a placeholder URL.
- **`make test-*` target(s)** that cover the change, when the change is exercised by the test suite
  rather than by hand.

State the **starting context** when it isn't obvious — auth required, `TESTING=true`, an environment
variable, a specific record that must exist — and close on the non-regression check that matters:

> Expect `400 {"error": "INVALID_PLACE_ID", ...}`. Full file run:
> `make test-file FILE=tests/unit/test_routes_images.py` — existing valid-`place_id` flows
> (`test_get_image_by_id_success`, `test_get_image_by_id_cache_hit`, ...) must still pass.

When neither shape applies (pure internal refactor, no behavior change) — drop the section rather
than padding it with something vague. When the change isn't observable by clicking or curling
(perf, caching, an internal refactor) — name the signal instead (log line, response time, a
`make test` target that covers it), don't force a fake journey.

## `## 📷 Screenshots`

**Only for `SunnyOnRoads` (iOS) and `SunnyOnRoads_android`** — `API_PLACES` has no UI, so this
section never appears in an `API_PLACES` PR; drop it entirely there rather than writing
`Not applicable`.

For the two app repos, when the change has any visible effect (a new screen, a layout fix, a color
change): a two-column table, one platform per PR since this skill only ever describes a change to one
app at a time — keep the column for the repo the PR is against, drop the other:

```markdown
| iOS | Android |
| --- | ------- |
| <img src="…" /> | <img src="…" /> |
```

No visible change (a networking fix with no UI symptom, an internal refactor) → drop the section.
Never leave a placeholder image or `TODO: screenshot` in place — an unticked `- [ ]` item in
`Changes proposed in this pull request` ("Screenshot pending") is preferable when the image isn't
ready yet but the section itself is expected.

## `## 🧾 Notion`

```markdown
Close [SOR-214](https://app.notion.com/p/373145d7c403801a83b5c1bd83dd4c7d)
```

Adapted from the source skill's `## :receipt: JIRA` section — this repo uses Notion, not Jira, so the
heading and the link target follow suit. No workflow parses "Close X" automatically in the PR body
here (unlike the ticket↔PR title match, already handled by `notion-pr-status-sync`), so a bare
`Close SOR-214` string would be dead text — the **link** is what makes it useful to a human reader.

Get the URL by querying the "⚒️ Tâches" data source for `"ID" unique_id equals <n>` (same lookup as
in `managing-pull-requests/SKILL.md` Step 2) — never fabricate or approximate the URL.

Exactly one such line, in exactly one such section — several tickets closed by one PR is a
conversation to have with the author, not something to encode with extra `Close` lines.

No ticket key available, or the Notion page can't be found → drop the section entirely rather than
writing `Close SOR-xxx` with a guessed number or a guessed URL.

## Never

- An AI attribution trailer (`🤖 Generated with …`) — see `CLAUDE.local.md`.
- A section left with placeholder text.
- The same fact stated twice (e.g. the same change explained in both the checklist and the test
  journey).
- A reviewer-count or owners section — not applicable to a solo project.
- An "Impacted Submodules" section — no bot generates one here, don't invent it.
- Jira syntax, a CI title-regex reference, or any other artifact of the source project this skill
  was adapted from — see `SKILL.md`'s Discipline section.
- More than one `## 🧾 Notion` section or `Close SOR-xxx` line.
