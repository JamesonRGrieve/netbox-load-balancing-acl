# SPDX-License-Identifier: AGPL-3.0-or-later
"""FilterSet tests against a real DB (no mocks): listener / target-pool scoping + choice filters.
LBMemberHA additionally covers the pool filter, which traverses the assignment's generic FK."""

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from ipam.models import IPAddress
from netbox_load_balancing.models import (
    LBService,
    Listener,
    Member,
    MemberAssignment,
    Pool,
)
from netbox_load_balancing_acl.choices import LBRoutingMatchTypeChoices
from netbox_load_balancing_acl.filtersets import LBMemberHAFilterSet, LBRoutingRuleFilterSet
from netbox_load_balancing_acl.models import LBMemberHA, LBRoutingRule


def _listener(name):
    service = LBService.objects.create(name=f"svc-{name}", reference=f"ref-{name}")
    return Listener.objects.create(name=name, service=service, port=443)


def _assignment(pool, name, address):
    ip = IPAddress.objects.create(address=address)
    member = Member.objects.create(name=name, reference=f"ref-{name}", ip_address=ip)
    return MemberAssignment.objects.create(
        assigned_object_type=ContentType.objects.get_for_model(pool),
        assigned_object_id=pool.pk,
        member=member,
    )


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


class LBMemberHAFilterSetTest(TestCase):
    queryset = LBMemberHA.objects.all()

    @classmethod
    def setUpTestData(cls):
        cls.tolley = Pool.objects.create(name="wp_tolley_pool")
        cls.parker = Pool.objects.create(name="wp_parker_pool")
        tolley_primary = _assignment(cls.tolley, "tolley-wordpress", "203.0.113.6/25")
        cls.tolley_mirror = _assignment(cls.tolley, "tolley-mirror", "198.18.0.6/24")
        parker_mirror = _assignment(cls.parker, "parker-mirror", "198.18.0.19/24")

        LBMemberHA.objects.create(assignment=tolley_primary, backup=False)
        LBMemberHA.objects.create(
            assignment=cls.tolley_mirror, backup=True, description="house mirror"
        )
        LBMemberHA.objects.create(assignment=parker_mirror, backup=True)

    def test_pool_id(self):
        self.assertEqual(
            LBMemberHAFilterSet({"pool_id": [self.tolley.pk]}, self.queryset).qs.count(), 2
        )
        self.assertEqual(
            LBMemberHAFilterSet({"pool_id": [self.parker.pk]}, self.queryset).qs.count(), 1
        )

    def test_member_id(self):
        self.assertEqual(
            LBMemberHAFilterSet(
                {"member_id": [self.tolley_mirror.member.pk]}, self.queryset
            ).qs.count(),
            1,
        )

    def test_backup(self):
        self.assertEqual(LBMemberHAFilterSet({"backup": True}, self.queryset).qs.count(), 2)
        self.assertEqual(LBMemberHAFilterSet({"backup": False}, self.queryset).qs.count(), 1)

    def test_search_member_name_and_description(self):
        self.assertEqual(LBMemberHAFilterSet({"q": "parker"}, self.queryset).qs.count(), 1)
        self.assertEqual(LBMemberHAFilterSet({"q": "house mirror"}, self.queryset).qs.count(), 1)
