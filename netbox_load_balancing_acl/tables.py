# SPDX-License-Identifier: AGPL-3.0-or-later
import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import LBRoutingRule


class LBRoutingRuleTable(NetBoxTable):
    listener = tables.Column(linkify=True)
    target_pool = tables.Column(linkify=True)
    match_type = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_load_balancing_acl:lbroutingrule_list")

    class Meta(NetBoxTable.Meta):
        model = LBRoutingRule
        fields = (
            "pk",
            "id",
            "listener",
            "match_type",
            "pattern",
            "target_pool",
            "order",
            "negate",
            "tags",
            "created",
            "last_updated",
        )
        default_columns = ("listener", "match_type", "pattern", "target_pool", "order", "negate")
