# SPDX-License-Identifier: AGPL-3.0-or-later
from django import forms
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from netbox_load_balancing.models import Listener, Pool
from utilities.forms.fields import (
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from .choices import LBRoutingActionTypeChoices, LBRoutingMatchTypeChoices
from .models import LBRoutingRule


class LBRoutingRuleForm(NetBoxModelForm):
    listener = DynamicModelChoiceField(queryset=Listener.objects.all())
    # Optional: only a use_backend action targets a pool.
    target_pool = DynamicModelChoiceField(queryset=Pool.objects.all(), required=False)

    fieldsets = (
        FieldSet("listener", "order", "action_type", name="Action"),
        FieldSet("acl_name", "match_type", "pattern", "case_sensitive", "negate", name="Match (use_backend)"),
        FieldSet("target_pool", name="Backend (use_backend)"),
        FieldSet("header_name", "header_value", name="Header (set-header)"),
        FieldSet("redirect_rule", name="Redirect"),
    )

    class Meta:
        model = LBRoutingRule
        fields = [
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
        ]


class LBRoutingRuleFilterForm(NetBoxModelFilterSetForm):
    model = LBRoutingRule
    listener_id = DynamicModelMultipleChoiceField(
        queryset=Listener.objects.all(), required=False, label="Listener"
    )
    target_pool_id = DynamicModelMultipleChoiceField(
        queryset=Pool.objects.all(), required=False, label="Target pool"
    )
    action_type = forms.MultipleChoiceField(choices=LBRoutingActionTypeChoices, required=False)
    match_type = forms.MultipleChoiceField(choices=LBRoutingMatchTypeChoices, required=False)
    negate = forms.NullBooleanField(required=False)
    tag = TagFilterField(LBRoutingRule)
