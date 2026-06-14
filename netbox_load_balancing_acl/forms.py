# SPDX-License-Identifier: AGPL-3.0-or-later
from django import forms
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from netbox_load_balancing.models import Listener, VirtualIPPool
from utilities.forms.fields import (
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from .choices import LBRoutingMatchTypeChoices
from .models import LBRoutingRule


class LBRoutingRuleForm(NetBoxModelForm):
    listener = DynamicModelChoiceField(queryset=Listener.objects.all())
    target_pool = DynamicModelChoiceField(queryset=VirtualIPPool.objects.all())

    fieldsets = (
        FieldSet("listener", "order", name="Frontend"),
        FieldSet("match_type", "pattern", "negate", name="Match"),
        FieldSet("target_pool", name="Backend"),
    )

    class Meta:
        model = LBRoutingRule
        fields = ["listener", "match_type", "pattern", "target_pool", "order", "negate", "tags"]


class LBRoutingRuleFilterForm(NetBoxModelFilterSetForm):
    model = LBRoutingRule
    listener_id = DynamicModelMultipleChoiceField(
        queryset=Listener.objects.all(), required=False, label="Listener"
    )
    target_pool_id = DynamicModelMultipleChoiceField(
        queryset=VirtualIPPool.objects.all(), required=False, label="Target pool"
    )
    match_type = forms.MultipleChoiceField(choices=LBRoutingMatchTypeChoices, required=False)
    negate = forms.NullBooleanField(required=False)
    tag = TagFilterField(LBRoutingRule)
