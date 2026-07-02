# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.serializers import NetBoxModelSerializer
from netbox_load_balancing.api.serializers import ListenerSerializer, PoolSerializer
from rest_framework import serializers
from ..models import LBAcl, LBListenerCertificate, LBRoutingRule


class LBAclSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_load_balancing_acl-api:lbacl-detail"
    )
    listener = ListenerSerializer(nested=True)

    class Meta:
        model = LBAcl
        fields = [
            "id",
            "url",
            "display",
            "listener",
            "order",
            "name",
            "match_type",
            "pattern",
            "case_sensitive",
            "negate",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        ]
        brief_fields = ["id", "url", "display", "listener", "order", "name"]


class LBRoutingRuleSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_load_balancing_acl-api:lbroutingrule-detail"
    )
    listener = ListenerSerializer(nested=True)
    target_pool = PoolSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = LBRoutingRule
        fields = [
            "id",
            "url",
            "display",
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
            "custom_fields",
            "created",
            "last_updated",
        ]
        brief_fields = ["id", "url", "display", "listener", "order", "action_type"]


class LBListenerCertificateSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_load_balancing_acl-api:lblistenercertificate-detail"
    )
    listener = ListenerSerializer(nested=True)

    class Meta:
        model = LBListenerCertificate
        fields = [
            "id",
            "url",
            "display",
            "listener",
            "order",
            "ssl_certificate",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        ]
        brief_fields = ["id", "url", "display", "listener", "order", "ssl_certificate"]
