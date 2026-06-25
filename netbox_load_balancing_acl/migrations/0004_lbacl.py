# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_load_balancing_acl --check --dry-run  (dev/ephemeral NetBox)
#
# Add LBAcl — first-class, ordered, duplicate-name-capable HAProxy ACL objects, so an
# adopted pfSense frontend's ha_acls array can be reproduced position-for-position (incl.
# same-named ACLs that OR their conditions). Additive; LBRoutingRule is unchanged.
import django.db.models.deletion
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_load_balancing_acl", "0003_lbroutingrule_actions"),
        ("netbox_load_balancing", "0007_alter_lbserviceassignment_assigned_object_type_and_more"),
        ("extras", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="LBAcl",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ("order", models.PositiveIntegerField(default=100)),
                ("name", models.CharField(max_length=64)),
                ("match_type", models.CharField(max_length=16)),
                ("pattern", models.CharField(max_length=255)),
                ("case_sensitive", models.BooleanField(default=False)),
                ("negate", models.BooleanField(default=False)),
                ("listener", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="acls", to="netbox_load_balancing.listener")),
                ("tags", models.ManyToManyField(blank=True, related_name="+", to="extras.tag")),
            ],
            options={
                "verbose_name": "LB ACL",
                "verbose_name_plural": "LB ACLs",
                "ordering": ["listener", "order"],
            },
        ),
        migrations.AddConstraint(
            model_name="lbacl",
            constraint=models.UniqueConstraint(fields=("listener", "order"), name="lb_acl_listener_order"),
        ),
    ]
