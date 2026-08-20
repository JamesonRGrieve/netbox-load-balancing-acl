# SPDX-License-Identifier: AGPL-3.0-or-later
"""netbox-load-balancing-acl: the one routing primitive the third-party
``netbox_load_balancing`` plugin is missing — **host / SNI / path → backend-pool
routing rules** (HAProxy ACLs).

``netbox_load_balancing`` models the listener (frontend) and the backend ``Pool``,
but has no native way to express "traffic matching ``erp.zephyrex.ca`` routes to pool X" — so
that intent kept falling back to unstructured ``config_context``. This plugin adds a single
``LBRoutingRule`` model FK-ing a ``Listener`` to a ``Pool`` with a match type + pattern,
making the HAProxy ACL a real, query-able, REST/GraphQL-exposed object.
"""

from netbox.plugins import PluginConfig

__version__ = "0.0.7"


class NetBoxLoadBalancingACLConfig(PluginConfig):
    name = "netbox_load_balancing_acl"
    verbose_name = "NetBox Load Balancing ACL"
    description = (
        "Host/SNI/path → backend-pool routing rules (HAProxy ACLs) for netbox_load_balancing"
    )
    version = __version__
    author = "Jameson"
    base_url = "lb-acl"
    min_version = "4.6.0"
    max_version = "4.6.99"
    required_plugins = ["netbox_load_balancing"]

    def ready(self):
        super().ready()
        # Compat shim: upstream netbox_load_balancing (≥1.3.6) ships assignment
        # models without Meta.ordering, so every paginated list endpoint 500s
        # with QuerySetNotOrdered — silently blinding any consumer that
        # tolerates fetch failure (the tofu LB reader renders zero intent).
        # Supply a pk ordering at runtime for any upstream model missing one.
        # Lives HERE (our plugin) so an upstream reinstall can't wipe it;
        # drop when upstream restores the orderings.
        from netbox_load_balancing import models as lb_models

        for model_name in (
            "LBServiceAssignment",
            "HealthMonitorAssignment",
            "PoolAssignment",
            "MemberAssignment",
            "VirtualIPPoolAssignment",
        ):
            model = getattr(lb_models, model_name, None)
            if model is not None and not model._meta.ordering:
                model._meta.ordering = ("pk",)


config = NetBoxLoadBalancingACLConfig
