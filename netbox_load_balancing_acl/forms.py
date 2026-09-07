# SPDX-License-Identifier: AGPL-3.0-or-later
from django import forms
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from netbox_load_balancing.models import Listener, Member, MemberAssignment, Pool
from utilities.forms.fields import (
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from .choices import LBRoutingActionTypeChoices, LBRoutingMatchTypeChoices
from .models import LBAcl, LBListenerCertificate, LBMemberHA, LBRoutingRule


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
        FieldSet("set_path", name="Rewrite (set-path)"),
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
            "set_path",
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


class LBAclForm(NetBoxModelForm):
    listener = DynamicModelChoiceField(queryset=Listener.objects.all())

    fieldsets = (
        FieldSet("listener", "order", name="ACL"),
        FieldSet("name", "match_type", "pattern", "case_sensitive", "negate", name="Match"),
    )

    class Meta:
        model = LBAcl
        fields = ["listener", "order", "name", "match_type", "pattern", "case_sensitive", "negate", "tags"]


class LBAclFilterForm(NetBoxModelFilterSetForm):
    model = LBAcl
    listener_id = DynamicModelMultipleChoiceField(
        queryset=Listener.objects.all(), required=False, label="Listener"
    )
    match_type = forms.MultipleChoiceField(choices=LBRoutingMatchTypeChoices, required=False)
    negate = forms.NullBooleanField(required=False)
    tag = TagFilterField(LBAcl)


class LBListenerCertificateForm(NetBoxModelForm):
    listener = DynamicModelChoiceField(queryset=Listener.objects.all())

    fieldsets = (
        FieldSet("listener", "order", name="Binding"),
        FieldSet("ssl_certificate", "description", name="Certificate"),
    )

    class Meta:
        model = LBListenerCertificate
        fields = ["listener", "order", "ssl_certificate", "description", "tags"]


class LBListenerCertificateFilterForm(NetBoxModelFilterSetForm):
    model = LBListenerCertificate
    listener_id = DynamicModelMultipleChoiceField(
        queryset=Listener.objects.all(), required=False, label="Listener"
    )
    tag = TagFilterField(LBListenerCertificate)


class LBMemberHAForm(NetBoxModelForm):
    # MemberAssignment.Meta upstream declares no ordering, so its list endpoint raises
    # QuerySetNotOrdered as soon as it is paginated — which is exactly what the dynamic select
    # does. Requesting an explicit ordering makes the picker work without patching the base plugin.
    assignment = DynamicModelChoiceField(
        queryset=MemberAssignment.objects.all(),
        query_params={"ordering": "id"},
        label="Member assignment",
    )

    fieldsets = (FieldSet("assignment", "backup", "description", name="HA role"),)

    class Meta:
        model = LBMemberHA
        fields = ["assignment", "backup", "description", "tags"]


class LBMemberHAFilterForm(NetBoxModelFilterSetForm):
    model = LBMemberHA
    pool_id = DynamicModelMultipleChoiceField(
        queryset=Pool.objects.all(), required=False, label="Pool"
    )
    member_id = DynamicModelMultipleChoiceField(
        queryset=Member.objects.all(), required=False, label="Member"
    )
    backup = forms.NullBooleanField(required=False)
    tag = TagFilterField(LBMemberHA)
