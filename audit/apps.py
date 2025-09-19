from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audit'
    label = 'hv_audit'

    def ready(self) -> None:
        # Import signal receivers
        from . import receivers  # noqa: F401