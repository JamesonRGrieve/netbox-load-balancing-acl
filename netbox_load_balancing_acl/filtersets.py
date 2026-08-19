# SPDX-License-Identifier: AGPL-3.0-or-later
import django_filters
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from netbox_load_balancing.models import HealthMonitor, Listener, Member, MemberAssignment, Pool
from .choices import LBRoutingActionTypeChoices, LBRoutingMatchTypeChoices
from .models import (
    LBAcl,
    LBBackendTuning,
    LBFrontendTuning,
    LBHealthCheckTuning,
    LBListenerCertificate,
    LBMemberHA,
    LBRoutingRule,
)


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


class LBListenerCertificateFilterSet(NetBoxModelFilterSet):
    listener_id = django_filters.ModelMultipleChoiceFilter(
        field_name="listener", queryset=Listener.objects.all(), label="Listener (ID)"
    )

    class Meta:
        model = LBListenerCertificate
        fields = ["id", "order", "ssl_certificate"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(ssl_certificate__icontains=value)
            | Q(description__icontains=value)
            | Q(listener__name__icontains=value)
        )


class LBMemberHAFilterSet(NetBoxModelFilterSet):
    assignment_id = django_filters.ModelMultipleChoiceFilter(
        field_name="assignment",
        queryset=MemberAssignment.objects.all(),
        label="Member assignment (ID)",
    )
    member_id = django_filters.ModelMultipleChoiceFilter(
        field_name="assignment__member", queryset=Member.objects.all(), label="Member (ID)"
    )
    # The pool is the generic target of the assignment, so it needs an explicit traversal of
    # (assigned_object_type, assigned_object_id) rather than a plain FK filter.
    pool_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Pool.objects.all(), method="filter_pool", label="Pool (ID)"
    )

    class Meta:
        model = LBMemberHA
        fields = ["id", "backup"]

    def filter_pool(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            assignment__assigned_object_type__app_label="netbox_load_balancing",
            assignment__assigned_object_type__model="pool",
            assignment__assigned_object_id__in=[pool.pk for pool in value],
        )

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(assignment__member__name__icontains=value) | Q(description__icontains=value)
        )


class LBHealthCheckTuningFilterSet(NetBoxModelFilterSet):
    monitor_id = django_filters.ModelMultipleChoiceFilter(
        field_name="monitor", queryset=HealthMonitor.objects.all(), label="Health monitor (ID)"
    )

    class Meta:
        model = LBHealthCheckTuning
        fields = ["id", "fall", "rise", "http_method"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(monitor__name__icontains=value))


class LBBackendTuningFilterSet(NetBoxModelFilterSet):
    pool_id = django_filters.ModelMultipleChoiceFilter(
        field_name="pool", queryset=Pool.objects.all(), label="Pool (ID)"
    )

    class Meta:
        model = LBBackendTuning
        fields = ["id", "retries", "redispatch", "log_health_checks"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(pool__name__icontains=value))


class LBFrontendTuningFilterSet(NetBoxModelFilterSet):
    listener_id = django_filters.ModelMultipleChoiceFilter(
        field_name="listener", queryset=Listener.objects.all(), label="Listener (ID)"
    )

    class Meta:
        model = LBFrontendTuning
        fields = ["id"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(listener__name__icontains=value))
