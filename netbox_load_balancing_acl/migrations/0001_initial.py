# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored initial migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_load_balancing_acl --check --dry-run  (dev/ephemeral NetBox)
#
# LBRoutingRule FKs netbox_load_balancing.Listener (CASCADE) + VirtualIPPool (PROTECT). Both tables
# are created in netbox_load_balancing's 0001_initial; we depend on that app's LATEST migration
# (0007) so every table + later alteration exists before this CreateModel runs. The (listener, order)
# UniqueConstraint enforces a single rule per evaluation slot per listener at the DB level.
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("extras", "0001_initial"),
        (
            "netbox_load_balancing",
            "0007_alter_lbserviceassignment_assigned_object_type_and_more",
        ),
    ]
    operations = [
        migrations.CreateModel(
            name="LBRoutingRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder
                    ),
                ),
                ("match_type", models.CharField(max_length=16)),
                ("pattern", models.CharField(max_length=255)),
                ("order", models.PositiveIntegerField(default=100)),
                ("negate", models.BooleanField(default=False)),
                (
                    "listener",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="routing_rules",
                        to="netbox_load_balancing.listener",
                    ),
                ),
                (
                    "target_pool",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="routing_rules",
                        to="netbox_load_balancing.virtualippool",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag"),
                ),
            ],
            options={"verbose_name": "LB Routing Rule", "ordering": ["listener", "order"]},
        ),
        migrations.AddConstraint(
            model_name="lbroutingrule",
            constraint=models.UniqueConstraint(
                fields=("listener", "order"), name="lb_acl_routing_rule_listener_order"
            ),
        ),
    ]
