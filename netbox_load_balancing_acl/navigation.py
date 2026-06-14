# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

_routing = PluginMenuItem(
    link="plugins:netbox_load_balancing_acl:lbroutingrule_list",
    link_text="Routing Rules",
    buttons=[
        PluginMenuButton(
            "plugins:netbox_load_balancing_acl:lbroutingrule_add", "Add", "mdi mdi-plus-thick"
        )
    ],
)

menu = PluginMenu(
    label="Load Balancing ACL",
    groups=(("Routing", (_routing,)),),
    icon_class="mdi mdi-call-split",
)
