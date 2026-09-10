---
name: managing-pull-requests
description: Create or update GitHub PRs for API_PLACES (and the other SunnyOnRoads repos) with a [SOR-xxx] title, a body matching this project's actual style, and gh CLI commands. Use when the user asks to create, update, or push a pull request.
---

# Managing Pull Requests

Produce the **title** and the **body** of a pull request for the current branch, then create or
update the pull request once the author has approved them.

A companion carries the detail: [`references/pr-body.md`](references/pr-body.md) annotates each
section; [`examples.md`](examples.md) calibrates size and tone on two real merged PRs from this repo
(#16, #14). The ticket itself is created by the sibling skill
[`../creating-notion-tickets/SKILL.md`](../creating-notion-tickets/SKILL.md) — a PR normally
references a ticket that already exists there.

## Discipline (non-negotiable)

- **Never invent.** An endpoint, a response field, a status code, or a behavior the diff does not
  back is a defect in the description. Missing information → ask.
- **Never write to GitHub without approval** — this is also the standing rule in `CLAUDE.local.md`.
  Show the title and the body, wait for an explicit go ahead, then run `gh`. This holds for
  `gh pr create` and `gh pr edit` alike, and for every repo (`API_PLACES`, `SunnyOnRoads`,
  `SunnyOnRoads_android`).
- **Never append an AI attribution trailer** (`🤖 Generated with …`) to the title or the body.
- **No "Impacted Submodules" section** — this repo has none, don't invent the concept.
- **No "Reviews required" / "Owners" sections** — solo project, nothing to assign or count.

## Step 0 — Base branch and range

In practice the base is almost always `main`, but don't assume blindly — check:

```bash
git status --porcelain          # non-empty → warn: uncommitted work is NOT in the pull request
git rev-parse --abbrev-ref HEAD
git merge-base main HEAD
git rev-list --count $(git merge-base main HEAD)..HEAD   # commits ahead
```

If the branch's parent is visibly another feature branch (not `main`), treat it as a **stacked PR**:
open the body with a callout naming the real base and warn that it must merge first.

## Step 1 — Offer a branch review

Before writing anything, offer:

> Run `/code-review` on this branch first? (recommended)

On yes, run the `code-review` skill and relay the ranked findings — fixing first is usually cheaper
than describing a bug and fixing it in a follow-up. On no, or one word of refusal, carry on. This is
an offer, never a gate.

## Step 2 — Collect the context

| Input | How |
|---|---|
| Ticket key | `SOR-\d+` in the branch name or already decided with the user. Ask when absent — don't guess a number. |
| Acceptance criteria / description | **Notion is the source of truth right now, not Jira** — the ticket migration hasn't happened yet (as of 2026-09-10). Query the "⚒️ Tâches" data source (`collection://341fda1b-dca9-415e-846e-c479f0afc506`) filtered on `"ID" unique_id equals <n>` to find the page, then fetch it for its `Success Criteria / Test` and `Sub-tasks / Tasks` sections — see `../creating-notion-tickets/references/ticket-body.md` for what each section means. Fall back to asking the author directly if no matching ticket exists. |
| Related repos | If the change spans API + app (e.g. a new endpoint consumed by iOS/Android), say so in the body rather than staying silent about the cross-repo dependency. |

## Step 3 — Read the diff

```bash
git diff --stat main..HEAD
git log --oneline main..HEAD
git diff main..HEAD -- app/routers app/services app/api    # group by area
git diff main..HEAD -- tests                                # only if tests ARE the change
```

Capture **intent**, not additions — a moved function is a move, not a new feature. Read every
changed source file; that's not a license to mention every one of them.

## Step 4 — Write the body

No `.github/PULL_REQUEST_TEMPLATE.md` exists in this repo (checked 2026-09-10) — the sections below
are used directly, not filled from a template file. Follow
[`references/pr-body.md`](references/pr-body.md) for what each one carries. Write the draft to the
scratchpad directory (or `/tmp/pr_body.md` if none), never inside the repo.

## Step 5 — Self-check, fix rather than flag

- Title is `[SOR-xxx] <imperative summary>`, matching the convention already in this repo's history
  (no CI regex enforces it here — it's a convention, not a gate).
- Every section either carries something real or is dropped — no placeholder left behind.
- No AI attribution trailer.
- `How to test` gives an actual runnable `curl` (or `make test-*`) command when the change is
  testable that way — copy the real endpoint path and params from the diff, don't approximate them.
- Body ends with exactly one `Close [SOR-xxx](<notion-url>)` line — a real link to the ticket's
  Notion page, not plain text (see `references/pr-body.md`) — when a ticket key and its page are
  known; dropped entirely, not guessed, when either isn't.

## Step 6 — Create or update

Show the title and the body, **wait for the author's go ahead**, then:

```bash
# new pull request
gh pr create -R GuillaumeGenest/<repo> --title "$TITLE" --body-file <body-file>

# existing pull request
gh pr view -R GuillaumeGenest/<repo> --json number,title,body     # read current state first
gh pr edit -R GuillaumeGenest/<repo> <PR#> --title "$TITLE" --body-file <body-file>

gh pr view -R GuillaumeGenest/<repo> --json title,body            # verify
```

## Edge cases

- **No divergence from `main`** — nothing to describe; report it and stop.
- **Branch not pushed** — say so, produce the description anyway; it'll be needed once pushed (with
  approval).
- **No ticket key available** — leave the title without a `[SOR-xxx]` prefix and say so explicitly
  rather than inventing a number; the `notion-pr-status-sync` workflow (label → Notion État) simply
  won't find a match for that PR.
- **Backend change with no observable behavior for a human** (perf, internal refactor, caching) —
  drop `How to test` in favor of naming the signal (log line, response time, a `make test` target
  that covers it) rather than padding the section.
