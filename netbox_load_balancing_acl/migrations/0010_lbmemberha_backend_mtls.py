# SPDX-License-Identifier: AGPL-3.0-or-later
# Add per-server backend mTLS to LBMemberHA: the client certificate this HAProxy
# server presents to an authenticated origin (sslClientCertificate refid) + whether
# to verify the origin's server cert (sslVerify). Restores the CLOUDFLARE_LB.md
# §2133 omg-edge -> house Receiver Authenticated-Origin-Pull failover forward that
# the pfSense->OPNsense migration dropped. Existing rows get ssl_client_cert=""
# (no cert emitted) / ssl_verify=True, so they are unaffected.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_load_balancing_acl", "0009_lbroutingrule_set_path"),
    ]

    operations = [
        migrations.AddField(
            model_name="lbmemberha",
            name="ssl_client_cert",
            field=models.CharField(
                blank=True,
                default="",
                max_length=200,
                help_text=(
                    "OPNsense trust-store refid of the client certificate this server presents "
                    "for mTLS to an authenticated origin (HAProxy `crt` — e.g. the omg-edge→house "
                    "Receiver Authenticated-Origin-Pull failover forward, CLOUDFLARE_LB.md §2133). "
                    "Blank = present no client cert (unchanged behaviour)."
                ),
            ),
        ),
        migrations.AddField(
            model_name="lbmemberha",
            name="ssl_verify",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Verify the backend server's TLS certificate (HAProxy `verify required` vs "
                    "`verify none`). Only consulted when this server presents a client cert / is ssl; "
                    "the device emits it alongside sslClientCertificate."
                ),
            ),
        ),
    ]
