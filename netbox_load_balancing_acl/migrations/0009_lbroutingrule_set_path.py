# SPDX-License-Identifier: AGPL-3.0-or-later
# Add the set-path action target to LBRoutingRule: a transparent request-path
# rewrite (HAProxy `http-request set-path`), scoped by the rule's match. The new
# action_type choice `http-request_set-path` is app-level (ChoiceSets are not
# serialized into migrations — see 0003's action_type field), so only the field
# is added here. Existing rows carry set_path="" and are unaffected.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_load_balancing_acl", "0008_lbbackendtuning_fallback_nocheck"),
    ]

    operations = [
        migrations.AddField(
            model_name="lbroutingrule",
            name="set_path",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
