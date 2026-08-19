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
        if self.action_type == LBRoutingActionTypeChoices.DEFAULT_BACKEND:
            return f"{self.listener}: default_backend → {self.target_pool}"
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
        elif self.action_type == LBRoutingActionTypeChoices.DEFAULT_BACKEND:
            # Catch-all: only the target pool matters; no ACL/match is used.
            if not self.target_pool_id:
                raise ValidationError({"target_pool": "Required for a default_backend action."})
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


class LBListenerCertificate(NetBoxModel):
    """One SNI/TLS certificate bound to a ``netbox_load_balancing.Listener`` (the frontend),
    as a first-class ordered object.

    Reproduces the device's frontend certificate array position-for-position — pfSense
    ``ha_certificates`` (``[{ssl_certificate: <refid>}, ...]``) and OPNsense
    ``ssl_certificates`` (a comma-joined refid list). Modeling it natively (rather than
    leaving the frontend's cert set live-managed) is what lets an adopted frontend's SNI
    certs render at 0-diff AND lets a new Cloudflare/ACME cert be APPENDED to the frontend
    through the pipeline. ``ssl_certificate`` is the device cert-store refid: opaque and
    device-assigned (ACME issuance yields the refid, which is recorded here to bind it)."""

    listener = models.ForeignKey(
        "netbox_load_balancing.Listener",
        on_delete=models.CASCADE,
        related_name="certificates",
        help_text="The listener (frontend) this certificate is bound to.",
    )
    order = models.PositiveIntegerField(
        default=100,
        help_text="Position in the frontend's ha_certificates / ssl_certificates array.",
    )
    ssl_certificate = models.CharField(
        max_length=64,
        help_text="Device cert-store refid (pfSense/OPNsense-assigned, opaque). An "
        "ACME-issued cert's refid is recorded here to bind it onto the frontend.",
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text="Human note — e.g. the FQDN this cert covers (not sent to the device).",
    )

    class Meta:
        ordering = ["listener", "order"]
        verbose_name = "LB Listener Certificate"
        verbose_name_plural = "LB Listener Certificates"
        constraints = [
            models.UniqueConstraint(
                fields=["listener", "order"], name="lb_listener_cert_listener_order"
            )
        ]

    def __str__(self):
        return f"{self.listener}[{self.order}]: {self.ssl_certificate}"

    def get_absolute_url(self):
        return reverse(
            "plugins:netbox_load_balancing_acl:lblistenercertificate", args=[self.pk]
        )


class LBMemberHA(NetBoxModel):
    """The HA role of one member *within one backend pool* — the HAProxy ``backup`` keyword.

    The role belongs to the **membership**, not the member: ``backup`` is an attribute of a
    ``server`` line inside a ``backend``, and the same ``netbox_load_balancing.Member`` may be
    assigned to more than one pool. The upstream through-model ``MemberAssignment`` (which
    already carries ``weight`` and ``disabled``) is therefore the correct grain, and this is a
    satellite one-to-one on it rather than a field on ``Member`` — the third-party base plugin
    is not modified.

    Absence of a row means **active**, which is the device default. A row exists to declare a
    standby: the device emits ``backup`` on that server, so it takes traffic only once every
    non-backup member of the pool fails its health check. This is the failover primitive behind
    a client site's house mirror being registered in the primary's ingress pool.

    ``MemberAssignment`` also attaches members to a ``HealthMonitor``; ``backup`` is meaningless
    there, so ``clean()`` constrains the assignment to a ``Pool``."""

    assignment = models.OneToOneField(
        "netbox_load_balancing.MemberAssignment",
        on_delete=models.CASCADE,
        related_name="ha",
        help_text="The pool↔member assignment (the HAProxy server line) this role applies to.",
    )
    backup = models.BooleanField(
        default=True,
        help_text="Serve only when every non-backup member of the pool is down (HAProxy "
        "`backup`). A member with no LBMemberHA row is active.",
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text="Human note — e.g. what this standby is a mirror of (not sent to the device).",
    )

    class Meta:
        ordering = ["assignment"]
        verbose_name = "LB Member HA"
        verbose_name_plural = "LB Member HA"

    def __str__(self):
        return f"{self.assignment}: {'backup' if self.backup else 'active'}"

    def clean(self):
        super().clean()
        # Compare the content type rather than importing Pool: the limit_choices_to upstream is
        # itself expressed on (app_label, model), and a model-module import of a sibling plugin
        # runs before the app registry is populated.
        if (
            self.assignment_id
            and self.assignment.assigned_object_type.model != "pool"
        ):
            raise ValidationError(
                {"assignment": "The assignment must be to a Pool (a backend), not a health monitor."}
            )

    def get_absolute_url(self):
        return reverse("plugins:netbox_load_balancing_acl:lbmemberha", args=[self.pk])

    @property
    def member(self):
        return self.assignment.member

    @property
    def pool(self):
        return self.assignment.assigned_object


class LBHealthCheckTuning(NetBoxModel):
    """Satellite on ``netbox_load_balancing.HealthMonitor`` for HAProxy health-check
    timing parameters that the upstream base plugin does not model.

    These control how quickly a server is marked DOWN on failure and how quickly it
    recovers — the difference between a 10ms blip causing a 30s outage and being
    invisible."""

    monitor = models.OneToOneField(
        "netbox_load_balancing.HealthMonitor",
        on_delete=models.CASCADE,
        related_name="tuning",
        help_text="The health monitor this tuning applies to.",
    )
    fall = models.PositiveIntegerField(
        default=3,
        help_text="Consecutive failed checks to mark server DOWN (HAProxy `fall`).",
    )
    rise = models.PositiveIntegerField(
        default=2,
        help_text="Consecutive successful checks to mark server UP (HAProxy `rise`).",
    )
    fast_interval = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Check interval (ms) during transitional state (HAProxy `fastinter`). "
        "Null = use the normal interval.",
    )
    down_interval = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Check interval (ms) while server is DOWN (HAProxy `downinter`). "
        "Null = use the normal interval.",
    )
    http_method = models.CharField(
        max_length=16,
        blank=True,
        default="",
        help_text="HTTP method for health checks (GET, HEAD, OPTIONS). "
        "Empty = platform default.",
    )

    class Meta:
        ordering = ["monitor"]
        verbose_name = "LB Health Check Tuning"
        verbose_name_plural = "LB Health Check Tuning"

    def __str__(self):
        return f"{self.monitor}: fall={self.fall} rise={self.rise}"

    def get_absolute_url(self):
        return reverse(
            "plugins:netbox_load_balancing_acl:lbhealthchecktuning", args=[self.pk]
        )


class LBBackendTuning(NetBoxModel):
    """Satellite on ``netbox_load_balancing.Pool`` (the backend) for retry, redispatch,
    custom pass-thru options, and health-check logging that the upstream base plugin
    does not model.

    ``custom_options`` is the HAProxy backend pass-thru: raw config lines injected after
    the generated config. Use for ``default-server`` overrides, ``option redispatch``,
    ``retry-on``, and any setting not covered by typed fields."""

    pool = models.OneToOneField(
        "netbox_load_balancing.Pool",
        on_delete=models.CASCADE,
        related_name="tuning",
        help_text="The pool (backend) this tuning applies to.",
    )
    retries = models.PositiveIntegerField(
        default=3,
        help_text="Number of retries on connection failure (HAProxy `retries`).",
    )
    redispatch = models.BooleanField(
        default=False,
        help_text="Re-dispatch failed request to another server (HAProxy `option redispatch`).",
    )
    retry_on = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Conditions to retry on (HAProxy `retry-on`), e.g. "
        "'conn-failure empty-response response-timeout 0rtt-rejected'.",
    )
    log_health_checks = models.BooleanField(
        default=False,
        help_text="Log every health-check state transition (HAProxy `option log-health-checks`).",
    )
    http_check_path = models.CharField(
        max_length=255,
        blank=True,
        default="/",
        help_text="URI path for HTTP health checks (HAProxy `http-check send uri`).",
    )
    http_check_method = models.CharField(
        max_length=16,
        blank=True,
        default="",
        help_text="HTTP method for backend health checks (GET, HEAD, OPTIONS). "
        "Empty = platform default.",
    )
    custom_options = models.TextField(
        blank=True,
        default="",
        help_text="Raw HAProxy config lines injected into the backend (pass-thru). "
        "One line per option, e.g. 'default-server inter 5000 fall 5 rise 1'.",
    )
    fallback_nocheck = models.BooleanField(
        default=False,
        help_text="Auto-generate a no-health-check clone backend + nbsrv() frontend ACL "
        "so traffic is attempted even when all servers are down (never 503).",
    )

    class Meta:
        ordering = ["pool"]
        verbose_name = "LB Backend Tuning"
        verbose_name_plural = "LB Backend Tuning"

    def __str__(self):
        return f"{self.pool}: retries={self.retries}"

    def get_absolute_url(self):
        return reverse(
            "plugins:netbox_load_balancing_acl:lbbackendtuning", args=[self.pk]
        )


class LBFrontendTuning(NetBoxModel):
    """Satellite on ``netbox_load_balancing.Listener`` (the frontend) for custom
    pass-thru options that the upstream base plugin does not model.

    ``custom_options`` is the HAProxy frontend pass-thru: raw config lines injected
    after the generated config. Use for ``nbsrv()`` ACLs, ``use_backend`` fallbacks,
    and any setting not covered by typed fields or routing rules."""

    listener = models.OneToOneField(
        "netbox_load_balancing.Listener",
        on_delete=models.CASCADE,
        related_name="tuning",
        help_text="The listener (frontend) this tuning applies to.",
    )
    custom_options = models.TextField(
        blank=True,
        default="",
        help_text="Raw HAProxy config lines injected into the frontend (pass-thru). "
        "One line per option.",
    )

    class Meta:
        ordering = ["listener"]
        verbose_name = "LB Frontend Tuning"
        verbose_name_plural = "LB Frontend Tuning"

    def __str__(self):
        return f"{self.listener}: custom_options={'yes' if self.custom_options else 'no'}"

    def get_absolute_url(self):
        return reverse(
            "plugins:netbox_load_balancing_acl:lbfrontendtuning", args=[self.pk]
        )
