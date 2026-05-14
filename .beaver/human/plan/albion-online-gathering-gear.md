# Albion Online Gathering Gear Implementation Plan

Architecture source: `.beaver/human/architecture/albion-online-gathering-gear.md`

## Planning Assumptions

- The architecture is ready for execution: all product decisions are fixed, including the single-page UX, the `All` city option, the default `Fort Sterling` + `Ore` filters, the side panel, and the profitability tab.
- The implementation should reduce duplication by extracting a shared core between `Leather Jacket` and `Gathering Gear`, then keeping feature-specific wrappers only where route or naming clarity matters.
- Recipe seeding must cover only the objects listed in the architecture file.
- Existing `Leather Jacket` behavior must remain stable while the new feature is introduced.

## Execution Rules

- One ticket should be handled by one LLM agent.
- Only one ticket should be `ongoing` unless the user explicitly chooses parallel execution.
- A ticket can move to `done` only after its implementation and validation steps are complete.
- If a ticket reveals missing architecture decisions, update the architecture and this plan before continuing.

## Phase 0 - Shared Core Extraction

### GEAR-001 - Extract shared Albion market core

Status: `done`

Goal:
- Extract the shared market logic used by `Leather Jacket` into reusable helpers/services that can power `Gathering Gear` without duplicating the refresh, summary, cache, and profitability mechanics.

Context:
- Architecture sections: `Key Decisions`, `Proposed Architecture`, `Services`, `Backend Flow`
- Relevant files or areas:
  - `albion_online/views/leather_jacket.py`
  - `albion_online/services/mercenary_jacket_price_refresh.py`
  - `albion_online/services/mercenary_jacket_market_summary.py`
  - `albion_online/services/leather_jacket_profitability.py`
  - `albion_online/constants/leather_jacket.py`

Scope:
- Introduce a shared market core that accepts feature configuration for object selection, route names, cache keys, default filters, and resource taxonomies.
- Keep `Leather Jacket` behavior intact by wiring it through the shared core or thin wrappers.
- Preserve the current public behavior of existing leather jacket routes and templates.

Out of scope:
- New routes for `Gathering Gear`.
- Migration data.
- Template redesign.
- Any change to the underlying price fetcher contract.

Implementation notes:
- Prefer a small, explicit configuration object or module-level constant set over a deep inheritance hierarchy.
- Keep the shared core generic enough to support the future `Gathering Gear` page without hardcoding jacket-specific fragments.

Acceptance criteria:
- Existing `Leather Jacket` view still renders and refreshes correctly.
- Shared logic is no longer duplicated between the jacket refresh and summary paths.
- The shared core can be configured for a second feature without rewriting the implementation.

Validation:
- Command: `poetry run pytest albion_online/tests/test_leather_jacket_view.py albion_online/tests/test_mercenary_jacket_price_refresh_service.py albion_online/tests/test_mercenary_jacket_market_summary_service.py`

Dependencies:
- None.

Risks:
- A too-aggressive refactor could subtly change cache behavior or detail panel rendering for the existing jacket page.

## Phase 1 - Gathering Gear Data and Domain Seeds

### GEAR-002 - Add gathering gear constants and seed recipes

Status: `done`

Goal:
- Add the `Gathering Gear` domain constants and the data migrations that seed all recipe definitions described in the architecture.

Context:
- Architecture sections: `Data Model`, `Seed Recipes Confirmed`, `Rollout And Migration`
- Relevant files or areas:
  - `albion_online/constants/`
  - `albion_online/migrations/`
  - `albion_online/models/recipe.py`
  - `albion_online/services/recipe_generation.py`

Scope:
- Create a dedicated constants module for gathering gear types and resource groupings.
- Add a data migration that seeds `RecipeDefinition` rows for:
  - Ore: Miner Cap, Miner Garb, Miner Workboot, Miner Backpack
  - Fiber: Harvester Cap, Harvester Garb, Harvester Workboot, Harvester Backpack
  - Wood: Lumberjack Cap, Lumberjack Garb, Lumberjack Workboot, Lumberjack Backpack
  - Stone: Quarrier Cap, Quarrier Garb, Quarrier Workboot, Quarrier Backpack
  - Hide: Skinner Cap, Skinner Garb, Skinner Workboot, Skinner Backpack
- Ensure recipes with mixed inputs are represented correctly.

Out of scope:
- View or template changes.
- Route additions.
- Refresh or profitability logic.
- Backfilling any historical objects outside the listed seeds.

Implementation notes:
- Use `update_or_create` in the migration so repeated applies remain idempotent.
- Keep the config shape compatible with `RecipeGenerationService`.
- If a `BACKPACK` output needs an AODP fragment match, encode that explicitly in the migration config rather than assuming it can be inferred.

Acceptance criteria:
- All listed gatherer recipe definitions exist after migration.
- `RecipeGenerationService` can rebuild recipes from the new definitions without custom code paths.
- The migration is deterministic and idempotent.

Validation:
- Command: `poetry run pytest albion_online/tests/test_recipe_generation_service.py`
- Command: `poetry run python manage.py migrate`

Dependencies:
- GEAR-001 is preferred first if the migration config will reference shared feature constants.

Risks:
- If the seed config is wrong, recipe generation will silently produce missing or incorrect outputs for the new page.

## Phase 2 - Gathering Gear Market Flow

### GEAR-003 - Implement gathering gear refresh and summary flow

Status: `done`

Goal:
- Build the gathering gear backend flow for price refresh, market summary, detail side panel data, and profitability calculations.

Context:
- Architecture sections: `Backend Flow`, `Proposed Architecture`, `Frontend Flow`
- Relevant files or areas:
  - `albion_online/views/`
  - `albion_online/services/`
  - `albion_online/constants/`
  - `albion_online/models/`
  - `albion_online/templatetags/`

Scope:
- Add the `Gathering Gear` page view and profitability view.
- Add the detail-panel endpoint for gathering gear rows.
- Wire the page to the shared market core created in GEAR-001.
- Implement resource-specific filtering, with `Ore` as the default and `All` as an available city option.
- Ensure refresh requests are split by resource category.

Out of scope:
- Final template styling polish.
- Recipe seeding.
- Changing the existing leather jacket routes beyond what is needed to share code.

Implementation notes:
- Keep the page single-route and single-page, with resource filtering handled by query parameters.
- Reuse the same freshness, margin, and offcanvas structure as the jacket page.
- Preserve the existing trade fee and return-rate behavior, including the city-specific override support.

Acceptance criteria:
- `Gathering Gear` refreshes prices successfully.
- The page renders a market table filtered by city and resource.
- The profitability view works without a resource filter.
- The detail side panel loads asynchronously for gathering gear rows.

Validation:
- Command: `poetry run pytest albion_online/tests/test_leather_jacket_view.py`
- Command: `poetry run pytest albion_online/tests/test_mercenary_jacket_market_summary_service.py`
- Command: `poetry run pytest albion_online/tests/test_mercenary_jacket_price_refresh_service.py`

Dependencies:
- GEAR-001
- GEAR-002

Risks:
- The shared core could regress the existing jacket page if the configuration boundary is too leaky.

## Phase 3 - Gathering Gear Frontend

### GEAR-004 - Add gathering gear templates and navigation

Status: `done`

Goal:
- Add the frontend pages, templates, and navigation entry for gathering gear, including the market table, profitability tab, and side panel UX.

Context:
- Architecture sections: `Frontend Flow`, `Proposed Architecture`, `Authorization And Feature Gates`
- Relevant files or areas:
  - `albion_online/templates/albion_online/`
  - `albion_online/urls.py`
  - `albion_online/views/home.py`
  - `albion_online/templates/albion_online/header.html`

Scope:
- Add the gathering gear route entries.
- Create the gathering gear market template.
- Create the gathering gear profitability template if the implementation uses separate templates.
- Add the header navigation link to the new page.
- Preserve the city filter `All` option and the default `Fort Sterling` + `Ore` landing state.

Out of scope:
- Backend domain logic.
- Data migrations.
- Changing existing jacket templates except for shared partial reuse if needed.

Implementation notes:
- Prefer shared template fragments only where they reduce duplication without making the page harder to read.
- Keep the template behavior consistent with existing bootstrap styling and offcanvas loading.

Acceptance criteria:
- The new page is reachable from the app navigation.
- The market page renders with the expected filters and the side panel.
- The profitability tab is present and functional.
- The initial state lands on `Fort Sterling` and `Ore`.

Validation:
- Command: `poetry run pytest albion_online/tests/test_home_view.py`
- Command: `poetry run pytest albion_online/tests/test_settings_view.py`
- Manual check: open the new page, verify the market table, profitability tab, and side panel interactions.

Dependencies:
- GEAR-003

Risks:
- Template duplication could creep back in if shared partials are not introduced carefully.

## Phase 4 - Verification and Cleanup

### GEAR-005 - Add targeted tests and finalize cleanup

Status: `not started`

Goal:
- Close the implementation with targeted tests around the new page, the migration-backed seeds, and the shared behavior between features.

Context:
- Architecture sections: `Testing Strategy`, `Edge Cases`, `Rollout And Migration`
- Relevant files or areas:
  - `albion_online/tests/`
  - `albion_online/migrations/`
  - `albion_online/views/`

Scope:
- Add or update tests for:
  - gathering gear view rendering
  - city/resource default handling
  - profitability behavior without resource filtering
  - detail panel endpoint
  - migration-driven recipe generation
  - shared core compatibility with existing jacket behavior
- Remove temporary scaffolding or compatibility code that is no longer needed.

Out of scope:
- New product scope.
- Further feature expansion.

Implementation notes:
- Test the new feature end-to-end at the smallest useful boundary, but keep the jacket regression coverage intact.
- If a shared abstraction is difficult to validate, add a direct unit test for the core helper and a narrow integration test for each feature wrapper.

Acceptance criteria:
- The new gathering gear flow has direct regression coverage.
- Existing leather jacket behavior remains covered.
- The plan can be completed without unresolved architectural questions.

Validation:
- Command: `poetry run pytest albion_online/tests`
- Command: `poetry run python manage.py check`

Dependencies:
- GEAR-001
- GEAR-002
- GEAR-003
- GEAR-004

Risks:
- Cross-feature regressions can be missed if the test matrix does not cover both the shared core and the feature wrappers.
