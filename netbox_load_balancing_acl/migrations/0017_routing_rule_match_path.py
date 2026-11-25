# SPDX-License-Identifier: AGPL-3.0-or-later
# A return action's optional path prefix (HAProxy path_beg, ANDed with the host match), so the edge
# answers one path of a host itself, e.g. robots.txt "Disallow: /" on every dev site (operator 2026-11-25).
# Hand-authored. Verify with makemigrations --check --dry-run.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_load_balancing_acl", "0016_drift_repair_tags_cfd_set_path"),
    ]

    operations = [
        migrations.AddField(
            model_name="lbroutingrule",
            name="match_path",
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
