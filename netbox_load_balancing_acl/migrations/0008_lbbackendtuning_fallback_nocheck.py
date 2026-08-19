# SPDX-License-Identifier: AGPL-3.0-or-later
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_load_balancing_acl", "0007_haproxy_tuning_satellites"),
    ]

    operations = [
        migrations.AddField(
            model_name="lbbackendtuning",
            name="fallback_nocheck",
            field=models.BooleanField(
                default=False,
                help_text="Auto-generate a no-health-check clone backend + nbsrv() frontend ACL "
                "so traffic is attempted even when all servers are down (never 503).",
            ),
        ),
    ]
