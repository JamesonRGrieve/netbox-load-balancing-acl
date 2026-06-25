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

__version__ = "0.0.4"


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


config = NetBoxLoadBalancingACLConfig
