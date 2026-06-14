# SPDX-License-Identifier: AGPL-3.0-or-later
"""Model tests against a real DB (no mocks): creation, str/url/color, the (listener, order)
uniqueness constraint, CASCADE from the listener, and PROTECT on the target pool. Real
netbox_load_balancing Listener + VirtualIPPool instances back every routing rule."""

from django.db import transaction
from django.db.models import ProtectedError
from django.db.utils import IntegrityError
from django.test import TestCase
from netbox_load_balancing.models import LBService, Listener, VirtualIPPool
from netbox_load_balancing_acl.choices import LBRoutingMatchTypeChoices
from netbox_load_balancing_acl.models import LBRoutingRule


def make_listener(name="fe"):
    service = LBService.objects.create(name=f"svc-{name}", reference=f"ref-{name}")
    return Listener.objects.create(name=name, service=service, port=443)


def make_pool(name="pool"):
    return VirtualIPPool.objects.create(name=name)


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
