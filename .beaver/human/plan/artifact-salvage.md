# Artifact Salvage Implementation Plan

Architecture source: `.beaver/human/architecture/artifact-salvage.md`

## Planning Assumptions

- The architecture is ready enough to plan; the only unresolved detail is the rounding convention for `buy_order_price`.
- The plan treats `sell_price_min` as the only displayed price source, exactly as the architecture specifies.
- The canonical AODP label mapping from the architecture is the source of truth for code-level matching.
- `city=all` is out of scope for this page.
- The page is a single route with no profitability sub-page.

## Execution Rules

- One ticket should be handled by one LLM agent.
- Only one ticket should be `ongoing` unless the user explicitly chooses parallel execution.
- A ticket can move to `done` only after its implementation and validation steps are complete.
- If a ticket reveals missing architecture decisions, update the architecture and this plan before continuing.

## Phase 0 - Data Contracts And Calculations

### ART-SALVAGE-001 - Add artifact salvage catalog constants

Status: `done`

Goal:
- Add the canonical artifact salvage catalog to the codebase as a Python constant module.
- Preserve the four families `rune`, `soul`, `relic`, and `avalonian`.
- Encode stable matching data for each artifact using the AODP fragment, not the raw user spelling.

Context:
- Architecture sections: `Key Decisions`, `Proposed Architecture`, `Files Expected To Change`.
- Relevant files or areas: `albion_online/constants/` and nearby tests.

Scope:
- Create `albion_online/constants/artifact_salvage.py`.
- Represent each family and each artifact in a code-friendly structure.
- Add any helper lookups needed for family filtering or matching.
- Add focused tests validating the full catalog contents and the canonical mappings.

Out of scope:
- Views, templates, tasks, or routing.
- Pricing calculations.
- Price refresh job wiring.

Implementation notes:
- Keep the data structure easy to iterate from a service.
- Use canonical AODP labels from the architecture, including the corrected names.
- Make sure the single ambiguous item is already resolved to `Hellish Sicklehead Pair`.

Acceptance criteria:
- The module exposes the four families and their artifacts in a deterministic structure.
- Every artifact has a stable AODP fragment usable for `Object.aodp_id__contains` matching.
- Tests prove the catalog contains the expected entries for all four families.

Validation:
- Command: `poetry run pytest albion_online/tests/test_artifact_salvage_constants.py`
- Manual check: inspect the constant structure for obvious spelling or family assignment mistakes.

Dependencies:
- None.

Risks:
- A wrong canonical label will propagate into downstream queries and UI labels.

### ART-SALVAGE-002 - Build salvage pricing service and formula tests

Status: `done`

Goal:
- Implement the backend service that builds the artifact salvage page data.
- Centralize the `buy_order_price` calculation and the green/red classification.

Context:
- Architecture sections: `Target Behavior`, `Backend Flow`, `Calculation`, `Open Questions`.
- Relevant files or areas: `albion_online/services/`, `albion_online/tests/`, `albion_online/services/market_summary_querysets.py`, `albion_online/models/price.py`.

Scope:
- Create `albion_online/services/artifact_salvage_market_summary.py`.
- Build the per-family, per-tier row structure expected by the template.
- Read the latest city prices from the prefetched `Price` rows.
- Calculate the shard base line as `10 * shard_price`.
- Calculate `buy_order_price` using the architecture formula and the chosen rounding convention.
- Classify colors with the `120%` threshold rule from the architecture.
- Add service tests for formula correctness, family grouping, missing price behavior, and color classification.

Out of scope:
- Refresh job orchestration.
- URL routing and views.
- Template rendering details.

Implementation notes:
- Reuse the existing summary-queryset helpers where possible.
- Keep the service pure and easy to unit test.
- Resolve the rounding convention inside this ticket if it is not already encoded elsewhere.
- Use the exact `0.935` sale factor from the architecture.

Acceptance criteria:
- Given mocked price inputs, the service returns the expected section and row structures.
- `buy_order_price` is computed consistently and tested.
- A price below `120%` of the threshold is classified green; otherwise red.
- Missing prices or incomplete tier coverage are handled without exceptions.

Validation:
- Command: `poetry run pytest albion_online/tests/test_artifact_salvage_service.py`
- Command: `poetry run pytest albion_online/tests/test_price_model.py albion_online/tests/test_price_fetcher.py`
- Manual check: verify the service output shape matches the architecture section `Rendering`.

Dependencies:
- `ART-SALVAGE-001`

Risks:
- A rounding mismatch will change the threshold boundary and may cause off-by-one UI differences.

## Phase 1 - Refresh Pipeline And Persistence

### ART-SALVAGE-003 - Wire artifact salvage refresh job and cache invalidation

Status: `done`

Goal:
- Make artifact salvage refreshable through the existing async job pipeline.
- Add the new job kind and invalidate the page cache on success.

Context:
- Architecture sections: `Data Model`, `Backend Flow`, `Observability And Operations`, `Rollout And Migration`.
- Relevant files or areas: `albion_online/models/price_refresh_job.py`, `albion_online/tasks.py`, `albion_online/services/price_refresh_cache.py`, `albion_online/services/`.

Scope:
- Add `PriceRefreshJob.Kind.ARTIFACT_SALVAGE`.
- Add a cache version key and invalidation helper for artifact salvage.
- Create `albion_online/services/artifact_salvage_price_refresh.py`.
- Update `albion_online/tasks.py` so the new job kind executes the new service and invalidates cache.
- Add or update tests for job execution and cache invalidation.
- Generate the required migration for the new `PriceRefreshJob.Kind` choice.

Out of scope:
- The page view and HTML template.
- The artifact catalog itself.
- Any unrelated refresh jobs.

Implementation notes:
- Follow the same grouped refresh pattern used by `gathering_gear` and `leather_jacket`.
- Keep the refresh independent of the selected city unless the architecture changes.
- Ensure the refresh still logs and marks job success/failure like the existing flow.

Acceptance criteria:
- A queued artifact salvage job runs through `refresh_price_job`.
- Success invalidates the artifact salvage cache.
- A new migration records the model choice update.
- Tests cover both success and failure paths for the new kind.

Validation:
- Command: `poetry run pytest albion_online/tests/test_price_refresh_task.py`
- Command: `poetry run pytest albion_online/tests/test_artifact_salvage_price_refresh_service.py`
- Command: `poetry run python manage.py makemigrations --check`

Dependencies:
- `ART-SALVAGE-001`

Risks:
- Missing or incorrect job-kind wiring will leave the refresh button non-functional even if the page renders.

## Phase 2 - Page Rendering

### ART-SALVAGE-004 - Add artifact salvage view, route, and template

Status: `done`

Goal:
- Expose the new artifact salvage page through Django routing and render the new UI.

Context:
- Architecture sections: `Frontend Flow`, `Authorization And Feature Gates`, `Files Expected To Change`.
- Relevant files or areas: `albion_online/views/`, `albion_online/templates/albion_online/`, `albion_online/urls.py`, `albion_online/tests/`.

Scope:
- Create `albion_online/views/artifact_salvage.py`.
- Add the `artifact_salvage` route to `albion_online/urls.py`.
- Create `albion_online/templates/albion_online/artifact_salvage.html`.
- Render the city selector, refresh button, job banner, and the four family tables.
- Use the new service from the view.
- Add view/template tests covering GET rendering and POST refresh redirect behavior.

Out of scope:
- Internal calculation logic already covered by the service ticket.
- Refresh job wiring already covered by the task ticket.
- Home/header link updates.

Implementation notes:
- Mirror the sticky header and refresh banner behavior from the existing market pages.
- Keep the template simple and Bootstrap-friendly.
- Do not add the offcanvas detail panel or any profitability sub-page.

Acceptance criteria:
- The page loads at a new route with the expected title and sections.
- The selected city persists through GET/POST interactions.
- The refresh button triggers the job flow and renders the status banner.
- Tests cover the happy path and invalid city fallback.

Validation:
- Command: `poetry run pytest albion_online/tests/test_artifact_salvage_view.py`
- Command: `poetry run pytest albion_online/tests/test_artifact_salvage_service.py albion_online/tests/test_artifact_salvage_view.py`

Dependencies:
- `ART-SALVAGE-001`
- `ART-SALVAGE-002`
- `ART-SALVAGE-003`

Risks:
- Template shape drift from the existing pages can make the new page inconsistent or harder to maintain.

## Phase 3 - Entry Points And Integration

### ART-SALVAGE-005 - Add navigation links and finish integration tests

Status: `not started`

Goal:
- Make the new page discoverable from the app entry points.
- Close the loop with integration-level tests.

Context:
- Architecture sections: `Files Expected To Change`, `Rollout And Migration`, `Testing Strategy`.
- Relevant files or areas: `albion_online/templates/albion_online/home.html`, `albion_online/templates/albion_online/header.html`, `albion_online/tests/`.

Scope:
- Add the new page link to the home page.
- Add the new page link to the header navigation if that matches the existing app style.
- Update or add tests that verify the page is reachable from the main navigation.
- Add any remaining end-to-end assertions that the page renders the four sections and the refresh banner.

Out of scope:
- Core calculation logic.
- Job wiring.
- Route creation.

Implementation notes:
- Keep navigation changes minimal and consistent with the current visual language.
- If a home or header test becomes too broad, split it into focused assertions.

Acceptance criteria:
- The home page exposes the new page.
- The header navigation exposes the new page if the design uses it.
- Tests confirm the link and page render correctly together.

Validation:
- Command: `poetry run pytest albion_online/tests/test_home_view.py albion_online/tests/test_artifact_salvage_view.py`
- Command: `poetry run pytest albion_online/tests/test_*artifact*`

Dependencies:
- `ART-SALVAGE-004`

Risks:
- Navigation updates can fail silently if the wrong template fragment is edited.

## Phase 4 - Cleanup And Review

### ART-SALVAGE-006 - Review, tighten, and document the final behavior

Status: `not started`

Goal:
- Verify the implementation is internally consistent and update the architecture or plan if any real-world mismatch appears.

Context:
- Architecture sections: all of them, especially `Open Questions`, `Testing Strategy`, and `Observability And Operations`.
- Relevant files or areas: the full `albion_online` artifact salvage slice.

Scope:
- Run the targeted artifact salvage tests.
- Fix any mismatched labels, rounding discrepancies, or cache issues uncovered by earlier tickets.
- Update the architecture or plan only if new facts emerge during implementation.

Out of scope:
- New feature scope.
- Extra refactors unrelated to artifact salvage.

Implementation notes:
- Treat this as a stabilization pass, not a feature expansion pass.
- Keep the write scope limited to the files needed to close any gaps found during validation.

Acceptance criteria:
- The new page, service, refresh pipeline, and navigation all work together.
- No open architecture question remains unresolved in the implementation.

Validation:
- Command: `poetry run pytest albion_online/tests/test_artifact_salvage* albion_online/tests/test_price_refresh_task.py`
- Command: `poetry run pytest albion_online/tests/test_home_view.py albion_online/tests/test_leather_jacket_view.py albion_online/tests/test_gathering_gear_view.py`

Dependencies:
- `ART-SALVAGE-001`
- `ART-SALVAGE-002`
- `ART-SALVAGE-003`
- `ART-SALVAGE-004`
- `ART-SALVAGE-005`

Risks:
- Final polish can turn into scope creep if new behaviors are added instead of only aligning the implementation with the architecture.
