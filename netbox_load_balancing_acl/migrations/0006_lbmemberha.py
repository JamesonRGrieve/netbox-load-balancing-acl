# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_load_balancing_acl --check --dry-run  (dev/ephemeral NetBox)
#
# Add LBMemberHA — the HAProxy `backup` keyword as a one-to-one satellite on the upstream
# MemberAssignment (the pool↔member through-model, i.e. one backend server line). Absence of a
# row means active; a row declares a standby. Additive; existing models unchanged.
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_load_balancing_acl", "0005_lblistenercertificate"),
        ("netbox_load_balancing", "0007_alter_lbserviceassignment_assigned_object_type_and_more"),
        ("extras", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="LBMemberHA",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ("backup", models.BooleanField(default=True)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("assignment", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="ha", to="netbox_load_balancing.memberassignment")),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "LB Member HA",
                "verbose_name_plural": "LB Member HA",
                "ordering": ["assignment"],
            },
        ),
    ]
