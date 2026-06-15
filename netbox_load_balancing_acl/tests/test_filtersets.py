# SPDX-License-Identifier: AGPL-3.0-or-later
"""FilterSet tests against a real DB (no mocks): listener / target-pool scoping + choice filters."""

from django.test import TestCase
from netbox_load_balancing.models import LBService, Listener, Pool
from netbox_load_balancing_acl.choices import LBRoutingMatchTypeChoices
from netbox_load_balancing_acl.filtersets import LBRoutingRuleFilterSet
from netbox_load_balancing_acl.models import LBRoutingRule


def _listener(name):
    service = LBService.objects.create(name=f"svc-{name}", reference=f"ref-{name}")
    return Listener.objects.create(name=name, service=service, port=443)


class LBRoutingRuleFilterSetTest(TestCase):
    queryset = LBRoutingRule.objects.all()

    @classmethod
    def setUpTestData(cls):
        cls.l1 = _listener("fe1")
        cls.l2 = _listener("fe2")
        cls.p1 = Pool.objects.create(name="pool1")
        cls.p2 = Pool.objects.create(name="pool2")
        LBRoutingRule.objects.create(
            listener=cls.l1,
            match_type=LBRoutingMatchTypeChoices.HOST,
            pattern="erp.zephyrex.ca",
            target_pool=cls.p1,
            order=10,
        )
        LBRoutingRule.objects.create(
            listener=cls.l1,
            match_type=LBRoutingMatchTypeChoices.SNI,
            pattern="secure.zephyrex.ca",
            target_pool=cls.p2,
            order=20,
        )
        LBRoutingRule.objects.create(
            listener=cls.l2,
            match_type=LBRoutingMatchTypeChoices.PATH_PREFIX,
            pattern="/api",
            target_pool=cls.p1,
            order=10,
        )

    def test_listener_id(self):
        self.assertEqual(
            LBRoutingRuleFilterSet({"listener_id": [self.l1.pk]}, self.queryset).qs.count(), 2
        )

    def test_target_pool_id(self):
        self.assertEqual(
            LBRoutingRuleFilterSet({"target_pool_id": [self.p1.pk]}, self.queryset).qs.count(), 2
        )

    def test_match_type(self):
        self.assertEqual(
            LBRoutingRuleFilterSet(
                {"match_type": [LBRoutingMatchTypeChoices.SNI]}, self.queryset
            ).qs.count(),
            1,
        )

    def test_search_pattern_and_listener(self):
        self.assertEqual(LBRoutingRuleFilterSet({"q": "zephyrex"}, self.queryset).qs.count(), 2)
        self.assertEqual(LBRoutingRuleFilterSet({"q": "fe2"}, self.queryset).qs.count(), 1)
