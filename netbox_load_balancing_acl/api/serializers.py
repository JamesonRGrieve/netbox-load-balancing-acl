# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.serializers import NetBoxModelSerializer
from netbox_load_balancing.api.serializers import ListenerSerializer, PoolSerializer
from rest_framework import serializers
from ..models import LBRoutingRule


class LBRoutingRuleSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_load_balancing_acl-api:lbroutingrule-detail"
    )
    listener = ListenerSerializer(nested=True)
    target_pool = PoolSerializer(nested=True)

    class Meta:
        model = LBRoutingRule
        fields = [
            "id",
            "url",
            "display",
            "listener",
            "match_type",
            "pattern",
            "target_pool",
            "order",
            "negate",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        ]
        brief_fields = ["id", "url", "display", "listener", "match_type", "pattern"]
