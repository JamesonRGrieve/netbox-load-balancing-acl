# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_load_balancing_acl --check --dry-run  (dev/ephemeral NetBox)
#
# Repoint LBRoutingRule.target_pool from netbox_load_balancing.VirtualIPPool (the FRONTEND VIP,
# upstream `virtual-pools`) to netbox_load_balancing.Pool (the BACKEND server pool, upstream
# `pools`). The original FK was a class-name conflation: a host/path ACL routes matched traffic
# to a backend POOL, not a frontend VIP. Both target tables exist by netbox_load_balancing's
# 0001_initial; we keep the same latest-migration dependency as 0001_initial. Safe AlterField —
# no rows reference target_pool yet.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_load_balancing_acl", "0001_initial"),
        (
            "netbox_load_balancing",
            "0007_alter_lbserviceassignment_assigned_object_type_and_more",
        ),
    ]
    operations = [
        migrations.AlterField(
            model_name="lbroutingrule",
            name="target_pool",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="routing_rules",
                to="netbox_load_balancing.pool",
            ),
        ),
    ]
