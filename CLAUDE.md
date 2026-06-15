# netbox-load-balancing-acl — Agent Operating Guide

Adapted from `../netbox-data-link`'s `CLAUDE.md` (same engineering + test discipline),
re-targeted from switch L2 features to **load-balancer routing ACLs**.

`netbox-load-balancing-acl` is an **AGPL-3.0** NetBox 4.6 Django plugin that adds the **one
routing primitive** the third-party `netbox_load_balancing` plugin is missing: **host / SNI /
path → backend-pool routing rules** (HAProxy ACLs). `netbox_load_balancing` models the listener
(frontend) and the backend `Pool` but cannot express "traffic matching
`erp.zephyrex.ca` routes to pool X"; that intent used to fall back to unstructured
`config_context`. This plugin makes the ACL a real, choice-validated, REST/GraphQL-exposed row.

It **depends on `netbox_load_balancing`** (declared via `required_plugins`), and its single
model FKs that plugin's `Listener` and `Pool` models. (NB: the backend is `Pool` — upstream API
mount `pools`, 1-per-backend — NOT `VirtualIPPool`, which is the frontend VIP at `virtual-pools`.)

---

## Key Directives / Rules

### DO, ALWAYS:
- If functionality won't work without a parameter, make it a **required positional** parameter —
  never an optional one with an inline presence check.
- Any time you modify a source file, ensure its accompanying test under
  `netbox_load_balancing_acl/tests/` contains **comprehensive tests for the change WITHOUT
  MOCKS**, so `manage.py test netbox_load_balancing_acl` discovers them, and update any `.md` in
  the same directory that references the changed code.
- Write concise code (avoid obvious comments; use one-liners where possible).
- Critically analyze requirements and ask all necessary clarifying questions before implementing
  or refactoring.
- Phrase documentation for yourself (AI) and for autistic/ADHD humans: a clear architectural
  summary you could reconstruct the code from with 95% accuracy, with minimal snippets — **not**
  usage examples (the browsable REST/GraphQL schema is the usage reference).

### DO NOT, EVER, UNDER ANY CIRCUMSTANCE:
- Make assumptions, or answer with "is likely", "probably", or "might be".
- Use frame-local or thread-local state instead of passing data via parameters.
- Skip a failing test instead of fixing the root cause.
- Fix broken functionality while keeping the broken path as a fallback.
- Re-implement existing functionality in a second location to bypass the original.
- Use bandaid fixes instead of fixing the core functionality.
- **Mock the database, the ORM, the NetBox API test client, or any integration path.** Tests run
  against a **real test database** via NetBox's Django test framework — use real model instances
  (including real `netbox_load_balancing` `LBService`/`Listener`/`Pool`) and real API
  requests. Only pure utility functions may use mocks for isolation.

### Python / Django Guidelines:
- Import children of `datetime`: `from datetime import date` — **never** `import datetime` then
  `datetime.date`.
- Imports are package-relative inside `netbox_load_balancing_acl` (`from .models import
  LBRoutingRule`), never `from netbox_load_balancing_acl.models import ...`. Imports of the
  upstream plugin use its real package path (`from netbox_load_balancing.models import Listener`).
- Models inherit `netbox.models.NetBoxModel` (custom fields, tags, journaling, change logging,
  GraphQL — for free).
- **SPDX header on every source file**: `# SPDX-License-Identifier: AGPL-3.0-or-later`.

### Documentation Guidelines:
- Markdown docs are concise: reconstruct-the-code-with-95%-accuracy architectural summaries with
  minimal snippets, not usage tutorials.

---

## Architecture (NetBox 4.6 plugin)

| File | Responsibility |
|------|----------------|
| `__init__.py` | `PluginConfig` — name `netbox_load_balancing_acl`, `base_url='lb-acl'`, `required_plugins=["netbox_load_balancing"]`, min/max NetBox version |
| `choices.py` | `LBRoutingMatchTypeChoices`: host / sni / path_prefix |
| `models.py` | The single `LBRoutingRule` model (see §Model) |
| `migrations/` | hand-authored (NetBox disables `makemigrations` in prod); verify with `makemigrations --check --dry-run` on an ephemeral NetBox |
| `api/serializers.py`, `api/views.py`, `api/urls.py` | REST API (`NetBoxModelViewSet`) — endpoint `/api/plugins/lb-acl/routing-rules/` |
| `filtersets.py` | `NetBoxModelFilterSet`: filter by `listener_id`, `target_pool_id`, `match_type` |
| `tables.py`, `forms.py`, `navigation.py`, `views.py`, `urls.py` | UI layer |
| `graphql/` | GraphQL types (none shipped yet — `NetBoxModel` still exposes auto GraphQL) |

### Model — the routing-ACL SoT
- **LBRoutingRule** (`NetBoxModel`):
  - `listener` → FK `netbox_load_balancing.Listener`, `on_delete=CASCADE` — the frontend the ACL
    lives on.
  - `match_type` — `host` / `sni` / `path_prefix`.
  - `pattern` — the match value (`erp.zephyrex.ca`, `/api`).
  - `target_pool` → FK `netbox_load_balancing.Pool`, `on_delete=PROTECT` — backend server pool
    matching traffic routes to (the upstream `pools` mount; NOT `VirtualIPPool`, the frontend VIP
    at `virtual-pools` — the original FK conflated the two).
  - `order` — evaluation order (lower first).
  - `negate` — invert the match.
  - `UniqueConstraint(listener, order)` — one rule per evaluation slot per listener.

`listener` CASCADEs (drop the frontend, its ACLs go); `target_pool` is PROTECT (a referenced pool
cannot be deleted out from under a rule). The migration depends on `netbox_load_balancing`'s
latest migration so both target tables exist before `LBRoutingRule` is created.

---

## Testing (NO MOCKS — real DB, NetBox test framework)

- Tests live in `netbox_load_balancing_acl/tests/` (inside the package, so `manage.py test
  netbox_load_balancing_acl` discovers them and they ship with the plugin), one module per source
  module (`test_models.py`, `test_api.py`, `test_filtersets.py`).
- Build real upstream objects: an `LBService` (needs `name` + `reference`) backs a `Listener`
  (needs `name`, `service`, `port`); a `Pool` needs only `name`. A routing rule needs a
  fresh listener per `order` value to respect the `(listener, order)` constraint.
- Use NetBox's base classes from `utilities.testing`: `APIViewTestCases.APIViewTestCase` (composed
  CRUD mixins).
- **Test isolation**: Django wraps each test in a transaction against a per-run test database with
  automatic teardown.
- **Never skip a failing test** — fix the root cause; repair deficiencies starting with the
  lowest-hanging fruit.
- **Run**: `python /opt/netbox/app/netbox/manage.py test netbox_load_balancing_acl --keepdb -v2`
  (or `pytest` with `pytest-django` + `DJANGO_SETTINGS_MODULE=netbox.settings`).
- **Coverage bar**: the model, serializer, filterset, and view all have tests — including the
  uniqueness constraint, CASCADE from the listener, and PROTECT on the target pool.

---

## Licensing
- **AGPL-3.0-or-later** (workspace production-IaC standard). SPDX header in every file.
