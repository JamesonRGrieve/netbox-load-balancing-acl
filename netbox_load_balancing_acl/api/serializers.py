# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.serializers import NetBoxModelSerializer
from netbox_load_balancing.api.serializers import (
    HealthMonitorSerializer,
    ListenerSerializer,
    MemberAssignmentSerializer,
    PoolSerializer,
)
from rest_framework import serializers
from ..models import (
    LBAcl,
    LBBackendTuning,
    LBFrontendTuning,
    LBHealthCheckTuning,
    LBListenerCertificate,
    LBMemberHA,
    LBRoutingRule,
)


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


class LBMemberHASerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_load_balancing_acl-api:lbmemberha-detail"
    )
    # The nested assignment carries both sides of the server line (member + assigned_object),
    # so no separate member/pool fields are needed to join this row to a backend.
    assignment = MemberAssignmentSerializer(nested=True)

    class Meta:
        model = LBMemberHA
        fields = [
            "id",
            "url",
            "display",
            "assignment",
            "backup",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        ]
        brief_fields = ["id", "url", "display", "assignment", "backup"]


class LBHealthCheckTuningSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_load_balancing_acl-api:lbhealthchecktuning-detail"
    )
    monitor = HealthMonitorSerializer(nested=True)

    class Meta:
        model = LBHealthCheckTuning
        fields = [
            "id",
            "url",
            "display",
            "monitor",
            "fall",
            "rise",
            "fast_interval",
            "down_interval",
            "http_method",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        ]
        brief_fields = ["id", "url", "display", "monitor", "fall", "rise"]


class LBBackendTuningSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_load_balancing_acl-api:lbbackendtuning-detail"
    )
    pool = PoolSerializer(nested=True)

    class Meta:
        model = LBBackendTuning
        fields = [
            "id",
            "url",
            "display",
            "pool",
            "retries",
            "redispatch",
            "retry_on",
            "log_health_checks",
            "http_check_path",
            "http_check_method",
            "custom_options",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        ]
        brief_fields = ["id", "url", "display", "pool", "retries"]


class LBFrontendTuningSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_load_balancing_acl-api:lbfrontendtuning-detail"
    )
    listener = ListenerSerializer(nested=True)

    class Meta:
        model = LBFrontendTuning
        fields = [
            "id",
            "url",
            "display",
            "listener",
            "custom_options",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        ]
        brief_fields = ["id", "url", "display", "listener"]
