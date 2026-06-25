# SPDX-License-Identifier: AGPL-3.0-or-later
import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import LBRoutingRule


class LBRoutingRuleTable(NetBoxTable):
    listener = tables.Column(linkify=True)
    target_pool = tables.Column(linkify=True)
    action_type = columns.ChoiceFieldColumn()
    match_type = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_load_balancing_acl:lbroutingrule_list")

    class Meta(NetBoxTable.Meta):
        model = LBRoutingRule
        fields = (
            "pk",
            "id",
            "listener",
            "order",
            "action_type",
            "acl_name",
            "match_type",
            "pattern",
            "case_sensitive",
            "negate",
            "target_pool",
            "header_name",
            "header_value",
            "redirect_rule",
            "tags",
            "created",
            "last_updated",
        )
        default_columns = (
            "listener",
            "order",
            "action_type",
            "match_type",
            "pattern",
            "target_pool",
        )
