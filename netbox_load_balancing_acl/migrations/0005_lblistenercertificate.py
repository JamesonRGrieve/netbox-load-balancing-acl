# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_load_balancing_acl --check --dry-run  (dev/ephemeral NetBox)
#
# Add LBListenerCertificate — first-class, ordered SNI/TLS cert bindings on a Listener, so an
# adopted frontend's cert array (pfSense ha_certificates / OPNsense ssl_certificates) renders
# position-for-position at 0-diff AND new ACME/Cloudflare cert refids can be appended natively.
# Additive; existing models unchanged.
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_load_balancing_acl", "0004_lbacl"),
        ("netbox_load_balancing", "0007_alter_lbserviceassignment_assigned_object_type_and_more"),
        ("extras", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="LBListenerCertificate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ("order", models.PositiveIntegerField(default=100)),
                ("ssl_certificate", models.CharField(max_length=64)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("listener", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="certificates", to="netbox_load_balancing.listener")),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "LB Listener Certificate",
                "verbose_name_plural": "LB Listener Certificates",
                "ordering": ["listener", "order"],
            },
        ),
        migrations.AddConstraint(
            model_name="lblistenercertificate",
            constraint=models.UniqueConstraint(fields=("listener", "order"), name="lb_listener_cert_listener_order"),
        ),
    ]
