# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.viewsets import NetBoxModelViewSet
from .. import filtersets
from ..models import LBRoutingRule
from .serializers import LBRoutingRuleSerializer


class LBRoutingRuleViewSet(NetBoxModelViewSet):
    queryset = LBRoutingRule.objects.prefetch_related("listener", "target_pool", "tags")
    serializer_class = LBRoutingRuleSerializer
    filterset_class = filtersets.LBRoutingRuleFilterSet
