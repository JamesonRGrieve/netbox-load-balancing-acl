# SPDX-License-Identifier: AGPL-3.0-or-later
"""Model tests against a real DB (no mocks): creation, str/url/color, the (listener, order)
uniqueness constraint, CASCADE from the listener, and PROTECT on the target pool. Real
netbox_load_balancing Listener + Pool instances back every routing rule."""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import ProtectedError
from django.db.utils import IntegrityError
from django.test import TestCase
from netbox_load_balancing.models import LBService, Listener, Pool
from netbox_load_balancing_acl.choices import (
    LBRoutingActionTypeChoices,
    LBRoutingMatchTypeChoices,
)
from netbox_load_balancing_acl.models import LBRoutingRule


def make_listener(name="fe"):
    service = LBService.objects.create(name=f"svc-{name}", reference=f"ref-{name}")
    return Listener.objects.create(name=name, service=service, port=443)


def make_pool(name="pool"):
    return Pool.objects.create(name=name)


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

    def test_clean_set_header_requires_name(self):
        r = LBRoutingRule(
            listener=self.listener,
            action_type=LBRoutingActionTypeChoices.SET_HEADER_RESPONSE,
            header_value="nginx",
            order=15,
        )
        with self.assertRaises(ValidationError):
            r.clean()
