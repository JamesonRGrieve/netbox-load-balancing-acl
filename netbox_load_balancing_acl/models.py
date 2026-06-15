# SPDX-License-Identifier: AGPL-3.0-or-later
"""LB ACL routing model. One ``LBRoutingRule`` ties a ``netbox_load_balancing.Listener``
(the frontend the ACL lives on) to a ``netbox_load_balancing.Pool`` (the backend server
pool matching traffic routes to — the model mounted at the upstream ``pools`` API, NOT
``VirtualIPPool`` which is the frontend VIP at ``virtual-pools``), via a match type +
pattern — the HAProxy ACL that ``netbox_load_balancing`` itself does not model, so it no
longer falls back to ``config_context``."""

from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from .choices import LBRoutingMatchTypeChoices


class LBRoutingRule(NetBoxModel):
    """A host/SNI/path → backend-pool routing rule (one HAProxy ACL) on a listener."""

    listener = models.ForeignKey(
        "netbox_load_balancing.Listener",
        on_delete=models.CASCADE,
        related_name="routing_rules",
        help_text="The listener (frontend) this routing ACL lives on.",
    )
    match_type = models.CharField(max_length=16, choices=LBRoutingMatchTypeChoices)
    pattern = models.CharField(
        max_length=255,
        help_text="Match value, e.g. erp.zephyrex.ca (host/sni) or /api (path-prefix).",
    )
    target_pool = models.ForeignKey(
        "netbox_load_balancing.Pool",
        on_delete=models.PROTECT,
        related_name="routing_rules",
        help_text="Backend server pool matching traffic routes to (upstream `pools`).",
    )
    order = models.PositiveIntegerField(
        default=100, help_text="Evaluation order; lower is matched first."
    )
    negate = models.BooleanField(
        default=False,
        help_text="Invert the match (matches when the pattern does NOT apply).",
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
        return f"{self.listener}: {self.match_type} {self.pattern} → {self.target_pool}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_load_balancing_acl:lbroutingrule", args=[self.pk])

    def get_match_type_color(self):
        return LBRoutingMatchTypeChoices.colors.get(self.match_type)
