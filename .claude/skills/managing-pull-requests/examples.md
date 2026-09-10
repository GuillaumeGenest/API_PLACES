# Examples

Two merged pull requests from `API_PLACES`, reproduced **as they were actually written** (not
invented — pulled with `gh pr view --json body`). They calibrate size and tone: match the change,
not the size of the example.

Neither one ends with a `Close [SOR-xxx](<notion-url>)` line — that convention was added after these
PRs were merged (see `references/pr-body.md`). Add it on every new PR from now on, as a real link to
the Notion ticket, not plain text; don't read its absence here as license to skip it.

## Example 1 — a new endpoint (#16, `[SOR-214]`)

One new endpoint, a service method, a router change, 5 tests, a doc update. The body leads with the
**why** (cheaper Google SKU), then the file-by-file **what changed**, then two runnable `curl`
examples covering both call shapes (with/without session token) plus the expected JSON — and closes
with a short **cost rationale** free section, because the SKU choice is the actual point of the PR.

```markdown
## Title
This PR adds a new endpoint to retrieve the coordinates of a place from its Google place_id, using the Place Details Essentials SKU — cheaper than Enterprise and with a 10x larger free cap.
What changed

## Description
Added get_search_coordinates() in app/api/API_Autocomplete.py — calls Place Details Essentials with FieldMask: id,location,formattedAddress
Added get_coordinates() method in app/services/autocomplete_service.py
Added GET /search/coordinates in app/routers/search.py — session_token optional to close Android session
Added TestCoordinates class in tests/unit/test_routes_search.py — 5 tests
Updated commandes.md — added $SESSION variable + coordinates curl examples

##  How to test
Sans session token (iOS)

curl -G "http://192.168.1.45:8000/search/coordinates" \
  --data-urlencode "place_id=ChIJu46S-ZZhLxMROG5lkwZ3D7k" \
  -H "Authorization: Bearer $TOKEN"

Avec session token (Android) — clôture la session autocomplete
curl -G "http://192.168.1.45:8000/search/coordinates" \
  --data-urlencode "place_id=ChIJu46S-ZZhLxMROG5lkwZ3D7k" \
  --data-urlencode "session_token=$SESSION" \
  -H "Authorization: Bearer $TOKEN"

Expected response
json{
  "place_id": "ChIJu46S-ZZhLxMROG5lkwZ3D7k",
  "formatted_address": "Rome, Metropolitan City of Rome Capital, Italy",
  "latitude": 41.8967068,
  "longitude": 12.4822025
}

Cost notes

SKU Place Details Essentials → free cap 10,000/month vs 1,000 for Enterprise
Price beyond free cap → $0.005 vs $0.02 for Enterprise
session_token closes the Android autocomplete session → autocomplete becomes free when followed by this call
```

### What to copy

- The **why before the what** — the SKU/cost rationale is the actual reason this PR exists, not an
  afterthought bolted at the end.
- `How to test` gives **two full curl commands**, copy-pasteable, with the real place_id used during
  development and the exact expected JSON shape — not a vague "test the endpoint".
- One free section (`Cost notes`) added because it answers the question a reviewer would otherwise
  ask ("why Essentials and not the usual SKU?").

## Example 2 — a cross-cutting security change (#14, `[SOR-208]`)

Five files, a new middleware wired into every route. The body stays short because the change is
uniform (same middleware, same effect everywhere) — no file-by-file checklist needed, a paragraph of
"what changed" is enough, and testing is entirely `make test-*` commands rather than curl, since the
thing being verified is "auth rejects/accepts correctly", not a specific response shape.

```markdown
## Title
feat(security): Securing the API with Supabase token

### Description
This PR implements JWT authentication on the FastAPI backend to protect all routes and third-party API keys (Google Places, OpenAI).

### What changed
Added app/core/security.py with a middleware that verifies every incoming request against Supabase public JWKS keys (ECC P-256)
Registered auth_middleware in app/main.py
Added TESTING=true environment variable to bypass auth in unit tests
Updated Makefile with make test, make test-unit and make test-integration
Added integration tests to validate the middleware end-to-end

Unit tests (41)
`make test-unit`

Integration tests (3) — requires network
`make test-integration`

Both
`make test`
```

### What to copy

- **Description states the "why" in one line** ("protect all routes and third-party API keys") —
  enough context to judge the change without re-deriving it from the diff.
- **`How to test` names the make targets**, not raw pytest invocations — matches how this project
  actually runs its test suite (see `CLAUDE.local.md`: the author runs these, not Claude).
- No screenshots, no reviewer count, no owners — none of that applies here, so none of it appears.
