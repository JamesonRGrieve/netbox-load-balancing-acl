# SPDX-License-Identifier: AGPL-3.0-or-later
# An http-request return action: the edge answers a matched request itself (status, content type, body),
# e.g. an MTA-STS policy on mta-sts.<domain>. Hand-authored; verify with makemigrations --check --dry-run.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_load_balancing_acl", "0013_edge_request_timeouts"),
    ]

    operations = [
        migrations.AddField(
            model_name="lbroutingrule",
            name="return_status",
            field=models.PositiveSmallIntegerField(default=200),
        ),
        migrations.AddField(
            model_name="lbroutingrule",
            name="return_content_type",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="lbroutingrule",
            name="return_body",
            field=models.TextField(blank=True),
        ),
    ]
