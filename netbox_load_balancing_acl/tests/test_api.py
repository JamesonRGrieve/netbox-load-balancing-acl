# SPDX-License-Identifier: AGPL-3.0-or-later
"""REST API CRUD tests against a real DB + real API client (no mocks).

Composes the explicit CRUD mixins (not the GraphQL-inclusive APIViewTestCase) since the plugin
ships no GraphQL type yet. Each created rule needs a fresh listener so the (listener, order)
uniqueness constraint never trips inside the create batch; pools are real Pool rows."""

from netbox_load_balancing.models import LBService, Listener, Pool
from utilities.testing import APIViewTestCases
from netbox_load_balancing_acl.models import LBAcl, LBRoutingRule


def _listener(name):
    service = LBService.objects.create(name=f"svc-{name}", reference=f"ref-{name}")
    return Listener.objects.create(name=name, service=service, port=443)


# Inherit the CRUD mixins directly: an intermediate mixin class is itself discovered
# by the test loader and run with model=None. Compose on the concrete test case so only
# this (model-bound) class is collected.
class LBRoutingRuleAPITest(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = LBRoutingRule
    brief_fields = ["action_type", "display", "id", "listener", "order", "url"]
    bulk_update_data = {"negate": True}

    @classmethod
    def setUpTestData(cls):
        pool = Pool.objects.create(name="api-pool")
        existing = [_listener(f"ex{i}") for i in range(3)]
        LBRoutingRule.objects.bulk_create(
            [
                LBRoutingRule(listener=lst, match_type="host", pattern=f"ex{i}.example", target_pool=pool)
                for i, lst in enumerate(existing)
            ]
        )
        fresh = [_listener(f"new{i}") for i in range(5)]
        cls.create_data = [
            # use_backend with a pfSense host match-variant
            {
                "listener": fresh[0].pk,
                "action_type": "use_backend",
                "acl_name": "acl_erp",
                "match_type": "host_matches",
                "pattern": "erp.zephyrex.ca",
                "target_pool": pool.pk,
                "order": 10,
            },
            {
                "listener": fresh[1].pk,
                "action_type": "use_backend",
                "match_type": "sni",
                "pattern": "secure.zephyrex.ca",
                "target_pool": pool.pk,
                "order": 20,
                "negate": True,
            },
            # set-header request (no acl / no pool)
            {
                "listener": fresh[2].pk,
                "action_type": "http-request_set-header",
                "header_name": "X-Forwarded-Proto",
                "header_value": "https",
                "order": 30,
            },
            # set-header response
            {
                "listener": fresh[3].pk,
                "action_type": "http-response_set-header",
                "header_name": "Server",
                "header_value": "nginx",
                "order": 40,
            },
            # redirect (no acl / no pool)
            {
                "listener": fresh[4].pk,
                "action_type": "http-request_redirect",
                "redirect_rule": "scheme https code 301",
                "order": 50,
            },
        ]


class LBAclAPITest(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = LBAcl
    brief_fields = ["display", "id", "listener", "name", "order", "url"]
    bulk_update_data = {"negate": True}

    @classmethod
    def setUpTestData(cls):
        existing = [_listener(f"acl-ex{i}") for i in range(3)]
        LBAcl.objects.bulk_create(
            [LBAcl(listener=lst, order=0, name=f"acl_ex{i}", match_type="host_matches", pattern=f"ex{i}.com")
             for i, lst in enumerate(existing)]
        )
        fresh = [_listener(f"acl-new{i}") for i in range(3)]
        cls.create_data = [
            {"listener": fresh[0].pk, "order": 0, "name": "acl_mail", "match_type": "host_starts_with", "pattern": "mail."},
            # duplicate name on a different listener+order is fine
            {"listener": fresh[1].pk, "order": 0, "name": "acl_mail", "match_type": "host_contains", "pattern": "mail2"},
            {"listener": fresh[2].pk, "order": 1, "name": "acl_path", "match_type": "host_matches", "pattern": "x.com", "negate": True},
        ]
