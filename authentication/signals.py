from typing import Iterable
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from authentication.const import ROLE_NAMES

@receiver(post_migrate)
def ensure_groups(sender, **kwargs):
    # Only run when auth or authentication app migrates
    app_label = kwargs.get("app_config").label if kwargs.get("app_config") else ""
    if app_label not in {"auth", "authentication"}:
        return
    for name in ROLE_NAMES:
        Group.objects.get_or_create(name=name)