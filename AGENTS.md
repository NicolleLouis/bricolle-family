# Repository Guidelines

## Project Structure & Module Organization

This repository hosts a multi-app Django project. Core configuration and global templates live in `bricolle_family/`;
shared helpers sit in `core/`. Feature apps (e.g., `baby_name`, `altered`) keep their own URLs, models, and templates,
with tests under `<app>/tests/`. New apps must follow the house layout: sibling folders `templates/`, `models/`,
`views/`, and `services/`. Static assets stay in `static/` (collected to `staticfiles/`), uploads in `media/`, and
deployment helpers remain at the root.

## Build, Test, and Development Commands

Install dependencies with `poetry install`. Use `make start` (alias for `poetry run python manage.py runserver`). Run
schema updates via `make migrate`, generate migrations with `make migrations`, and execute tests with `make test`. For
asset collection, run `make collectstatic`. Docker workflows use `./deploy.sh` and
`docker compose exec web python manage.py ...`.

## Migration

You should never update an existing migration but instead creating a new one reflecting the changes. You can use the
command make_migrations for that

## Coding Style & Naming Conventions

Target Python 3.11 and follow PEP 8: four-space indentation, `snake_case` for modules/functions, `CamelCase` for
classes. Define each model alongside its `ModelAdmin` in the same module and register both there—no model ships without
admin coverage. Place business logic in service modules inside each app’s `services/` directory; views should stay thin
and delegate work. Every public service function requires matching tests. Every service should be a class with as little
public function as possible and private function to split the logic and have a readable file. Templates use Django block
syntax; name them
after their route (`baby_name/index.html`) and use Bootstrap-friendly markup (`django-bootstrap-v5`).
Avoid variable names that are contractions or abbreviations; prefer full, descriptive names.

## Template & App Scaffolding

Each app’s `templates/` directory must provide three base files:

- `header.html`: renders navigation, with the app name on the left linking to the app home and an admin button on the
  right targeting `/admin/{app_name}`.
- `base.html`: shared layout for every page in the app.
- `home.html`: landing page extending `base.html`.
  Keep reusable fragments in `{% include %}` files to stay DRY and ensure navigation also exposes the global home when
  relevant.

## Testing Guidelines

Tests run with `pytest` and `pytest-django` (see `pytest.ini`). Store tests in `<app>/tests/`, name files
`test_<subject>.py`, and use descriptive `Test...` classes or `test_` functions. Cover service-layer logic first, adding
view or integration tests where behaviour crosses boundaries. Use `factory_boy` for non-trivial data. Confirm the suite
passes on SQLite and, when needed, PostgreSQL through Docker.

## Configuration & Environment

Secrets load through `python-decouple`; define `.env` keys such as `SECRET_KEY`, `ENV`, and `DATABASE_URL`. Local
development uses SQLite (`db.sqlite3`); production expects PostgreSQL via `DATABASE_URL`. Static files rely on
WhiteNoise in production, so run `make collectstatic` before deploying. Use
`docker compose exec web python manage.py <command>` for admin tasks inside containers.
