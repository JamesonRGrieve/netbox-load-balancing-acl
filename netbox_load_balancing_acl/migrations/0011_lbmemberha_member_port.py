# SPDX-License-Identifier: AGPL-3.0-or-later
# Add an optional per-server backend port override to LBMemberHA. The netbox-load-balancing
# base plugin has a single Pool.member_port for every member; a standby that forwards to a
# different port than the pool's primaries needs its own — e.g. the CLOUDFLARE_LB.md §2133
# omg-edge -> house Receiver mTLS failover, where the primary WordPress members are :80 but
# the house-edge backup must reach the mTLS Receiver on :443. Existing rows get member_port=NULL
# (fall back to the pool's member_port), so they are unaffected.
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_load_balancing_acl", "0010_lbmemberha_backend_mtls"),
    ]

    operations = [
        migrations.AddField(
            model_name="lbmemberha",
            name="member_port",
            field=models.PositiveIntegerField(
                null=True,
                blank=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(65535),
                ],
                help_text=(
                    "Override the backend port for THIS server only (HAProxy `<ip>:<port>`). The "
                    "netbox-load-balancing base plugin has a single Pool.member_port for every "
                    "member; a standby that forwards to a different port than the pool's primaries "
                    "sets it here — e.g. the §2133 omg-edge→house Receiver mTLS failover, where the "
                    "primary WordPress members are :80 but the house-edge backup must reach the mTLS "
                    "Receiver on :443. Null = use the pool's member_port (unchanged behaviour)."
                ),
            ),
        ),
    ]
