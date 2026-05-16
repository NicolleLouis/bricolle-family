# AODP Request Logs Implementation Plan

Architecture source: `.beaver/human/architecture/aodp-request-logs.md`

## Planning Assumptions

- There are no blocking open questions left in the architecture.
- No Celery beat task will be added; retention is handled opportunistically at the start of AODP price fetches.
- The request log write path must remain confined to `AlbionOnlineDataPriceFetcher` or private helpers it alone calls.
- Search is substring-based on the stored request query and response body, not full-text indexed search.
- The UI page is a normal `albion_online` page and must be linked from the app header.

## Execution Rules

- One ticket should be handled by one LLM agent.
- Only one ticket should be `ongoing` unless the user explicitly chooses parallel execution.
- A ticket can move to `done` only after its implementation and validation steps are complete.
- If a ticket reveals missing architecture decisions, update the architecture and this plan before continuing.

## Phase 0 - Schema And Persistence Primitives

### AODP-001 - Add the AODP request log model, admin, and migration

Status: `done`

Goal:
- Add a durable table for AODP request logs with fields for source, request query, response body, status, error state, duration, and timestamps.

Context:
- Architecture sections: `Data Model`, `Key Decisions`, `Files Expected To Change`.
- Relevant files or areas: `albion_online/models/`, `albion_online/migrations/`, `albion_online/tests/`, `albion_online/models/__init__.py`.

Scope:
- Create `albion_online/models/aodp_request_log.py`.
- Register the model in the same module with a `ModelAdmin`.
- Export the model from `albion_online/models/__init__.py`.
- Add the Django migration for the new table and indexes.
- Add model-focused tests for ordering, `__str__`, and admin search fields if needed.

Out of scope:
- Fetcher instrumentation.
- Search or purge service logic.
- Frontend pages and routing.
- Any write path outside the fetcher pipeline.

Implementation notes:
- Use `TextField` for the stored query and response body.
- Add an index on `created_at` because purge and default ordering depend on it.
- Keep the admin search fields aligned with the expected debug workflow.
- Keep the schema small and explicit; do not add headers or unrelated payloads.

Acceptance criteria:
- The model exists with the expected fields and indexes.
- The model is registered in the admin from its module.
- The model is importable from `albion_online.models`.
- A migration is generated and applies cleanly.

Validation:
- Command: `poetry run python manage.py makemigrations --check`
- Command: `poetry run pytest albion_online/tests/test_aodp_request_log_model.py`
- Manual check: inspect the generated migration for the expected fields and indexes.

Dependencies:
- None.

Risks:
- A wrong field type or missing index will make later search and purge work unnecessarily expensive.

### AODP-002 - Add request log read/search/purge helpers

Status: `done`

Goal:
- Add the internal helper layer that reads, filters, formats, and purges logs without creating any write path outside the price fetcher.

Context:
- Architecture sections: `Proposed Architecture`, `Backend Flow`, `Observability And Operations`, `Edge Cases`.
- Relevant files or areas: `albion_online/services/`, `albion_online/tests/`, `albion_online/models/aodp_request_log.py`.

Scope:
- Create `albion_online/services/aodp_request_log_service.py`.
- Implement log listing and substring search on request query and response body.
- Implement best-effort purge of logs older than 24 hours.
- Add a private write helper that is only intended to be called by `price_fetcher.py`.
- Add service tests for filtering, purge cutoff, and display normalization if needed.

Out of scope:
- Calling the write helper from anywhere except the fetcher.
- UI rendering.
- URL routing.
- Changes to the actual HTTP fetch logic beyond the helper contract.

Implementation notes:
- Keep the read API simple enough for a Django view to consume directly.
- Make the purge idempotent and safe to call on every fetch.
- Do not introduce full-text search or a separate search backend.
- Keep the write helper private or narrowly scoped so its only caller is the fetcher.

Acceptance criteria:
- The service can return logs filtered by a free-text string.
- The service can purge records older than 24 hours.
- The service exposes no public write path that other parts of the app can use casually.
- Tests cover the search and purge behavior.

Validation:
- Command: `poetry run pytest albion_online/tests/test_aodp_request_log_service.py`
- Manual check: verify the service does not expose a general-purpose create API used by views or tasks.

Dependencies:
- `AODP-001`

Risks:
- If the helper API is too broad, another code path may start writing logs outside the fetcher.

## Phase 1 - Fetch Path Instrumentation

### AODP-003 - Instrument the price fetcher with non-blocking log persistence and purge

Status: `done`

Goal:
- Persist AODP request logs only from the price fetcher path, and make the purge best-effort so it never blocks the actual fetch.

Context:
- Architecture sections: `Current State`, `Backend Flow`, `Key Decisions`, `Rollout And Migration`.
- Relevant files or areas: `albion_online/services/price_fetcher.py`, `albion_online/tests/test_price_fetcher.py`, `albion_online/services/aodp_request_log_service.py`.

Scope:
- Update `AlbionOnlineDataPriceFetcher` so each outgoing request can record its request query and response body.
- Make sure error responses are still captured before `raise_for_status()` interrupts the flow.
- Run opportunistic purge of expired logs at the start of the fetch path.
- Keep purge failure non-blocking for the network call and the rest of the fetch.
- Update `albion_online/tests/test_price_fetcher.py` to cover success, error, and purge failure behavior.

Out of scope:
- Any logging from views, tasks, templates, or other services.
- Frontend rendering.
- New background workers or Celery tasks.
- Changing the business meaning of the fetched price payload.

Implementation notes:
- Capture the response body before raising for HTTP errors so debug data is preserved.
- If purge fails, log the purge error and continue the fetch.
- Keep the write path limited to the fetcher or its private helper contract.
- Do not move price parsing or batching concerns out of the existing fetcher.

Acceptance criteria:
- A successful AODP call creates a log entry with query and response body.
- An HTTP error still creates a log entry that can be rendered as an error.
- A purge failure does not abort the fetch or suppress the AODP call.
- No other app code writes AODP logs directly.

Validation:
- Command: `poetry run pytest albion_online/tests/test_price_fetcher.py`
- Manual check: inspect the request log rows after a fetch and after an induced HTTP failure.

Dependencies:
- `AODP-001`
- `AODP-002`

Risks:
- If the logging hooks are placed after `raise_for_status()`, the debug body for failures will be lost.
- If purge errors are allowed to bubble, the fetch path becomes fragile.

## Phase 2 - Frontend Exposure

### AODP-004 - Add the AODP request log page, route, and navigation entry

Status: `done`

Goal:
- Expose a searchable front page for AODP request logs and make it reachable from the Albion header.

Context:
- Architecture sections: `Frontend Flow`, `Authorization And Feature Gates`, `Files Expected To Change`.
- Relevant files or areas: `albion_online/views/`, `albion_online/templates/albion_online/`, `albion_online/urls.py`, `albion_online/templates/albion_online/header.html`, `albion_online/templates/albion_online/home.html`, `albion_online/tests/`.

Scope:
- Create a list view for request logs with free-text filtering.
- Create the corresponding template with readable query and response body rendering.
- Add the route in `albion_online/urls.py`.
- Add the header navigation entry as the primary way to reach the page.
- Add a home page link if it helps discovery without replacing the header link.
- Add tests for page rendering, filtering, and navigation entry presence.

Out of scope:
- Modifying the write path.
- Changing the model schema.
- Adding separate permissions or feature flags.
- Adding a second API or JSON endpoint for the logs.

Implementation notes:
- Keep the page Bootstrap-friendly and consistent with the rest of `albion_online`.
- Show error rows in a visibly distinct style.
- Render the request query and response body in a readable, scroll-safe way.
- Use the service from ticket `AODP-002` rather than reimplementing search in the view.

Acceptance criteria:
- The page is reachable from the Albion header.
- The page shows recent logs and supports string search.
- Error rows are visibly highlighted.
- The page still works with the app’s existing access rules.

Validation:
- Command: `poetry run pytest albion_online/tests/test_aodp_request_log_view.py`
- Command: `poetry run pytest albion_online/tests/test_home_view.py albion_online/tests/test_settings_view.py`
- Manual check: click through the header link and confirm the page loads with the expected filters.

Dependencies:
- `AODP-001`
- `AODP-002`
- `AODP-003`

Risks:
- If the template leans on raw bodies without formatting, the page will be hard to scan.
- If the header link is missed, the feature will be effectively hidden despite working code.

## Phase 3 - Tightening And Regression Coverage

### AODP-005 - Add integration coverage and clean up any cross-cutting fallout

Status: `not started`

Goal:
- Close any gaps left by the new logging feature with focused regression tests and any necessary import or navigation fixes.

Context:
- Architecture sections: `Testing Strategy`, `Rollout And Migration`, `Files Expected To Change`.
- Relevant files or areas: `albion_online/tests/`, `albion_online/models/__init__.py`, `albion_online/templates/albion_online/header.html`, `albion_online/templates/albion_online/home.html`.

Scope:
- Add or extend tests that prove the log page, header link, and fetch logging work together.
- Fix any import/export gaps introduced by the new model and service modules.
- Verify the final migration and test suite state after the feature is wired end to end.

Out of scope:
- New product behavior.
- Schema redesign.
- Broad refactors unrelated to AODP logs.

Implementation notes:
- Prefer small targeted regression tests over a large end-to-end test that is hard to debug.
- Keep the last pass focused on what actually regressed while wiring the previous tickets.

Acceptance criteria:
- The feature has at least one test covering each of the three joints: model/service, fetcher, and UI.
- No unresolved import or route breakage remains.
- The implementation is ready to ship without relying on manual verification only.

Validation:
- Command: `poetry run pytest albion_online/tests/test_aodp_request_log_model.py albion_online/tests/test_aodp_request_log_service.py albion_online/tests/test_price_fetcher.py albion_online/tests/test_aodp_request_log_view.py`
- Command: `poetry run python manage.py makemigrations --check`

Dependencies:
- `AODP-001`
- `AODP-002`
- `AODP-003`
- `AODP-004`

Risks:
- A small import or template registration mistake can hide behind otherwise green unit tests if this final pass is skipped.
