<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# netbox-load-balancing-acl

A NetBox 4.6 plugin that adds the **one routing primitive** the third-party
[`netbox_load_balancing`](https://pypi.org/project/netbox-load-balancing/) plugin is missing:
**host / SNI / path → backend-pool routing rules** (HAProxy ACLs).

`netbox_load_balancing` models the listener (frontend) and the backend `VirtualIPPool`, but has
no native way to express "traffic matching `erp.zephyrex.ca` routes to pool X" — so that intent
kept falling back to unstructured `config_context`. This plugin makes the HAProxy ACL a real,
query-able, REST/GraphQL-exposed object.

## Model

One model, `LBRoutingRule`, inheriting `NetBoxModel` (custom fields, tags, change logging,
GraphQL, REST):

| Field | Type | Notes |
|-------|------|-------|
| `listener` | FK `netbox_load_balancing.Listener` (CASCADE) | The frontend this ACL lives on |
| `match_type` | choice | `host` / `sni` / `path_prefix` |
| `pattern` | char(255) | Match value, e.g. `erp.zephyrex.ca` or `/api` |
| `target_pool` | FK `netbox_load_balancing.VirtualIPPool` (PROTECT) | Backend pool traffic routes to |
| `order` | positive int (default 100) | Evaluation order; lower matched first |
| `negate` | bool | Invert the match |

A `UniqueConstraint` on `(listener, order)` enforces one rule per evaluation slot per listener.
The `listener` FK cascades (delete the frontend, its ACLs go); the `target_pool` FK is `PROTECT`
(a pool referenced by a rule cannot be deleted out from under it).

## Why

`netbox_load_balancing` stops at listener + pool; the host/SNI/path routing decision that wires a
listener to a specific backend pool had no home, so it lived as free-form `config_context` JSON —
un-query-able, un-validated. This plugin gives that decision a real, choice-validated, filterable
row, so the HAProxy intent reads back 1:1 from NetBox instead of from buried JSON.

## Depends on

`netbox_load_balancing` must be installed and enabled — it is declared via `required_plugins`, so
NetBox refuses to start this plugin without it. The FKs target that plugin's `Listener` and
`VirtualIPPool` models.

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
building real `netbox_load_balancing` `LBService` / `Listener` / `VirtualIPPool` instances. See
`CLAUDE.md`.

```bash
python /opt/netbox/app/netbox/manage.py test netbox_load_balancing_acl --keepdb -v2
```

## License

AGPL-3.0-or-later.
