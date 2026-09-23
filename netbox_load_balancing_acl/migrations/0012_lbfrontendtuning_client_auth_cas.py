# SPDX-License-Identifier: AGPL-3.0-or-later
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_load_balancing_acl", "0011_lbmemberha_member_port"),
        ("netbox_pki", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="lbfrontendtuning",
            name="client_auth_cas",
            field=models.ManyToManyField(
                blank=True,
                help_text="CAs the frontend trusts for client-certificate (mTLS) auth, referenced on the "
                "device by each CA's trust_refid. Empty = the frontend's CA list stays live-managed. "
                "The verification policy is the listener's ssl_client_auth_verify custom field.",
                related_name="lb_frontend_tunings",
                to="netbox_pki.pkicertificateauthority",
            ),
        ),
    ]
