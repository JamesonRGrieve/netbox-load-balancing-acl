# SPDX-License-Identifier: AGPL-3.0-or-later
"""REST API CRUD tests against a real DB + real API client (no mocks).

Composes the explicit CRUD mixins (not the GraphQL-inclusive APIViewTestCase) since the plugin
ships no GraphQL type yet. Each created rule needs a fresh listener so the (listener, order)
uniqueness constraint never trips inside the create batch; pools are real VirtualIPPool rows."""

from netbox_load_balancing.models import LBService, Listener, VirtualIPPool
from utilities.testing import APIViewTestCases
from netbox_load_balancing_acl.models import LBRoutingRule


class _CRUD(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    pass


def _listener(name):
    service = LBService.objects.create(name=f"svc-{name}", reference=f"ref-{name}")
    return Listener.objects.create(name=name, service=service, port=443)


class LBRoutingRuleAPITest(_CRUD):
    model = LBRoutingRule
    brief_fields = ["display", "id", "listener", "match_type", "pattern", "url"]
    bulk_update_data = {"negate": True}

    @classmethod
    def setUpTestData(cls):
        pool = VirtualIPPool.objects.create(name="api-pool")
        existing = [_listener(f"ex{i}") for i in range(3)]
        LBRoutingRule.objects.bulk_create(
            [
                LBRoutingRule(listener=lst, match_type="host", pattern=f"ex{i}.example", target_pool=pool)
                for i, lst in enumerate(existing)
            ]
        )
        fresh = [_listener(f"new{i}") for i in range(3)]
        cls.create_data = [
            {
                "listener": fresh[0].pk,
                "match_type": "host",
                "pattern": "erp.zephyrex.ca",
                "target_pool": pool.pk,
                "order": 10,
            },
            {
                "listener": fresh[1].pk,
                "match_type": "sni",
                "pattern": "secure.zephyrex.ca",
                "target_pool": pool.pk,
                "order": 20,
                "negate": True,
            },
            {
                "listener": fresh[2].pk,
                "match_type": "path_prefix",
                "pattern": "/api",
                "target_pool": pool.pk,
                "order": 30,
            },
        ]
