---
name: create-new-app
description: Use when adding a new Django app in this repository. Creates the required app tree (models, views, services, templates), adds base/home/header templates, and wires a button on the global home cards.
---

# Create New App

Use this workflow whenever a new app is added to this repository.

## 1. Create app scaffold

Create the app folder and required house structure:

- `<app_name>/models/`
- `<app_name>/views/`
- `<app_name>/services/`
- `<app_name>/templates/<app_name>/`

Also create:

- `<app_name>/migrations/`
- `<app_name>/tests/`
- `<app_name>/__init__.py`
- `<app_name>/apps.py`
- `<app_name>/urls.py`
- `__init__.py` in `models/`, `views/`, `services/`, `migrations/`, `tests/`

Keep naming in `snake_case` for app and files.

## 2. URL wiring

1. Add app route include in `bricolle_family/urls.py`:

```python
path("<app_name>/", include("<app_name>.urls")),
```

2. In `<app_name>/urls.py`, define `app_name` and a home route:

```python
from django.urls import path
from <app_name>.views.home import HomeController

app_name = "<app_name>"

urlpatterns = [
    path("", HomeController.home, name="home"),
]
```

## 3. Add home button on global homepage cards

In `bricolle_family/views/summary.py`, add a module card entry in one of the sections:

- `SummaryView.home`
- `SummaryView.games`
- `SummaryView.more`

Entry format:

```python
{"name": "My App", "url": "/<app_name>/", "color": "#3498db"}
```

This is mandatory for each new app so it is reachable from the global home flow.

## 4. Create required templates

Each new app must contain:

- `<app_name>/templates/<app_name>/header.html`
- `<app_name>/templates/<app_name>/base.html`
- `<app_name>/templates/<app_name>/home.html`

### `header.html` (structure aligned with existing apps)

- Bootstrap navbar.
- Left: app name linking to `'<app_name>:home'`.
- Use nav links (`.nav-link`) in a collapsed navbar menu (Altered-style), not button-styled links.
- Keep in-app links (features of the app) on the left (`.navbar-nav.me-auto`).
- Keep cross-app links (`'home'` and `/admin/<app_name>/`) on the right (`.navbar-nav.ms-auto`) to separate navigation scopes.

Minimal pattern:

```html
<nav class="navbar navbar-expand-lg navbar-light bg-light px-3">
    <div class="container-fluid">
        <a class="navbar-brand" href="{% url '<app_name>:home' %}">My App</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#appNavbar">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="appNavbar">
            <ul class="navbar-nav me-auto">
                <li class="nav-item">
                    <a class="nav-link" href="{% url '<app_name>:home' %}">Home</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url '<app_name>:settings' %}">Settings</a>
                </li>
            </ul>
            <ul class="navbar-nav ms-auto">
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'home' %}">Accueil global</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/admin/<app_name>/">Admin</a>
                </li>
            </ul>
        </div>
    </div>
</nav>
```

### `base.html`

- Load Bootstrap (`django-bootstrap-v5`).
- Include app header via `{% include '<app_name>/header.html' %}`.
- Expose `{% block content %}`.

### `home.html`

- Extend `<app_name>/base.html`.
- Provide a simple landing page with clear links to key actions.

## 5. Models and admin rule

When adding models:

- Put each model in `<app_name>/models/`.
- Register admin in the same model module as the model (project rule).

## 6. Services rule

Business logic goes to `<app_name>/services/`:

- Prefer service classes.
- Keep a small public API and private helper methods for readability.

## 7. Test rule

For each public service function, add matching tests under `<app_name>/tests/`.
