# SPDX-License-Identifier: AGPL-3.0-or-later
"""Every pool and listener carries a tuning row, so its NetBox-default edge timeouts reach the
pipeline without anyone creating the row by hand."""
from django.db.models.signals import post_save


def ensure_backend_tuning(sender, instance, created, raw=False, **kwargs):
    from .models import LBBackendTuning

    if created and not raw:
        LBBackendTuning.objects.get_or_create(pool=instance)


def ensure_frontend_tuning(sender, instance, created, raw=False, **kwargs):
    from .models import LBFrontendTuning

    if created and not raw:
        LBFrontendTuning.objects.get_or_create(listener=instance)


def register():
    from netbox_load_balancing.models import Listener, Pool

    post_save.connect(ensure_backend_tuning, sender=Pool, dispatch_uid="lb_acl_ensure_backend_tuning")
    post_save.connect(ensure_frontend_tuning, sender=Listener, dispatch_uid="lb_acl_ensure_frontend_tuning")
