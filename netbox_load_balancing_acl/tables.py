# SPDX-License-Identifier: AGPL-3.0-or-later
import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import LBAcl, LBListenerCertificate, LBMemberHA, LBRoutingRule


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
            "set_path",
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


class LBAclTable(NetBoxTable):
    listener = tables.Column(linkify=True)
    name = tables.Column(linkify=True)
    match_type = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_load_balancing_acl:lbacl_list")

    class Meta(NetBoxTable.Meta):
        model = LBAcl
        fields = (
            "pk",
            "id",
            "listener",
            "order",
            "name",
            "match_type",
            "pattern",
            "case_sensitive",
            "negate",
            "tags",
            "created",
            "last_updated",
        )
        default_columns = ("listener", "order", "name", "match_type", "pattern", "negate")


class LBListenerCertificateTable(NetBoxTable):
    listener = tables.Column(linkify=True)
    ssl_certificate = tables.Column(linkify=True)
    tags = columns.TagColumn(
        url_name="plugins:netbox_load_balancing_acl:lblistenercertificate_list"
    )

    class Meta(NetBoxTable.Meta):
        model = LBListenerCertificate
        fields = (
            "pk",
            "id",
            "listener",
            "order",
            "ssl_certificate",
            "description",
            "tags",
            "created",
            "last_updated",
        )
        default_columns = ("listener", "order", "ssl_certificate", "description")


class LBMemberHATable(NetBoxTable):
    assignment = tables.Column(linkify=True)
    pool = tables.Column(accessor="assignment__assigned_object", linkify=True, orderable=False)
    member = tables.Column(accessor="assignment__member", linkify=True, orderable=False)
    backup = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_load_balancing_acl:lbmemberha_list")

    class Meta(NetBoxTable.Meta):
        model = LBMemberHA
        fields = (
            "pk",
            "id",
            "assignment",
            "pool",
            "member",
            "backup",
            "description",
            "tags",
            "created",
            "last_updated",
        )
        default_columns = ("pool", "member", "backup", "description")
