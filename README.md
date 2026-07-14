<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# netbox-load-balancing-acl

A NetBox 4.6 plugin that adds the **one routing primitive** the third-party
[`netbox_load_balancing`](https://pypi.org/project/netbox-load-balancing/) plugin is missing:
**host / SNI / path → backend-pool routing rules** (HAProxy ACLs).

`netbox_load_balancing` models the listener (frontend) and the backend `Pool`, but has no native
way to express "traffic matching `erp.zephyrex.ca` routes to pool X" — so that intent kept falling
back to unstructured `config_context`. This plugin makes the HAProxy ACL a real, query-able,
REST/GraphQL-exposed object, and adds the frontend-side and failover-side primitives the base
plugin also lacks.

Every model inherits `NetBoxModel` (custom fields, tags, change logging, GraphQL, REST). The base
plugin is never modified — each model is a satellite FK-ing into it.

## Models

### `LBRoutingRule` — one HAProxy frontend action

A `use_backend` host/SNI/path route, a `default_backend` catch-all, a request/response
`set-header`, or a `redirect`. FKs a `Listener` (CASCADE) and, for the backend-selecting actions,
a `Pool` (PROTECT). `order` positions it in the frontend's action array; `(listener, order)` is
unique. `clean()` enforces the per-action-type requirements (a `use_backend` needs a pool and a
match; a `redirect` needs a rule; a `set-header` needs a name).

### `LBAcl` — one HAProxy frontend ACL condition

The `ha_acls` array entries, modeled per-position because an ACL name is **not** unique: pfSense
permits two ACLs with the same name whose conditions OR together. `(listener, order)` is unique.

### `LBListenerCertificate` — one SNI/TLS cert bound to a frontend

Reproduces the device's certificate array position-for-position (pfSense `ha_certificates`,
OPNsense `ssl_certificates`), so an adopted frontend renders at 0-diff and an ACME-issued cert can
be appended natively. `ssl_certificate` is the opaque device cert-store refid.

### `LBMemberHA` — the HAProxy `backup` keyword

A one-to-one satellite on the base plugin's `MemberAssignment` (the pool↔member through-model,
i.e. one backend `server` line). The role belongs to the **membership**, not the member: `backup`
is an attribute of a server line inside a backend, and a `Member` may be assigned to more than one
pool.

| Field | Type | Notes |
|-------|------|-------|
| `assignment` | OneToOne `netbox_load_balancing.MemberAssignment` (CASCADE) | The server line |
| `backup` | bool (default `true`) | Serve only when every non-backup member of the pool is down |
| `description` | char(200) | Human note; not sent to the device |

**Absence of a row means active** — the device default. A row exists to declare a standby.
`MemberAssignment` can also attach a member to a `HealthMonitor`, where `backup` is meaningless,
so `clean()` constrains the assignment to a `Pool`.

## Why

`netbox_load_balancing` stops at listener + pool + member. The routing decision, the frontend's
ACL and certificate arrays, and a member's active/backup role had no home, so they lived as
free-form `config_context` JSON — un-query-able, un-validated. These models give each of them a
choice-validated, filterable row, so the HAProxy intent reads back 1:1 from NetBox.

## Depends on

`netbox_load_balancing` must be installed and enabled — it is declared via `required_plugins`, so
NetBox refuses to start this plugin without it. The FKs target that plugin's `Listener`, `Pool`,
and `MemberAssignment` models.

## Install

```bash
uv pip install --python /opt/netbox/venv/bin/python netbox-load-balancing-acl   # or: pip install -e .
# add "netbox_load_balancing_acl" to PLUGINS in configuration.py (after "netbox_load_balancing")
python manage.py migrate netbox_load_balancing_acl
python manage.py collectstatic --no-input
systemctl restart netbox netbox-rq
```

## Develop / test

Tests run against a **real NetBox test database** (no mocks) via NetBox's Django test framework,
building real `netbox_load_balancing` `LBService` / `Listener` / `Pool` / `Member` /
`MemberAssignment` instances. See `CLAUDE.md`.

```bash
python /opt/netbox/app/netbox/manage.py test netbox_load_balancing_acl --keepdb -v2
```

## License

AGPL-3.0-or-later.
