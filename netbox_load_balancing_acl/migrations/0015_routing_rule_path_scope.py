# SPDX-License-Identifier: AGPL-3.0-or-later
# A set-path action's path scope: root (only /, every rule made before this migration) or all (every path
# not in exclude_paths; set_path carries %[path]), for vanity hosts that prefix an org path (card 406).
# Hand-authored; the ChoiceSet is app-level. Verify with makemigrations --check --dry-run.
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_load_balancing_acl", "0014_routing_rule_return"),
    ]

    operations = [
        migrations.AddField(
            model_name="lbroutingrule",
            name="path_scope",
            field=models.CharField(default="root", max_length=8),
        ),
        migrations.AddField(
            model_name="lbroutingrule",
            name="exclude_paths",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=128), blank=True, default=list, size=None
            ),
        ),
    ]
