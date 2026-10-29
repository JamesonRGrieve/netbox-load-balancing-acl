# SPDX-License-Identifier: AGPL-3.0-or-later
"""Model tests against a real DB (no mocks): creation, str/url/color, the (listener, order)
uniqueness constraint, CASCADE from the listener, and PROTECT on the target pool. Real
netbox_load_balancing Listener + Pool instances back every routing rule.

LBMemberHA is exercised against real Member / Pool / MemberAssignment rows — the HA role hangs
off the assignment (the server line), so the tests assert the one-to-one, the CASCADE from the
assignment, and that clean() refuses a health-monitor assignment."""

import importlib

from django.apps import apps as django_apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import ProtectedError
from django.db.utils import IntegrityError
from django.test import TestCase
from ipam.models import IPAddress
from netbox_load_balancing.models import (
    HealthMonitor,
    LBService,
    Listener,
    Member,
    MemberAssignment,
    Pool,
)
from netbox_load_balancing_acl.choices import (
    LBRoutingActionTypeChoices,
    LBRoutingMatchTypeChoices,
)
from netbox_load_balancing_acl.models import (
    CLOUDFLARE_ORIGIN_TIMEOUT_SECONDS,
    EDGE_REQUEST_TIMEOUT_SECONDS,
    LBAcl,
    LBBackendTuning,
    LBFrontendTuning,
    LBMemberHA,
    LBRoutingRule,
)
from netbox_pki.choices import CATypeChoices
from netbox_pki.models import PkiCertificateAuthority


def make_listener(name="fe"):
    service = LBService.objects.create(name=f"svc-{name}", reference=f"ref-{name}")
    return Listener.objects.create(name=name, service=service, port=443)


def make_pool(name="pool"):
    return Pool.objects.create(name=name)


def make_member(name, address):
    ip = IPAddress.objects.create(address=address)
    return Member.objects.create(name=name, reference=f"ref-{name}", ip_address=ip)


def make_assignment(target, member):
    return MemberAssignment.objects.create(
        assigned_object_type=ContentType.objects.get_for_model(target),
        assigned_object_id=target.pk,
        member=member,
    )


class LBRoutingRuleModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.listener = make_listener("fe1")
        cls.pool = make_pool("pool1")

    def test_create_str_url_color_defaults(self):
        r = LBRoutingRule.objects.create(
            listener=self.listener,
            match_type=LBRoutingMatchTypeChoices.HOST,
            pattern="erp.zephyrex.ca",
            target_pool=self.pool,
        )
        self.assertIn("erp.zephyrex.ca", str(r))
        self.assertIn("/plugins/lb-acl/routing-rules/", r.get_absolute_url())
        self.assertEqual(r.order, 100)
        self.assertFalse(r.negate)
        self.assertEqual(r.get_match_type_color(), "blue")

    def test_unique_listener_order(self):
        LBRoutingRule.objects.create(
            listener=self.listener,
            match_type=LBRoutingMatchTypeChoices.HOST,
            pattern="a.example",
            target_pool=self.pool,
            order=10,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            LBRoutingRule.objects.create(
                listener=self.listener,
                match_type=LBRoutingMatchTypeChoices.SNI,
                pattern="b.example",
                target_pool=self.pool,
                order=10,
            )

    def test_same_order_distinct_listeners_allowed(self):
        other = make_listener("fe2")
        LBRoutingRule.objects.create(
            listener=self.listener,
            match_type=LBRoutingMatchTypeChoices.HOST,
            pattern="a.example",
            target_pool=self.pool,
            order=5,
        )
        r2 = LBRoutingRule.objects.create(
            listener=other,
            match_type=LBRoutingMatchTypeChoices.HOST,
            pattern="a.example",
            target_pool=self.pool,
            order=5,
        )
        self.assertEqual(r2.order, 5)

    def test_cascade_from_listener(self):
        r = LBRoutingRule.objects.create(
            listener=self.listener,
            match_type=LBRoutingMatchTypeChoices.PATH_PREFIX,
            pattern="/api",
            target_pool=self.pool,
        )
        pk = r.pk
        self.listener.delete()
        self.assertFalse(LBRoutingRule.objects.filter(pk=pk).exists())

    def test_protect_target_pool(self):
        protected_pool = make_pool("protected")
        LBRoutingRule.objects.create(
            listener=self.listener,
            match_type=LBRoutingMatchTypeChoices.HOST,
            pattern="keep.example",
            target_pool=protected_pool,
        )
        with self.assertRaises(ProtectedError), transaction.atomic():
            protected_pool.delete()

    # ── action-type generalization (header / redirect / match-variants) ──

    def test_use_backend_is_default_action(self):
        r = LBRoutingRule.objects.create(
            listener=self.listener,
            match_type=LBRoutingMatchTypeChoices.HOST_MATCHES,
            pattern="erp.zephyrex.ca",
            target_pool=self.pool,
        )
        self.assertEqual(r.action_type, LBRoutingActionTypeChoices.USE_BACKEND)
        self.assertEqual(r.get_match_type_color(), "indigo")  # host_matches
        self.assertEqual(r.get_action_type_color(), "blue")

    def test_header_action_no_pool(self):
        r = LBRoutingRule.objects.create(
            listener=self.listener,
            action_type=LBRoutingActionTypeChoices.SET_HEADER_REQUEST,
            header_name="X-Forwarded-Proto",
            header_value="https",
            order=11,
        )
        r.full_clean()  # must not raise (no pool / no match required)
        self.assertIsNone(r.target_pool)
        self.assertIn("X-Forwarded-Proto", str(r))

    def test_redirect_action_no_pool(self):
        r = LBRoutingRule.objects.create(
            listener=self.listener,
            action_type=LBRoutingActionTypeChoices.REDIRECT,
            redirect_rule="scheme https code 301",
            order=12,
        )
        r.full_clean()
        self.assertIn("redirect", str(r))

    def test_clean_use_backend_requires_pool_and_match(self):
        r = LBRoutingRule(
            listener=self.listener,
            action_type=LBRoutingActionTypeChoices.USE_BACKEND,
            pattern="x.example",
            order=13,
        )  # no target_pool
        with self.assertRaises(ValidationError):
            r.clean()

    def test_clean_redirect_requires_rule(self):
        r = LBRoutingRule(
            listener=self.listener,
            action_type=LBRoutingActionTypeChoices.REDIRECT,
            order=14,
        )
        with self.assertRaises(ValidationError):
            r.clean()

    def test_clean_return_requires_match_type_and_body(self):
        r = LBRoutingRule(
            listener=self.listener, action_type=LBRoutingActionTypeChoices.RETURN_REQUEST, order=15,
            return_content_type="text/plain", return_body="version: STSv1\n",
        )
        with self.assertRaises(ValidationError):
            r.clean()  # no match_type
        r.match_type, r.pattern = "host", "mta-sts.example.com"
        r.return_body = ""
        with self.assertRaises(ValidationError):
            r.clean()  # no body
        r.return_body = "version: STSv1\nmode: testing\n"
        r.return_status = 999
        with self.assertRaises(ValidationError):
            r.clean()  # not an HTTP status
        r.return_status = 200
        r.clean()
        r.save()
        self.assertIn("return 200 if host mta-sts.example.com", str(r))

    def test_clean_set_header_requires_name(self):
        r = LBRoutingRule(
            listener=self.listener,
            action_type=LBRoutingActionTypeChoices.SET_HEADER_RESPONSE,
            header_value="nginx",
            order=15,
        )
        with self.assertRaises(ValidationError):
            r.clean()

    def test_default_backend_action(self):
        r = LBRoutingRule.objects.create(
            listener=self.listener,
            action_type=LBRoutingActionTypeChoices.DEFAULT_BACKEND,
            target_pool=self.pool,
            order=16,
        )
        r.full_clean()  # no match_type / acl_name / pattern required
        self.assertEqual(r.action_type, LBRoutingActionTypeChoices.DEFAULT_BACKEND)
        self.assertEqual(r.get_action_type_color(), "green")
        self.assertIn("default_backend", str(r))
        self.assertEqual(r.target_pool, self.pool)

    def test_clean_default_backend_requires_pool(self):
        r = LBRoutingRule(
            listener=self.listener,
            action_type=LBRoutingActionTypeChoices.DEFAULT_BACKEND,
            order=17,
        )  # no target_pool
        with self.assertRaises(ValidationError):
            r.clean()


class LBAclModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.listener = make_listener("fe-acl")

    def test_create_and_str(self):
        a = LBAcl.objects.create(
            listener=self.listener, order=0, name="acl_mail",
            match_type=LBRoutingMatchTypeChoices.HOST_STARTS_WITH, pattern="mail.",
        )
        self.assertIn("acl_mail", str(a))
        self.assertIn("/plugins/lb-acl/acls/", a.get_absolute_url())
        self.assertEqual(a.get_match_type_color(), "cyan")

    def test_duplicate_names_allowed(self):
        # pfSense permits two ACLs with the same name (OR of conditions) — distinct order.
        LBAcl.objects.create(listener=self.listener, order=0, name="acl_wp_bighearts",
                             match_type=LBRoutingMatchTypeChoices.HOST_CONTAINS, pattern="x.com")
        a2 = LBAcl.objects.create(listener=self.listener, order=1, name="acl_wp_bighearts",
                                  match_type=LBRoutingMatchTypeChoices.HOST_MATCHES, pattern="x.com")
        self.assertEqual(LBAcl.objects.filter(name="acl_wp_bighearts").count(), 2)
        self.assertEqual(a2.order, 1)

    def test_unique_listener_order(self):
        LBAcl.objects.create(listener=self.listener, order=5, name="a",
                             match_type=LBRoutingMatchTypeChoices.HOST_MATCHES, pattern="a")
        with self.assertRaises(IntegrityError), transaction.atomic():
            LBAcl.objects.create(listener=self.listener, order=5, name="b",
                                 match_type=LBRoutingMatchTypeChoices.HOST_MATCHES, pattern="b")


class LBMemberHAModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pool = make_pool("wp_tolley_pool")
        cls.primary = make_member("wp_tolley_pool-wordpress", "203.0.113.6/25")
        cls.mirror = make_member("wp_tolley_pool-mirror", "198.18.0.6/24")
        cls.primary_assignment = make_assignment(cls.pool, cls.primary)
        cls.mirror_assignment = make_assignment(cls.pool, cls.mirror)

    def test_defaults_to_backup(self):
        ha = LBMemberHA.objects.create(assignment=self.mirror_assignment)
        ha.full_clean()
        self.assertTrue(ha.backup)
        self.assertIn("backup", str(ha))
        self.assertIn("/plugins/lb-acl/member-ha/", ha.get_absolute_url())

    def test_member_and_pool_properties(self):
        ha = LBMemberHA.objects.create(assignment=self.mirror_assignment)
        self.assertEqual(ha.member, self.mirror)
        self.assertEqual(ha.pool, self.pool)

    def test_explicit_active_role(self):
        ha = LBMemberHA.objects.create(assignment=self.primary_assignment, backup=False)
        ha.full_clean()
        self.assertIn("active", str(ha))

    def test_one_role_per_assignment(self):
        LBMemberHA.objects.create(assignment=self.mirror_assignment)
        with self.assertRaises(IntegrityError), transaction.atomic():
            LBMemberHA.objects.create(assignment=self.mirror_assignment, backup=False)

    def test_cascade_from_assignment(self):
        ha = LBMemberHA.objects.create(assignment=self.mirror_assignment)
        pk = ha.pk
        self.mirror_assignment.delete()
        self.assertFalse(LBMemberHA.objects.filter(pk=pk).exists())

    def test_clean_rejects_health_monitor_assignment(self):
        monitor = HealthMonitor.objects.create(name="wp-http-check")
        ha = LBMemberHA(assignment=make_assignment(monitor, self.mirror))
        with self.assertRaises(ValidationError):
            ha.clean()

    def test_member_port_defaults_null(self):
        # Absent override => fall back to the pool's member_port (unchanged behaviour).
        ha = LBMemberHA.objects.create(assignment=self.mirror_assignment)
        ha.full_clean()
        self.assertIsNone(ha.member_port)

    def test_member_port_override_accepted(self):
        # §2133: the house-edge backup forwards to the mTLS Receiver on :443 while the
        # pool's primary WordPress members stay :80.
        ha = LBMemberHA.objects.create(assignment=self.mirror_assignment, member_port=443)
        ha.full_clean()
        self.assertEqual(LBMemberHA.objects.get(pk=ha.pk).member_port, 443)

    def test_member_port_out_of_range_rejected(self):
        ha = LBMemberHA(assignment=self.mirror_assignment, member_port=70000)
        with self.assertRaises(ValidationError):
            ha.full_clean()


class LBFrontendTuningClientAuthModelTest(TestCase):
    """The §2133 house Receiver: its frontend trusts the Cloudflare origin-pull CAs plus the
    omg-edge-failover CA, referenced on the device by each CA's trust_refid."""

    @classmethod
    def setUpTestData(cls):
        cls.cf = PkiCertificateAuthority.objects.create(
            name="cf-origin-pull", ca_type=CATypeChoices.EXTERNAL, trust_refid="6a9ac549cc8d0"
        )
        cls.failover = PkiCertificateAuthority.objects.create(
            name="omg-edge-failover CA 2026", ca_type=CATypeChoices.SELF_SIGNED, trust_refid="0e2133fa11ca0"
        )

    def test_client_auth_cas_default_empty(self):
        tuning = make_listener("plain").tuning
        tuning.full_clean()
        self.assertFalse(tuning.client_auth_cas.exists())

    def test_client_auth_cas_saved(self):
        tuning = make_listener("receiver").tuning
        tuning.client_auth_cas.set([self.cf, self.failover])
        tuning.full_clean()
        stored = LBFrontendTuning.objects.get(pk=tuning.pk)
        self.assertEqual(
            sorted(stored.client_auth_cas.values_list("trust_refid", flat=True)), ["0e2133fa11ca0", "6a9ac549cc8d0"]
        )

    def test_deleting_ca_drops_only_the_link(self):
        tuning = make_listener("drop").tuning
        tuning.client_auth_cas.set([self.cf, self.failover])
        self.failover.delete()
        self.assertEqual(list(LBFrontendTuning.objects.get(pk=tuning.pk).client_auth_cas.all()), [self.cf])

    def test_reverse_accessor_from_ca(self):
        tuning = make_listener("rev").tuning
        tuning.client_auth_cas.add(self.cf)
        self.assertEqual(list(self.cf.lb_frontend_tunings.all()), [tuning])


class EdgeRequestTimeoutTest(TestCase):
    """Edge timeouts are NetBox intent with a default 1 s past Cloudflare's fixed origin timeout:
    every pool/listener gets a tuning row automatically, and nothing may be set at or below
    Cloudflare's timeout (the edge must never cut a request first)."""

    def test_new_pool_gets_backend_tuning_with_default(self):
        tuning = LBBackendTuning.objects.get(pool=make_pool("auto-pool"))
        self.assertEqual(tuning.timeout_server, CLOUDFLARE_ORIGIN_TIMEOUT_SECONDS + 1)
        self.assertEqual(tuning.timeout_server, EDGE_REQUEST_TIMEOUT_SECONDS)

    def test_new_listener_gets_frontend_tuning_with_default(self):
        tuning = LBFrontendTuning.objects.get(listener=make_listener("auto-fe"))
        self.assertEqual(tuning.timeout_client, EDGE_REQUEST_TIMEOUT_SECONDS)

    def test_timeouts_at_or_below_cloudflare_rejected(self):
        backend = make_pool("bad-pool").tuning
        backend.timeout_server = CLOUDFLARE_ORIGIN_TIMEOUT_SECONDS
        with self.assertRaises(ValidationError):
            backend.full_clean()
        frontend = make_listener("bad-fe").tuning
        frontend.timeout_client = 30
        with self.assertRaises(ValidationError):
            frontend.full_clean()

    def test_longer_override_allowed(self):
        backend = make_pool("slow-pool").tuning
        backend.timeout_server = 300
        backend.full_clean()
        backend.save()
        self.assertEqual(LBBackendTuning.objects.get(pk=backend.pk).timeout_server, 300)

    def test_saving_existing_pool_does_not_duplicate_tuning(self):
        pool = make_pool("resave")
        pool.description = "edited"
        pool.save()
        self.assertEqual(LBBackendTuning.objects.filter(pool=pool).count(), 1)

    def test_backfill_creates_rows_only_where_missing(self):
        # Pools/listeners that predate the signal (rows removed here to simulate them) are
        # backfilled by migration 0013 with the default; existing rows are left untouched.
        untuned_pool = make_pool("legacy-pool")
        untuned_fe = make_listener("legacy-fe")
        LBBackendTuning.objects.filter(pool=untuned_pool).delete()
        LBFrontendTuning.objects.filter(listener=untuned_fe).delete()
        kept = make_pool("kept-pool").tuning
        kept.timeout_server = 200
        kept.save()
        migration = importlib.import_module("netbox_load_balancing_acl.migrations.0013_edge_request_timeouts")
        migration.backfill_tuning_rows(django_apps, None)
        self.assertEqual(LBBackendTuning.objects.get(pool=untuned_pool).timeout_server, EDGE_REQUEST_TIMEOUT_SECONDS)
        self.assertEqual(LBFrontendTuning.objects.get(listener=untuned_fe).timeout_client, EDGE_REQUEST_TIMEOUT_SECONDS)
        self.assertEqual(LBBackendTuning.objects.get(pk=kept.pk).timeout_server, 200)
        self.assertEqual(LBBackendTuning.objects.filter(pool=untuned_pool).count(), 1)
