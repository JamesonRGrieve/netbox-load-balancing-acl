# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.routers import NetBoxRouter
from . import views

app_name = "netbox_load_balancing_acl"

router = NetBoxRouter()
router.register("routing-rules", views.LBRoutingRuleViewSet)

urlpatterns = router.urls
