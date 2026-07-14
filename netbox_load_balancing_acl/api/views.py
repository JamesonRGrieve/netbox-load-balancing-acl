# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.viewsets import NetBoxModelViewSet
from .. import filtersets
from ..models import LBAcl, LBListenerCertificate, LBMemberHA, LBRoutingRule
from .serializers import (
    LBAclSerializer,
    LBListenerCertificateSerializer,
    LBMemberHASerializer,
    LBRoutingRuleSerializer,
)


class LBRoutingRuleViewSet(NetBoxModelViewSet):
    queryset = LBRoutingRule.objects.prefetch_related("listener", "target_pool", "tags")
    serializer_class = LBRoutingRuleSerializer
    filterset_class = filtersets.LBRoutingRuleFilterSet


class LBAclViewSet(NetBoxModelViewSet):
    queryset = LBAcl.objects.prefetch_related("listener", "tags")
    serializer_class = LBAclSerializer
    filterset_class = filtersets.LBAclFilterSet


class LBListenerCertificateViewSet(NetBoxModelViewSet):
    queryset = LBListenerCertificate.objects.prefetch_related("listener", "tags")
    serializer_class = LBListenerCertificateSerializer
    filterset_class = filtersets.LBListenerCertificateFilterSet


class LBMemberHAViewSet(NetBoxModelViewSet):
    queryset = LBMemberHA.objects.prefetch_related(
        "assignment__member", "assignment__assigned_object_type", "tags"
    )
    serializer_class = LBMemberHASerializer
    filterset_class = filtersets.LBMemberHAFilterSet
