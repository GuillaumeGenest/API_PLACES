# Examples

Two real tickets from the "⚒️ Tâches" database, `Sub project = API`, reproduced **as they actually
are** (fetched via the Notion MCP, not invented). Both happen to be filled in retrospectively
(alongside their PR), which is why their sub-tasks are ticked — a ticket you open *before* starting
work should have the same depth of detail but unticked boxes.

## Example 1 — `SOR-214`, a new endpoint (Maintenance, Priority 1 - Hight)

```markdown
**Description of the task**
Add a `/search/coordinates` endpoint that returns the latitude and longitude of a place from its Google `place_id`, using the Place Details Essentials SKU. Also add the `/search/autocomplete` endpoint with session token support.

**Purpose / Objective**
After an autocomplete search, the app needs the coordinates of the selected place to center the map. The Place Details Essentials SKU is used — cheaper than Enterprise (free cap 10,000/month vs 1,000) — since only `location` and `formattedAddress` are needed, not the full place details.

**Success Criteria / Test**
- `GET /search/coordinates?place_id=ChIJ...` returns `place_id`, `formatted_address`, `latitude`, `longitude`
- With `session_token` → token passed to Google to close the Android session
- Without `session_token` → works normally (iOS)
- Missing `place_id` → `422`
- Unknown `place_id` → `400`
- All unit tests pass

**Sub-tasks / Tasks**
- [x] Add `get_search_coordinates()` in `app/api/API_Autocomplete.py`
- [x] Add `get_coordinates()` method in `app/services/autocomplete_service.py`
- [x] Add `GET /search/coordinates` in `app/routers/search.py`
- [x] Add `TestCoordinates` class in `tests/unit/test_routes_search.py`
- [x] Update `commandes.md` with curl examples

**Dependencies**
- `app/core/config.py` — `get_api_key()` for Google API key
- `app/core/security.py` — auth middleware
- `app/core/exceptions.py` — `PlaceNotFoundError`
- Google Places API (New) — Place Details Essentials SKU

**Support Files / References**
- `app/api/API_Autocomplete.py`
- `app/services/autocomplete_service.py`
- `app/routers/search.py`
- `tests/unit/test_routes_search.py`
- `commandes.md`

**Notes / Comments**
- SKU Place Details Essentials : free cap 10,000/month → $0.005 beyond
- FieldMask : `id,location,formattedAddress` — only Essentials fields
- `session_token` closes the Android autocomplete session → autocomplete becomes free
- `viewport` intentionally excluded — not needed for map centering
```

### What to copy

- **Success criteria name exact status codes** (`422`, `400`) and the exact response fields — not
  "handles errors properly".
- **Dependencies point at real files already in the codebase**, not generic categories.
- The `Notes / Comments` section carries the non-obvious rationale (why this SKU, why `viewport` was
  left out) — exactly the kind of thing a future reader can't re-derive from the code alone.

## Example 2 — `SOR-231`, a bug fix (Bug, Priority 0 - Critical)

```markdown
### Description of the task
The app generates its own unique session identifier on the client side when a user starts a place search (Autocomplete). This identifier needs to be passed through the backend, from the `/attraction/by_name` endpoint down to the Google Places Place Details API call, where it is sent as Google's `sessionToken` parameter. This links the Autocomplete search and the subsequent Place Details lookup into a single Google billing session, even though the token itself is generated and owned by our own app rather than by a Google SDK.

### Purpose / Objective
Google bills Autocomplete and Place Details as a single, discounted "session" when both calls share the same `sessionToken`. Since our app generates this identifier itself (rather than relying on Google's client-side SDK to do so), the backend needs to accept it as an optional parameter and forward it untouched to Google on the Place Details request. This reduces Google Places API costs by ensuring related search-then-lookup flows are correctly billed as one session, while keeping the parameter fully optional so flows that don't originate from an Autocomplete search (e.g. coordinate-based lookups) are unaffected.

### Success Criteria / Test
- `GET /attraction/by_name` accepts an optional `session_token` query parameter (the app-generated identifier).
- When provided, the token is forwarded unchanged through `PlacesService.get_tourist_attraction` and included as `sessionToken` in the Google Place Details API request.
- When omitted, the endpoint behaves exactly as before — no `sessionToken` sent to Google, no errors.
- `GET /attraction/by_coordinates` remains unchanged and does not require/accept a session token, since it isn't part of an Autocomplete-driven search flow.
- Unit test `test_get_attraction_by_name_with_session_token` passes, verifying `get_tourist_attraction` is called with the correct `place_id` and `session_token`.
- All existing tests in `test_routes_attractions.py` continue to pass.
- App boots and test suite collects without `NameError` (missing `Optional` import fixed).

### Sub-tasks / Tasks
- [x] Add `session_token: Optional[str] = None` query parameter to `GET /attraction/by_name`
- [x] Propagate `session_token` through `PlacesService.get_tourist_attraction`
- [x] Propagate `session_token` through the module-level `get_tourist_attraction` function
- [x] Forward the app-generated token as Google's `sessionToken` query param on the Place Details API call when present
- [x] Confirm `GET /attraction/by_coordinates` intentionally left without `session_token` (not an Autocomplete-originated flow)
- [x] Add `from typing import Optional` import to `app/routers/attraction.py` to fix `NameError`
- [x] Add unit test covering the `session_token` propagation on `by_name`
- [x] Run full test suite to confirm no regressions

### Dependencies
- Existing `PlacesService.get_place_id` (Autocomplete call) — needs the same app-generated token passed in by the frontend during Autocomplete, so that Google sees the same `sessionToken` on both calls. Worth confirming this is consistent end-to-end.
- Google Places API (New) — Place Details endpoint, `sessionToken` query parameter.

### Support Files / References
- [Google Places API — Session Tokens documentation](https://developers.google.com/maps/documentation/places/web-service/place-session-tokens)
- `app/routers/attraction.py`
- `app/services/places_service.py` (or equivalent service file)
- `tests/unit/test_routes_attractions.py`

### Notes / Comments
- The token is generated by our own app (not Google's client SDK), so it's our responsibility to ensure uniqueness and proper lifecycle (one token per search session, discarded after the Details call completes) for Google's billing rules to apply correctly.
- Should confirm with frontend that the same token used during Autocomplete is the one passed to `by_name`, otherwise the session grouping on Google's side won't work as intended.
- Token is intentionally optional everywhere in the chain so the coordinates-based lookup flow, which has no associated search session, is unaffected.
```

### What to copy

- **`Purpose / Objective` explains the billing mechanism**, not just "pass the token through" — the
  reviewer needs to understand *why* a session token matters to judge the change.
- A **known uncertainty is written down as a note** ("Should confirm with frontend…") rather than
  silently assumed — never invent that the frontend side is already confirmed.
- One sub-task is explicitly a bug fix found along the way (`NameError` from a missing import) — it's
  fine for a ticket to grow slightly during implementation, but it must be *recorded*, not left
  implicit.
