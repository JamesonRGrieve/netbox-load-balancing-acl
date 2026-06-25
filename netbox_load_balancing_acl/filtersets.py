# SPDX-License-Identifier: AGPL-3.0-or-later
import django_filters
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from netbox_load_balancing.models import Listener, Pool
from .choices import LBRoutingActionTypeChoices, LBRoutingMatchTypeChoices
from .models import LBAcl, LBRoutingRule


# Explicit FK filters: django-filter does NOT derive `<fk>_id` from a bare FK in Meta.fields,
# so a bare `listener`/`target_pool` would be silently ignored. NetBox convention is `<fk>_id`.
class LBRoutingRuleFilterSet(NetBoxModelFilterSet):
    listener_id = django_filters.ModelMultipleChoiceFilter(
        field_name="listener", queryset=Listener.objects.all(), label="Listener (ID)"
    )
    target_pool_id = django_filters.ModelMultipleChoiceFilter(
        field_name="target_pool", queryset=Pool.objects.all(), label="Target pool (ID)"
    )
    action_type = django_filters.MultipleChoiceFilter(choices=LBRoutingActionTypeChoices)
    match_type = django_filters.MultipleChoiceFilter(choices=LBRoutingMatchTypeChoices)

    class Meta:
        model = LBRoutingRule
        fields = ["id", "order", "negate", "case_sensitive", "acl_name"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(pattern__icontains=value)
            | Q(listener__name__icontains=value)
            | Q(acl_name__icontains=value)
            | Q(header_name__icontains=value)
        )


class LBAclFilterSet(NetBoxModelFilterSet):
    listener_id = django_filters.ModelMultipleChoiceFilter(
        field_name="listener", queryset=Listener.objects.all(), label="Listener (ID)"
    )
    match_type = django_filters.MultipleChoiceFilter(choices=LBRoutingMatchTypeChoices)

    class Meta:
        model = LBAcl
        fields = ["id", "order", "name", "negate", "case_sensitive"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(pattern__icontains=value) | Q(listener__name__icontains=value)
        )
