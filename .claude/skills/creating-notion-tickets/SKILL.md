---
name: creating-notion-tickets
description: Create a new task in the Notion "⚒️ Tâches" database for API_PLACES work — Sub project fixed to "API", État fixed to "Todo", following the project's own default template and real ticket style. Use when the user asks to create, file, or open a ticket/task for this repo.
---

# Creating Notion Tickets

Produce the **properties** and the **content** of a new task in Notion's "⚒️ Tâches" database, then
create it once the author has approved both — same discipline as
[`../managing-pull-requests/SKILL.md`](../managing-pull-requests/SKILL.md), and the two are meant to
be used together: a ticket created here is what `managing-pull-requests` later looks up by its
`SOR-xxx` key.

A companion carries the detail: [`references/ticket-body.md`](references/ticket-body.md) annotates
each section; [`examples.md`](examples.md) reproduces two real tickets from this project (`SOR-214`,
`SOR-231`) as calibration.

## Discipline (non-negotiable)

- **Never invent.** A success criterion, a dependency, or a file the task doesn't actually involve is
  a defect. Missing information → ask.
- **Never write to Notion without approval.** Show the full properties and the content, wait for an
  explicit go ahead, then create the page. This mirrors `CLAUDE.local.md`'s git rule, extended to
  Notion writes.
- **Never leave template placeholder text** (`Task 1`, `Task 2`, `Provide a clear overview…`) — every
  section carries real content, or is dropped.
- **Fixed for this repo, every time, no need to ask:**
    - `Sub project` = `["API"]`
    - `État` = `Todo`
    - `Projet` (relation) = the SunnyOnRoads project page, `https://app.notion.com/p/42c732aa3c544d5d83fa90120024970a`
    - **Icon** = the purple light-bulb, matching every real ticket in this database (template included).
      `notion-create-pages`'s `icon` field doesn't accept Notion's native icon name directly — pass the
      URL `https://www.notion.so/icons/light-bulb_purple.svg` and it resolves to the correct native
      icon (verified: `iconMetadata` comes back as `{"type":"icon","icon":{"name":"light-bulb","color":"purple"}}`,
      not an external image). Set it at creation time; if it was missed, fix it after with
      `notion-update-page` passing the same URL as `icon`.
- **Not fixed — ask or infer from context, then confirm:**
    - `Task Type` — one of `Bug`, `Maintenance`, `New Feature`, `Improvement`, `Optional`
    - `Priority` — one of `0 - Critical`, `1 - Hight`, `2 - Medium`, `3 - Low`, `4 - Option`
      (typo `Hight` is the actual option name in this database — reuse it verbatim, don't "fix" it)

## Database reference

- Data source: `collection://341fda1b-dca9-415e-846e-c479f0afc506` ("⚒️ Tâches")
- The `ID` property (`userDefined:ID`, type `unique_id`, prefix `SOR`) is assigned automatically on
  creation — you cannot set it, and you won't know the ticket's `SOR-xxx` key until after creating it.
  Fetch the created page back to report the key to the user.

## Step 1 — Collect the context

| Input | How |
|---|---|
| What needs doing, and why | Ask, or derive from the current conversation/diff if the task is already being discussed. |
| How to verify it's done | Concrete, checkable criteria — not "it works". See `SOR-214`/`SOR-231` in `examples.md` for the level of detail expected (exact routes, status codes, test names). |
| Breakdown into steps | A short checklist — **unticked** (`[ ]`) for a newly-created ticket, since the work hasn't happened yet. (The two examples show `[x]` because they were filled in retrospectively, alongside the PR — don't copy that part literally for a ticket opened *before* starting work.) |
| Dependencies | Existing files/services/config the task touches or relies on — real ones, named from the actual codebase (`app/core/...`, `app/services/...`), not generic placeholders. |
| Task Type / Priority | Ask if not obvious from context; state the inferred value and let the author correct it. |

## Step 2 — Write the content

Follow the section structure in [`references/ticket-body.md`](references/ticket-body.md) — it's this
project's actual default template ("Title Task SunnyOnRoads"), not invented:

```
## Description of the task
## Purpose / Objective
## Success Criteria / Test
## Sub-tasks / Tasks
## Dependencies
## Support Files / References
## Notes / Comments        (optional — drop if there's nothing to add)
```

Draft it in the scratchpad (or `/tmp`), not as a Notion page yet.

## Step 3 — Self-check

- No section still has template placeholder text.
- Success criteria are concrete and testable (route + expected status/shape, not vague intent).
- Sub-tasks are unticked (new ticket, work not started) unless the author says otherwise.
- `Task Type` and `Priority` were confirmed, not silently guessed.
- **The properties JSON literally contains `"Sub project": ["API"]`** — check the payload itself
  before calling `notion-create-pages`, don't just trust that Step 4's template was followed. This is
  the one property most likely to get silently dropped when several tickets are drafted in a row.
- **`icon` is set to `https://www.notion.so/icons/light-bulb_purple.svg`** in the same
  `notion-create-pages` call — easy to forget since it's outside the `properties` block.

## Step 4 — Create

Show the full properties block and the content, **wait for the author's go ahead**, then create in
one call — include the `Projet` relation directly, no separate update step needed:

```json
{
  "properties": {
    "Nom de la tâche": "<title>",
    "État": "Todo",
    "Sub project": ["API"],
    "Task Type": "<Bug|Maintenance|New Feature|Improvement|Optional>",
    "Priority": "<0 - Critical|1 - Hight|2 - Medium|3 - Low|4 - Option>",
    "Projet": ["https://app.notion.com/p/42c732aa3c544d5d83fa90120024970a"]
  },
  "icon": "https://www.notion.so/icons/light-bulb_purple.svg",
  "content": "<the sections from Step 2>"
}
```

Use `notion-create-pages` with `parent: {"type": "data_source_id", "data_source_id": "341fda1b-dca9-415e-846e-c479f0afc506"}`.

After creation, fetch the page back (or read the create response) to get the assigned `ID` — report
the ticket as `SOR-<n>` and its URL to the author. That key is what future commits/branches/PRs
should reference (see `managing-pull-requests`).

## Edge cases

- **Bug report, not a new feature** — the "Title issue" template (simpler: Description, Test, Task to
  fix issue, Support) may fit better than the default one. Ask which shape fits when it's ambiguous;
  default to the standard sections above otherwise.
- **Ticket for work already done** (backfilling, like `SOR-214`/`SOR-231` were) — sub-tasks can be
  ticked `[x]`, and the `pull request` property can be filled immediately with the known PR URL.
- **Vague ask ("add a ticket for the caching bug")** — don't fabricate success criteria or a file
  list to look complete; ask the two or three questions needed instead.
