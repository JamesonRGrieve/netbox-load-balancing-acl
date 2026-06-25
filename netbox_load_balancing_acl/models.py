# SPDX-License-Identifier: AGPL-3.0-or-later
"""LB ACL routing model. One ``LBRoutingRule`` is one HAProxy frontend *action* on a
``netbox_load_balancing.Listener`` (the frontend). A ``use_backend`` action carries an
inline match condition (the HAProxy ACL) and routes to a ``netbox_load_balancing.Pool``
(the backend mounted at the upstream ``pools`` API, NOT ``VirtualIPPool`` which is the
frontend VIP at ``virtual-pools``). Non-routing actions (request/response header rewrites,
scheme redirects) carry no ACL/pool — modeling them natively lets an adopted frontend
reproduce its whole action array at 0-diff instead of dropping the non-routing actions."""

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from .choices import LBRoutingActionTypeChoices, LBRoutingMatchTypeChoices


class LBRoutingRule(NetBoxModel):
    """One HAProxy frontend action (use_backend host-route, header rewrite, or redirect)."""

    listener = models.ForeignKey(
        "netbox_load_balancing.Listener",
        on_delete=models.CASCADE,
        related_name="routing_rules",
        help_text="The listener (frontend) this action lives on.",
    )
    order = models.PositiveIntegerField(
        default=100, help_text="Evaluation order; lower is matched first."
    )
    action_type = models.CharField(
        max_length=32,
        choices=LBRoutingActionTypeChoices,
        default=LBRoutingActionTypeChoices.USE_BACKEND,
        help_text="The HAProxy frontend action this rule expresses.",
    )

    # ── use_backend: the inline match condition (HAProxy ACL) + target pool ──
    acl_name = models.CharField(
        max_length=64,
        blank=True,
        help_text="The HAProxy ACL name (use_backend). Stored verbatim — pfSense names "
        "are historical (e.g. acl_mail, proxmox_acl) and must round-trip exactly.",
    )
    match_type = models.CharField(
        max_length=16, choices=LBRoutingMatchTypeChoices, blank=True
    )
    pattern = models.CharField(
        max_length=255,
        blank=True,
        help_text="Match value, e.g. mail. (host_starts_with) or erp.zephyrex.ca (host).",
    )
    case_sensitive = models.BooleanField(
        default=False, help_text="ACL case sensitivity (HAProxy casesensitive)."
    )
    negate = models.BooleanField(
        default=False,
        help_text="Invert the match (matches when the pattern does NOT apply).",
    )
    target_pool = models.ForeignKey(
        "netbox_load_balancing.Pool",
        on_delete=models.PROTECT,
        related_name="routing_rules",
        null=True,
        blank=True,
        help_text="Backend pool for a use_backend action (upstream `pools`).",
    )

    # ── set-header (request/response): header name + value ──
    header_name = models.CharField(
        max_length=128, blank=True, help_text="Header name for a set-header action."
    )
    header_value = models.CharField(
        max_length=255, blank=True, help_text="Header value (HAProxy fmt) for set-header."
    )

    # ── redirect: the HAProxy redirect rule ──
    redirect_rule = models.CharField(
        max_length=255,
        blank=True,
        help_text='HAProxy redirect rule for a redirect action, e.g. "scheme https code 301".',
    )

    class Meta:
        ordering = ["listener", "order"]
        verbose_name = "LB Routing Rule"
        constraints = [
            models.UniqueConstraint(
                fields=["listener", "order"], name="lb_acl_routing_rule_listener_order"
            )
        ]

    def __str__(self):
        if self.action_type == LBRoutingActionTypeChoices.USE_BACKEND:
            return f"{self.listener}: {self.match_type} {self.pattern} → {self.target_pool}"
        if self.action_type == LBRoutingActionTypeChoices.REDIRECT:
            return f"{self.listener}: redirect {self.redirect_rule}"
        return f"{self.listener}: {self.action_type} {self.header_name}={self.header_value}"

    def clean(self):
        super().clean()
        if self.action_type == LBRoutingActionTypeChoices.USE_BACKEND:
            if not self.target_pool_id:
                raise ValidationError({"target_pool": "Required for a use_backend action."})
            if not self.match_type:
                raise ValidationError({"match_type": "Required for a use_backend action."})
        elif self.action_type == LBRoutingActionTypeChoices.REDIRECT:
            if not self.redirect_rule:
                raise ValidationError({"redirect_rule": "Required for a redirect action."})
        else:  # set-header request/response
            if not self.header_name:
                raise ValidationError({"header_name": "Required for a set-header action."})

    def get_absolute_url(self):
        return reverse("plugins:netbox_load_balancing_acl:lbroutingrule", args=[self.pk])

    def get_match_type_color(self):
        return LBRoutingMatchTypeChoices.colors.get(self.match_type)

    def get_action_type_color(self):
        return LBRoutingActionTypeChoices.colors.get(self.action_type)


class LBAcl(NetBoxModel):
    """One HAProxy frontend ACL condition (a ``ha_acls`` entry), as a first-class ordered
    object on a ``netbox_load_balancing.Listener``.

    Modeled separately from ``LBRoutingRule`` (the actions) because the device's ``ha_acls``
    array and ``a_actionitems`` array are independent, and an ACL is NOT uniquely named:
    pfSense allows two ACLs with the same name but different expressions (e.g. an OR of
    host_contains + host_matches for the same domain). The action references an ACL by name,
    so a duplicate name simply ORs the conditions. Reproducing the live array byte-for-byte
    (for 0-diff adoption) therefore requires per-position ACL objects, which this provides."""

    listener = models.ForeignKey(
        "netbox_load_balancing.Listener",
        on_delete=models.CASCADE,
        related_name="acls",
        help_text="The listener (frontend) this ACL lives on.",
    )
    order = models.PositiveIntegerField(
        default=100, help_text="Position in the frontend's ha_acls array (the device id)."
    )
    name = models.CharField(
        max_length=64,
        help_text="HAProxy ACL name (NOT unique — duplicates OR their conditions).",
    )
    match_type = models.CharField(max_length=16, choices=LBRoutingMatchTypeChoices)
    pattern = models.CharField(max_length=255, help_text="Match value (host/SNI/path).")
    case_sensitive = models.BooleanField(default=False)
    negate = models.BooleanField(
        default=False, help_text="Invert the match (HAProxy `not`)."
    )

    class Meta:
        ordering = ["listener", "order"]
        verbose_name = "LB ACL"
        verbose_name_plural = "LB ACLs"
        constraints = [
            models.UniqueConstraint(
                fields=["listener", "order"], name="lb_acl_listener_order"
            )
        ]

    def __str__(self):
        return f"{self.listener}[{self.order}]: {self.name} {self.match_type} {self.pattern}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_load_balancing_acl:lbacl", args=[self.pk])

    def get_match_type_color(self):
        return LBRoutingMatchTypeChoices.colors.get(self.match_type)
