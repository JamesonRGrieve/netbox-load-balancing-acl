# SPDX-License-Identifier: AGPL-3.0-or-later
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_load_balancing", "0001_initial"),
        ("netbox_load_balancing_acl", "0006_lbmemberha"),
    ]

    operations = [
        migrations.CreateModel(
            name="LBHealthCheckTuning",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict)),
                ("monitor", models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="tuning",
                    to="netbox_load_balancing.healthmonitor",
                    help_text="The health monitor this tuning applies to.",
                )),
                ("fall", models.PositiveIntegerField(default=3, help_text="Consecutive failed checks to mark server DOWN (HAProxy `fall`).")),
                ("rise", models.PositiveIntegerField(default=2, help_text="Consecutive successful checks to mark server UP (HAProxy `rise`).")),
                ("fast_interval", models.PositiveIntegerField(null=True, blank=True, help_text="Check interval (ms) during transitional state (HAProxy `fastinter`).")),
                ("down_interval", models.PositiveIntegerField(null=True, blank=True, help_text="Check interval (ms) while server is DOWN (HAProxy `downinter`).")),
                ("http_method", models.CharField(max_length=16, blank=True, default="", help_text="HTTP method for health checks (GET, HEAD, OPTIONS).")),
            ],
            options={
                "ordering": ["monitor"],
                "verbose_name": "LB Health Check Tuning",
                "verbose_name_plural": "LB Health Check Tuning",
            },
        ),
        migrations.CreateModel(
            name="LBBackendTuning",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict)),
                ("pool", models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="tuning",
                    to="netbox_load_balancing.pool",
                    help_text="The pool (backend) this tuning applies to.",
                )),
                ("retries", models.PositiveIntegerField(default=3, help_text="Number of retries on connection failure (HAProxy `retries`).")),
                ("redispatch", models.BooleanField(default=False, help_text="Re-dispatch failed request to another server (HAProxy `option redispatch`).")),
                ("retry_on", models.CharField(max_length=255, blank=True, default="", help_text="Conditions to retry on (HAProxy `retry-on`).")),
                ("log_health_checks", models.BooleanField(default=False, help_text="Log every health-check state transition (HAProxy `option log-health-checks`).")),
                ("http_check_path", models.CharField(max_length=255, blank=True, default="/", help_text="URI path for HTTP health checks.")),
                ("http_check_method", models.CharField(max_length=16, blank=True, default="", help_text="HTTP method for backend health checks (GET, HEAD, OPTIONS).")),
                ("custom_options", models.TextField(blank=True, default="", help_text="Raw HAProxy config lines injected into the backend (pass-thru).")),
            ],
            options={
                "ordering": ["pool"],
                "verbose_name": "LB Backend Tuning",
                "verbose_name_plural": "LB Backend Tuning",
            },
        ),
        migrations.CreateModel(
            name="LBFrontendTuning",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict)),
                ("listener", models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="tuning",
                    to="netbox_load_balancing.listener",
                    help_text="The listener (frontend) this tuning applies to.",
                )),
                ("custom_options", models.TextField(blank=True, default="", help_text="Raw HAProxy config lines injected into the frontend (pass-thru).")),
            ],
            options={
                "ordering": ["listener"],
                "verbose_name": "LB Frontend Tuning",
                "verbose_name_plural": "LB Frontend Tuning",
            },
        ),
    ]
