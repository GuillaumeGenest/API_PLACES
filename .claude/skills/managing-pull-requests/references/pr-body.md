# Pull request body — sections used in this repo

No `.github/PULL_REQUEST_TEMPLATE.md` exists (checked 2026-09-10), so there's no fixed template to
fill — these are the sections this project's own merged PRs actually use (see `../examples.md`).
Drop a section that carries nothing; add a free section when it answers a question a reviewer (or
future-you) would otherwise have to ask.

## `## Description`

One to a few lines on **why the change exists**, not what files it touches. A reviewer (or you, six
months later) opens the description to learn what problem is being solved.

> This PR adds a new endpoint to retrieve the coordinates of a place from its Google place_id, using
> the Place Details Essentials SKU — cheaper than Enterprise and with a 10x larger free cap.

**Stacked PR** — when the base is another feature branch, not `main`, open with a callout:

```markdown
> :warning: Stacked on `feature/xxx`, which is not merged yet. **Merge the base branch first.**
```

## `## What changed`

A short list, one line per load-bearing change, file or module named directly. This is where the
**mechanism** lives — which file, which function, what it now does. Plumbing (formatting, renames,
generated files) stays out unless it *is* the change.

## `## How to test`

The single most useful section for an API repo with no UI. Two acceptable shapes, pick whichever
actually proves the change:

- **Runnable `curl`**, copied from real testing during development (real path, real params, real
  expected JSON) — not a placeholder URL.
- **`make test-*` target(s)** that cover the change, when the change is exercised by the test suite
  rather than by hand.

When neither applies (pure internal refactor, no behavior change) — drop the section rather than
padding it with something vague.

## Free sections

Add one only when it earns its place. Seen in this repo's own history:

| Section | What it carries |
|---|---|
| `Cost notes` | Pricing/quota rationale for an external API choice (SKU, model, tier). |
| `Notes on scope` | Why an adjacent thing was deliberately **not** changed. |

## Closing line — ticket reference

**Always the last line of the body**, on its own, once a ticket key is known — and it must be a
**link to the actual Notion ticket page**, not plain text. No workflow parses "Close X" automatically
here (unlike the ticket↔PR title match, already handled by `notion-pr-status-sync`), so a bare
`Close SOR-214` string would be dead text — the link is what makes it useful to a human reader:

```markdown
Close [SOR-214](https://app.notion.com/p/373145d7c403801a83b5c1bd83dd4c7d)
```

Get the URL by querying the "⚒️ Tâches" data source for `"ID" unique_id equals <n>` (same lookup as
in `managing-pull-requests/SKILL.md` Step 2) — never fabricate or approximate the URL.

Exactly one such line, no more — several tickets closed by one PR is a conversation to have with the
author, not something to encode with extra `Close` lines.

No ticket key available, or the Notion page can't be found → drop the line entirely rather than
writing `Close SOR-xxx` with a guessed number or a guessed URL.

## Never

- An AI attribution trailer (`🤖 Generated with …`) — see `CLAUDE.local.md`.
- A section left with placeholder text.
- The same fact stated twice (e.g. the same change explained in both "What changed" and "How to
  test").
- A reviewer-count or owners section — not applicable to a solo project.
- More than one `Close SOR-xxx` line.
