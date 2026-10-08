# SPDX-License-Identifier: AGPL-3.0-or-later
# Edge request timeouts as NetBox intent: LBBackendTuning.timeout_server and
# LBFrontendTuning.timeout_client, defaulting to 1 s past Cloudflare's fixed 100 s origin timeout.
# The default only reaches pools/listeners that HAVE a tuning row, so this also backfills a
# default-valued row for every pool and listener without one (22/106 pools and 3/6 listeners had
# rows on 2026-10-08). New pools/listeners get theirs from the post_save signal in signals.py.
import django.core.validators
from django.db import migrations, models

EDGE_REQUEST_TIMEOUT_SECONDS = 101  # literal on purpose: a migration must not import live model code


def backfill_tuning_rows(apps, schema_editor):
    Pool = apps.get_model("netbox_load_balancing", "Pool")
    Listener = apps.get_model("netbox_load_balancing", "Listener")
    BackendTuning = apps.get_model("netbox_load_balancing_acl", "LBBackendTuning")
    FrontendTuning = apps.get_model("netbox_load_balancing_acl", "LBFrontendTuning")
    BackendTuning.objects.bulk_create(
        [BackendTuning(pool=p) for p in Pool.objects.filter(tuning__isnull=True)]
    )
    FrontendTuning.objects.bulk_create(
        [FrontendTuning(listener=lst) for lst in Listener.objects.filter(tuning__isnull=True)]
    )


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_load_balancing_acl", "0012_lbfrontendtuning_client_auth_cas"),
    ]

    operations = [
        migrations.AddField(
            model_name="lbbackendtuning",
            name="timeout_server",
            field=models.PositiveIntegerField(
                default=EDGE_REQUEST_TIMEOUT_SECONDS,
                validators=[django.core.validators.MinValueValidator(EDGE_REQUEST_TIMEOUT_SECONDS)],
                help_text="Seconds to wait for a backend response (HAProxy `timeout server`). Must exceed "
                "Cloudflare's fixed origin timeout so the edge never cuts a request first.",
            ),
        ),
        migrations.AddField(
            model_name="lbfrontendtuning",
            name="timeout_client",
            field=models.PositiveIntegerField(
                default=EDGE_REQUEST_TIMEOUT_SECONDS,
                validators=[django.core.validators.MinValueValidator(EDGE_REQUEST_TIMEOUT_SECONDS)],
                help_text="Seconds a client connection may stay inactive (HAProxy `timeout client`). Must "
                "exceed Cloudflare's fixed origin timeout so the edge never cuts a request first.",
            ),
        ),
        migrations.RunPython(backfill_tuning_rows, migrations.RunPython.noop),
    ]
