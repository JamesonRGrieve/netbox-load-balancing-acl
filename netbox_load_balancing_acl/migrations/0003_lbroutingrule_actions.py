# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_load_balancing_acl --check --dry-run  (dev/ephemeral NetBox)
#
# Generalize LBRoutingRule from "use_backend host-route only" to "any HAProxy frontend
# action": add action_type + the header/redirect/acl-name fields, and relax match_type /
# pattern / target_pool to optional (a header or redirect action carries no ACL/pool).
# Existing rows are use_backend (the field default) so they are unchanged.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_load_balancing_acl", "0002_alter_lbroutingrule_target_pool"),
        ("netbox_load_balancing", "0007_alter_lbserviceassignment_assigned_object_type_and_more"),
    ]
    operations = [
        migrations.AddField(
            model_name="lbroutingrule",
            name="action_type",
            field=models.CharField(default="use_backend", max_length=32),
        ),
        migrations.AddField(
            model_name="lbroutingrule",
            name="acl_name",
            field=models.CharField(blank=True, default="", max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="lbroutingrule",
            name="case_sensitive",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="lbroutingrule",
            name="header_name",
            field=models.CharField(blank=True, default="", max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="lbroutingrule",
            name="header_value",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="lbroutingrule",
            name="redirect_rule",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="lbroutingrule",
            name="match_type",
            field=models.CharField(blank=True, max_length=16),
        ),
        migrations.AlterField(
            model_name="lbroutingrule",
            name="pattern",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="lbroutingrule",
            name="target_pool",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="routing_rules",
                to="netbox_load_balancing.pool",
            ),
        ),
    ]
